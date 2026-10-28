from enum import Enum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3000)]

class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

DIFFICULTY_COUNTS = {
    Difficulty.EASY: (3, 5, 2, 100),
    Difficulty.MEDIUM: (4, 7, 3, 150),
    Difficulty.HARD: (5, 9, 3, 200),
}

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Suspect(StrictModel):
    id: ShortText
    name: ShortText
    profile: LongText
    motive: LongText
    public_alibi: LongText
    private_truth: LongText

class Clue(StrictModel):
    id: ShortText
    title: ShortText
    description: LongText
    details: LongText
    implicates_suspect_ids: list[ShortText]
    solution_relevance: LongText

class Hint(StrictModel):
    id: ShortText
    text: ShortText
    reveal_level: int = Field(ge=1, le=3)

class Solution(StrictModel):
    culprit_id: ShortText
    reasoning: LongText
    supporting_clue_ids: list[ShortText] = Field(min_length=1)
    full_explanation: LongText

class TimelineEvent(StrictModel):
    time: ShortText
    event: LongText

class GeneratedCase(StrictModel):
    case_id: str
    title: ShortText
    premise: LongText
    difficulty: Difficulty
    story: LongText
    suspects: list[Suspect]
    clues: list[Clue]
    hints: list[Hint]
    solution: Solution
    timeline: list[TimelineEvent] = Field(min_length=1)

class PublicCase(StrictModel):
    case_id: str
    title: str
    premise: str
    difficulty: Difficulty
    story: str
    suspects: list[dict]
    clues: list[dict]
    hints: list[dict]
    timeline: list[dict]
