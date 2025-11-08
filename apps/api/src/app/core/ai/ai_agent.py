import json
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
    AnalyzedData,
    MessagesState,
    EvaluatorOutput,
    Syllabus,
    CourseRevision,
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
    oa_model = model.with_structured_output(AnalyzedData)
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
            "analyzed_data": response,
            "llm_calls": state.get("llm_calls", 0) + 1,
            "evaluator": None,
        },
    )


def evaluator_oa(state: MessagesState):
    print("evaluator_oa")
    model_eval = model.with_structured_output(EvaluatorOutput)
    analyzed_data = state.get("analyzed_data")
    if not analyzed_data:
        return Command(
            goto="objective_architect",
            update={"evaluator": None},
        )

    prompt = [
        SystemMessage(
            content=prompt_manager.get_evaluator_oa_prompt(
                analyzed_data,
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

    return Command(
        goto="objective_architect" if feedback_state else "curriculum_designer",
        update={"evaluator": feedback_state},
    )


def curriculum_designer(state: MessagesState):
    print("cd")
    cd_model = model.with_structured_output(Syllabus)

    prompt = prompt_manager.get_curriculum_designer_prompt(state.get("analyzed_data"))

    response = cd_model.invoke(prompt)

    return Command(
        goto="evaluator_cd",
        update={
            "syllabus": response,
            "llm_calls": state.get("llm_calls", 0) + 1,
            "evaluator": None,
        },
    )


def evaluator_cd(state: MessagesState):
    print("evaluator_cd")

    model_eval = model.with_structured_output(EvaluatorOutput)
    syllabus = state.get("syllabus")

    if not syllabus:
        return Command(
            goto="curriculum_designer",
            update={"evaluator": None},
        )

    prompt = [
        SystemMessage(
            content=prompt_manager.get_evaluator_cd_prompt(
                syllabus,
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
            "agent": "curriculum_designer",
        }
        if response.get("retry")
        else None
    )

    return Command(
        goto="curriculum_designer" if feedback_state else "lesson_author",
        update={"evaluator": feedback_state},
    )


def lesson_author(state: MessagesState):
    print("lesson_author")
    la_model = model.with_structured_output(CourseRevision)

    prompt = prompt_manager.get_lesson_author_prompt(state.get("syllabus"))

    response = la_model.invoke(prompt)

    print(json.dumps(response, indent=4))

    return Command(
        goto="evaluator_la",
        update={"course": response, "llm_calls": state.get("llm_calls", 0) + 1},
    )


def evaluator_la(state: MessagesState):
    print("evaluator_la")

    model_eval = model.with_structured_output(EvaluatorOutput)
    course = state.get("course")

    if not course:
        return Command(
            goto="lesson_author",
            update={"evaluator": None},
        )

    prompt = [
        SystemMessage(
            content=prompt_manager.get_evaluator_la_prompt(
                course.get("course"),
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
            "agent": "curriculum_designer",
        }
        if response.get("retry")
        else None
    )

    return Command(
        goto="lesson_author" if feedback_state else "lesson_author_hitl",
        update={"evaluator": feedback_state},
    )


def lesson_author_hitl(state: MessagesState):
    hitl = interrupt("DO_YOU_WANT_TO_PROCEED")

    print("Here is the schema:", json.dumps(state.get("course").get("course")))

    return Command(
        goto=END if hitl else "lesson_author",
    )


builder.add_node("data_curator", data_curator)
builder.add_node("repeat_curator", repeat_curator)
builder.add_node("objective_architect", objective_architect)
builder.add_node("evaluator_oa", evaluator_oa)
builder.add_node("curriculum_designer", curriculum_designer)
builder.add_node("evaluator_cd", evaluator_cd)
builder.add_node("lesson_author_hitl", lesson_author_hitl)
builder.add_node("evaluator_la", evaluator_la)
builder.add_node("lesson_author", lesson_author)


builder.add_edge(START, "data_curator")
builder.add_edge("repeat_curator", "data_curator")
# builder.add_edge("implementation_engineer", END)

with PostgresSaver.from_conn_string(
    os.getenv("LANGGRAPH_DATABASE_URL")
) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test123"}}

    while True:
        msg = input("User: ")
        result = graph.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
        print(f"AI: {result.get('messages')[-1].content}")

        while type := result.get("__interrupt__"):
            if type == "DO_YOU_WANT_TO_PROCEED":
                msg = input("User (Y/N) - Do you want to proceed: ")
                msg = True if msg == "Y" else False
            else:
                msg = input("User: ")

            result = graph.invoke(Command(resume=msg), config=config)
            print(f"AI: {result.get('messages')[-1].content}")
