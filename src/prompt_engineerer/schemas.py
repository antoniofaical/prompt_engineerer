from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Question(ResponseModel):
    text: str
    reason: str
    blocking: bool


class Analysis(ResponseModel):
    objective: str
    requirements: list[str]
    missing_information: list[str]
    questions: list[Question]
    blocking_conflicts: list[str]


class Selection(ResponseModel):
    guideline_ids: list[str]
    rationale: str


class Draft(ResponseModel):
    markdown: str = Field(min_length=1)


class Issue(ResponseModel):
    severity: Literal["blocking", "suggestion"]
    description: str


class Review(ResponseModel):
    passed: bool
    issues: list[Issue]
