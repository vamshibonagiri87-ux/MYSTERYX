from .models import DIFFICULTY_COUNTS, Difficulty

def score_case(difficulty: Difficulty, correct: bool, discovered_count: int, hint_count: int) -> dict:
    base = DIFFICULTY_COUNTS[difficulty][3] if correct else 0
    clue_points = 5 * max(0, discovered_count)
    penalties = 10 * max(0, hint_count)
    return {"base_points": base, "clue_points": clue_points,
            "hint_penalties": penalties, "final_score": max(0, base + clue_points - penalties)}
