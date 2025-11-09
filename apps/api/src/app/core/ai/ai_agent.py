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
    Course,
    Chapter,
    CourseOutput,
    Lesson,
)
from src.app.core.ai.prompt_manager import PromptManager

load_dotenv()

model = init_chat_model("openai:gpt-4.1-mini")
prompt_manager = PromptManager()


def data_curator(
    state: MessagesState,
) -> Command[Literal["repeat_curator", "objective_architect", END]]:
    print("data_curator")
    dc_model = model.with_structured_output(DataCuratorOutput)
    prompt_messages = [
        SystemMessage(content=prompt_manager.get_curator_prompt())
    ] + state.get("messages")

    result = dc_model.invoke(prompt_messages)
    goto = "repeat_curator" if result.get("gather_more_info") else "objective_architect"

    goto = goto if result.get("create_course") else END

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
    course_model = model.with_structured_output(CourseOutput)
    chapter_model = model.with_structured_output(Chapter)
    lesson_model = model.with_structured_output(Lesson)

    syllabus = state.get("syllabus")

    prompt = [SystemMessage(content=prompt_manager.get_course_output_prompt(syllabus))]
    course_output_raw = course_model.invoke(prompt)
    course_output = (
        CourseOutput(**course_output_raw)
        if isinstance(course_output_raw, dict)
        else course_output_raw
    )

    chapters = []
    generated_chapters_summary = ""

    for i in range(course_output.chapter_count):
        chapter_prompt = [
            SystemMessage(
                content=prompt_manager.get_chapter_output_prompt(
                    syllabus, course_output.model_dump(), generated_chapters_summary
                )
            )
        ]
        chapter_raw = chapter_model.invoke(chapter_prompt)
        chapter = (
            Chapter(**chapter_raw) if isinstance(chapter_raw, dict) else chapter_raw
        )

        lessons = []
        generated_lessons_summary = ""

        for j in range(chapter.lesson_count):
            lesson_prompt = [
                SystemMessage(
                    content=prompt_manager.get_lesson_output_prompt(
                        syllabus, chapter.model_dump(), generated_lessons_summary
                    )
                )
            ]
            lesson_raw = lesson_model.invoke(lesson_prompt)
            lesson = (
                Lesson(**lesson_raw) if isinstance(lesson_raw, dict) else lesson_raw
            )
            lessons.append(lesson)

            generated_lessons_summary += (
                f"\n- Lesson {j+1}: {lesson.title} ({lesson.type})"
            )

        chapter.lessons = lessons
        chapters.append(chapter)

        generated_chapters_summary += (
            f"\n- Ch {i+1}: {chapter.title} ({len(lessons)} lessons)"
        )

    course = Course(
        title=course_output.title,
        description=course_output.description,
        chapter_count=course_output.chapter_count,
        chapters=chapters,
    )

    return Command(
        goto=END,
        update={
            "course": course.model_dump(),
            "llm_calls": state.get("llm_calls", 0) + 1,
        },
    )


# def evaluator_la(state: MessagesState):
#     print("evaluator_la")
#
#     model_eval = model.with_structured_output(EvaluatorOutput)
#     course = state.get("course")
#
#     if not course:
#         return Command(
#             goto="lesson_author",
#             update={"evaluator": None},
#         )
#
#     prompt = [
#         SystemMessage(
#             content=prompt_manager.get_evaluator_la_prompt(
#                 course.get("course"),
#                 "\n".join(
#                     [
#                         msg.content
#                         for msg in state.get("messages")
#                         if hasattr(msg, "content")
#                     ]
#                 ),
#             )
#         )
#     ]
#
#     response = model_eval.invoke(prompt)
#
#     feedback_state = (
#         {
#             "retry": response.get("retry"),
#             "feedback": response.get("feedback"),
#             "agent": "curriculum_designer",
#         }
#         if response.get("retry")
#         else None
#     )
#
#     return Command(
#         goto="lesson_author" if feedback_state else END,
#         update={"evaluator": feedback_state},
#     )


# with PostgresSaver.from_conn_string(
#     os.getenv("LANGGRAPH_DATABASE_URL")
# ) as checkpointer:
#     # graph = builder.compile(checkpointer=checkpointer)
#     config = {"configurable": {"thread_id": "testdasdaasdasdasdasdsdsdfsdf123"}}
#
#     while True:
#         msg = input("User: ")
#         result = graph.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
#         print(f"AI: {result.get('messages')[-1].content}")
#
#         while type := result.get("__interrupt__"):
#             if type == "DO_YOU_WANT_TO_PROCEED":
#                 msg = input("User (Y/N) - Do you want to proceed: ")
#                 msg = True if msg == "Y" else False
#             else:
#                 msg = input("User: ")
#
#             result = graph.invoke(Command(resume=msg), config=config)
#             print(f"AI: {result.get('messages')[-1].content}")
