import json, uuid
import logging
from .ai_service import get_ai_service, AIUnavailable
from .case_validator import parse_case, CaseValidationError
from .models import Difficulty, DIFFICULTY_COUNTS
from .prompts import CASE_PROMPT

class GenerationError(RuntimeError): pass
logger=logging.getLogger(__name__)

def generate_case(premise: str, difficulty: Difficulty, ai=None, attempts=3, language="English"):
    if len(premise.strip()) < 20 or len(premise.strip()) > 500:
        raise ValueError("Premise must be between 20 and 500 characters.")
    ai=ai or get_ai_service(); ns,nc,nh,_=DIFFICULTY_COUNTS[difficulty]
    prompt=CASE_PROMPT.format(difficulty=difficulty.value,counts=f"{ns} suspects, {nc} clues, {nh} hints",premise=json.dumps(premise.strip()),language=language)
    correction=""
    for attempt in range(attempts):
        try:
            case=parse_case(ai.generate_json(prompt+correction),difficulty)
            data=case.model_dump(); data["case_id"]=str(uuid.uuid4())
            return case.model_validate(data)
        except CaseValidationError as exc:
            logger.warning("Gemini case rejected by validation (attempt %s/%s): %s",attempt+1,attempts,str(exc)[:500])
            correction="\nThe previous response was rejected: "+str(exc)+". Correct those issues and return a complete corrected JSON object."
            continue
        except ValueError as exc:
            logger.warning("Gemini case could not be parsed (attempt %s/%s): %s",attempt+1,attempts,str(exc)[:300])
            correction="\nThe previous response was invalid. Return a complete raw JSON object matching the required fields exactly."
            continue
        except AIUnavailable as exc:
            if "not configured" in str(exc):
                raise GenerationError("AI API key is not configured. Set OPENROUTER_API_KEY (recommended) or GEMINI_API_KEY in the environment or Streamlit secrets.") from exc
            raise GenerationError(str(exc)) from exc
        except Exception as exc:
            raise GenerationError("We couldn't generate your mystery. Please try again.") from exc
    raise GenerationError("The generated case failed validation after several tries. No case was saved; please try again.")
