import operator
from typing import Annotated, List, Optional, Literal, TypedDict, Any

from langchain_core.messages import AnyMessage
from pydantic import BaseModel


class AuthData(BaseModel):
    email: str
    password: str


class DataCuratorOutput(TypedDict):
    message: Annotated[str, "Agent output message"]
    gather_more_info: Annotated[bool, "True if you need more info, otherwise false"]
    create_course: Annotated[
        bool,
        "True if user intent is to create a course, false if user just wants to talk",
    ]


class Objective(TypedDict):
    name: str
    description: str
    status: Literal["completed", "not_completed"]
    bloom_tag: Literal[1, 2, 3, 4, 5, 6]
    smart: bool


class Constraint(TypedDict):
    type: str
    description: str
    value: str


class AnalyzedData(TypedDict):
    topic: str
    summary: Optional[str]
    tags: Optional[List[str]]
    prerequisites: Optional[List[str]]
    learning_outcomes: Optional[List[str]]
    difficulty: Optional[Literal["beginner", "intermediate", "advanced"]]
    objectives: Optional[List[Objective]]
    constraints: Optional[List[Constraint]]


class EvaluatorOutput(TypedDict):
    feedback: Annotated[str, "Feedback of what to improve"]
    retry: Annotated[
        bool,
        "Set to True if data is invalid, incomplete, or needs to be redone or something is missing",
    ]


class EvaluatorData(TypedDict):
    agent: Literal[
        "data_curator",
        "objective_architect",
        "curriculum_designer",
        "lesson_author",
        "implementation_engineer",
    ]

    feedback: str
    retry: bool


class LessonTemplate(TypedDict):
    type: Annotated[
        Literal[
            "text",
            "ai_mentor",
        ],
        "Types of questions you will be able to have",
    ]
    overview: Annotated[str, "Rough overview of the lesson"]
    bloom: Annotated[Literal[1, 2, 3, 4, 5, 6], "Rough bloom estimation of this lesson"]


class ChapterTemplate(TypedDict):
    overview: Annotated[str, "Rough overview of what this chapter will contain"]
    bloom: Annotated[
        Literal[1, 2, 3, 4, 5, 6], "Rough bloom estimation of this chapter"
    ]
    difficulty: Annotated[
        Literal["easy", "medium", "tough"], "Estimated difficulty of the chapter"
    ]
    lessons: Annotated[List[LessonTemplate], "Rough overview of lessons"]


class Syllabus(TypedDict):
    chapters: Annotated[List[ChapterTemplate], "Outline shape of the chapters"]
    reason: Annotated[
        str,
        "Observations on balance, alignment with objectives, and constraint satisfaction, incorporating presenter feedback if available",
    ]
    feedback: Annotated[
        str,
        "2-3 sentences explaining the chapter structure, Bloom progression, and lesson count rationale",
    ]


class Lesson(BaseModel):
    type: Annotated[
        Literal["ai_mentor", "text"],
        "type of lesson, based on the type of the lesson other dependencies are filled",
    ]
    title: Annotated[str, "Title of the lesson"]
    content: Annotated[
        str,
        "Content of the text lesson",
    ]
    display_order: Annotated[
        int, "index of the display of the lesson in the chapter (unique)"
    ]

    ai_mentor_instructions: Annotated[
        str, "Instructions for the AI Mentor. Only include if lesson type is AI mentor"
    ]

    ai_completion_conditions: Annotated[
        str,
        "Completion conditions for the lesson (bulletpoints for conditions and also add threshold for approval by ai judge). Should be empty if lesson is not ai mentor",
    ]
    mentor_type: Annotated[
        Literal["roleplay", "mentor", "teacher"],
        "Roleplay plays out a scenario, mentor is a mix between teacher and roleplay, teacher aims to teach. It's empty if lesson type is not ai mentor",
    ]


class Chapter(BaseModel):
    lesson_count: Annotated[int, "amount of lessons in chapter"]
    display_order: Annotated[int, "index of display in course (unique)"]
    title: Annotated[str, "title of chapter"]

    lessons: List[Lesson]


class ChapterOutput(BaseModel):
    lesson_count: Annotated[int, "amount of lessons in chapter"]
    title: Annotated[str, "title of chapter"]


class CourseOutput(BaseModel):
    title: Annotated[str, "Title of the course"]
    description: Annotated[str, "Description of the course"]
    chapter_count: Annotated[int, "Count of chapters in course"]


class Course(BaseModel):
    title: Annotated[str, "Title of the course"]
    description: Annotated[str, "Description of the course"]
    chapter_count: Annotated[int, "Count of chapters in course"]
    chapters: Annotated[List[Chapter], "Chapters for the course"]


class CourseRevision(TypedDict):
    course: Course


class MessagesState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    analyzed_data: Optional[AnalyzedData]
    evaluator: Optional[EvaluatorData]
    syllabus: Optional[Syllabus]
    course: Optional[Course]
    llm_calls: Optional[int]


class Message(BaseModel):
    message: str
