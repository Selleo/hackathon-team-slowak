import operator
from typing import Annotated, List, Optional, Literal, TypedDict

from langchain_core.messages import AnyMessage


class DataCuratorOutput(TypedDict):
    message: Annotated[str, "Agent output message"]
    gather_more_info: Annotated[bool, "True if you need more info, otherwise false"]


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


class ObjectiveArchitectOutput(TypedDict):
    analyzed_data: AnalyzedData


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


class MessagesState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    analyzed_objectives: Optional[ObjectiveArchitectOutput]
    evaluator: Optional[EvaluatorData]
    llm_calls: Optional[int]
