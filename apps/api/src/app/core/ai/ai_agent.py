import os
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt

from src.app.core.ai.ai_schema import (
    DataCuratorOutput,
    ObjectiveArchitectOutput,
    MessagesState,
    EvaluatorOutput,
)
from src.app.core.ai.prompt_manager import PromptManager

load_dotenv()

model = init_chat_model("openai:gpt-4.1-nano")
prompt_manager = PromptManager()

builder = StateGraph(MessagesState)


def data_curator(
    state: MessagesState,
) -> Command[Literal["repeat_curator", "objective_architect"]]:
    print("data_curator")
    dc_model = model.with_structured_output(DataCuratorOutput)
    prompt_messages = [
        SystemMessage(content=prompt_manager.get_curator_prompt())
    ] + state.get("messages")

    result = dc_model.invoke(prompt_messages)
    goto = "repeat_curator" if result.get("gather_more_info") else "objective_architect"

    return Command(
        goto=goto,
        update={
            "messages": [AIMessage(content=result.get("message"))],
            "llm_calls": state.get("llm_calls", 0) + 1,
        },
    )


def repeat_curator(state: MessagesState) -> Command[Literal["data_curator"]]:
    resumed = interrupt("PROVIDE_MORE_INFORMATION")
    print("repeat_curator")

    return Command(
        goto="data_curator",
        update={
            "messages": [HumanMessage(content=resumed)],
            "llm_calls": state.get("llm_calls", 0) + 1,
        },
    )


def objective_architect(state: MessagesState) -> Command[Literal["evaluator_oa"]]:
    oa_model = model.with_structured_output(ObjectiveArchitectOutput)
    print("objective_architect")

    messages_text = "\n".join(
        [msg.content for msg in state.get("messages", []) if hasattr(msg, "content")]
    )

    feedback = (
        state.get("evaluator").get("feedback")
        if state.get("evaluator")
        and state.get("evaluator").get("agent") == "objective_architect"
        else None
    )

    prompt = [
        SystemMessage(
            content=prompt_manager.get_objective_architect_prompt(
                messages_text, feedback
            )
        )
    ]

    response = oa_model.invoke(prompt)

    return Command(
        goto="evaluator_oa",
        update={
            "analyzed_objectives": response,
            "llm_calls": state.get("llm_calls", 0) + 1,
            "evaluator": None,
        },
    )


def evaluator_oa(state: MessagesState):
    print("evaluator_oa")
    model_eval = model.with_structured_output(EvaluatorOutput)
    analyzed_data = state.get("analyzed_objectives")
    if not analyzed_data:
        return Command(
            goto="objective_architect",
            update={"evaluator": None},
        )

    prompt = [
        SystemMessage(
            content=prompt_manager.get_evaluator_oa_prompt(
                state.get("analyzed_objectives").get("analyzed_data"),
                "\n".join(
                    [
                        msg.content
                        for msg in state.get("messages")
                        if hasattr(msg, "content")
                    ]
                ),
            )
        )
    ]

    response = model_eval.invoke(prompt)

    feedback_state = (
        {
            "retry": response.get("retry"),
            "feedback": response.get("feedback"),
            "agent": "objective_architect",
        }
        if response.get("retry")
        else None
    )

    print(state)

    return Command(
        goto="objective_architect" if feedback_state else "curriculum_designer",
        update={"evaluator": feedback_state},
    )


def curriculum_designer(state: MessagesState):
    print("curriculum designer")
    pass


builder.add_node("data_curator", data_curator)
builder.add_node("repeat_curator", repeat_curator)
builder.add_node("objective_architect", objective_architect)
builder.add_node("evaluator_oa", evaluator_oa)
builder.add_node("curriculum_designer", curriculum_designer)

builder.add_edge(START, "data_curator")
builder.add_edge("repeat_curator", "data_curator")
builder.add_edge("evaluator_oa", END)

with PostgresSaver.from_conn_string(
    os.getenv("LANGGRAPH_DATABASE_URL")
) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "123fdsfsdabca"}}

    while True:
        msg = input("User: ")
        result = graph.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
        print(f"AI: {result.get("messages")[-1].content}")

        while result.get("__interrupt__"):
            msg = input("User: ")
            result = graph.invoke(Command(resume=msg), config=config)
            print(f"AI: {result.get("messages")[-1].content}")
