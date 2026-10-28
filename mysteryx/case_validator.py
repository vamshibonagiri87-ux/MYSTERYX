import json
import re
from pydantic import ValidationError
from .models import DIFFICULTY_COUNTS, GeneratedCase, Difficulty

class CaseValidationError(ValueError):
    pass

def parse_case(raw: str, difficulty: Difficulty) -> GeneratedCase:
    if len(raw) > 50000 or raw.lstrip().startswith("```"):
        raise CaseValidationError("Model output must be bounded raw JSON.")
    try:
        case = GeneratedCase.model_validate_json(raw)
    except (ValidationError, ValueError) as exc:
        if isinstance(exc, ValidationError):
            problems=[".".join(str(part) for part in item["loc"])+" ("+item["type"]+")" for item in exc.errors(include_input=False)]
            detail="; ".join(problems[:8])
            raise CaseValidationError("Schema fields need correction: "+detail) from exc
        raise CaseValidationError("Generated case was not valid JSON.") from exc
    if case.difficulty != difficulty:
        raise CaseValidationError("Generated difficulty did not match the request.")
    ns, nc, nh, _ = DIFFICULTY_COUNTS[difficulty]
    if (len(case.suspects), len(case.clues), len(case.hints)) != (ns, nc, nh):
        raise CaseValidationError("Generated case has incorrect difficulty counts.")
    for values, label in ((case.suspects, "suspect"), (case.clues, "clue"), (case.hints, "hint")):
        ids = [x.id for x in values]
        if len(ids) != len(set(ids)):
            raise CaseValidationError(f"Duplicate {label} IDs.")
    suspect_ids = {s.id for s in case.suspects}
    clue_ids = {c.id for c in case.clues}
    if case.solution.culprit_id not in suspect_ids:
        raise CaseValidationError("Culprit reference is invalid.")
    if not set(case.solution.supporting_clue_ids) <= clue_ids:
        raise CaseValidationError("Solution references unknown clues.")
    if not set(case.solution.supporting_clue_ids):
        raise CaseValidationError("Solution requires supporting clues.")
    if any(not set(c.implicates_suspect_ids) <= suspect_ids for c in case.clues):
        raise CaseValidationError("Clue references unknown suspects.")
    culprit_name = next(s.name for s in case.suspects if s.id == case.solution.culprit_id)
    mentions_culprit = lambda text: bool(re.search(r"\b" + re.escape(culprit_name) + r"\b", text, re.I))
    if any(mentions_culprit(h.text) for h in case.hints):
        raise CaseValidationError("Hints must not name the culprit.")
    clue_by_id = {c.id: c for c in case.clues}
    if not any(case.solution.culprit_id in clue_by_id[cid].implicates_suspect_ids for cid in case.solution.supporting_clue_ids):
        raise CaseValidationError("At least one supporting clue must link to the culprit.")
    if any(mentions_culprit(text) for c in case.clues for text in (c.title, c.description, c.details)):
        raise CaseValidationError("Player-facing evidence must not name the culprit directly.")
    if sorted(h.reveal_level for h in case.hints) != list(range(1, nh + 1)):
        raise CaseValidationError("Hints must have one sequential reveal level each.")
    return case

def public_case(case: GeneratedCase, discovered_ids=()) -> dict:
    discovered = set(discovered_ids)
    return {
        "case_id": case.case_id, "title": case.title, "premise": case.premise,
        "difficulty": case.difficulty.value, "story": case.story,
        "suspects": [s.model_dump(include={"id", "name", "profile", "motive", "public_alibi"}) for s in case.suspects],
        "clues": [c.model_dump(include={"id", "title", "description", "details"}) for c in case.clues if c.id in discovered],
        "hints": [], "timeline": [],
    }
