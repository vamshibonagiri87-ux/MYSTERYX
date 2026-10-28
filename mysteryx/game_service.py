import json, re
from .ai_service import get_ai_service
from .models import Difficulty
from .prompts import INTERROGATION_PROMPT
from .scoring import score_case

def discover_clue(repo,sid,cid):
    game=repo.get_game(sid)
    if not game or cid not in {c['id'] for c in game['case']['clues']}: raise ValueError("Invalid clue")
    return repo.discover(sid,cid)

def request_hint(repo,sid):
    game=repo.get_game(sid)
    if not game: raise ValueError("Invalid session")
    hints=game['case']['hints']; used=set(game['hints_used'])
    hint=next((h for h in sorted(hints,key=lambda x:x['reveal_level']) if h['id'] not in used),None)
    if not hint: return None
    if not repo.use_hint(sid,hint['id']): return None
    return {"id":hint['id'],"text":hint['text']}

def interrogate(repo,sid,suspect_id,question,ai=None):
    question=question.strip()
    if not question: raise ValueError("Enter a question for the suspect.")
    if len(question)>500: raise ValueError("Question must be 500 characters or fewer.")
    game=repo.get_game(sid)
    suspect=next((s for s in game['case']['suspects'] if s['id']==suspect_id),None)
    if not suspect: raise ValueError("That suspect is not part of this case.")
    repo.add_message(sid,suspect_id,"user",question)
    discovered=[c for c in game['case']['clues'] if c['id'] in game['discoveries']]
    allowed={"name":suspect['name'],"profile":suspect['profile'],"motive":suspect['motive'],"public_alibi":suspect['public_alibi']}
    language=game['case'].get('language','English')
    prompt=INTERROGATION_PROMPT.format(language=language)+"\nSuspect public facts: "+json.dumps(allowed,ensure_ascii=False)+"\nThis suspect's consistency constraint (never repeat as fact unless public): "+json.dumps(suspect['private_truth'],ensure_ascii=False)+"\nDiscovered evidence: "+json.dumps(discovered,ensure_ascii=False)+"\nPlayer question: "+json.dumps(question,ensure_ascii=False)
    try:
        answer=(ai or get_ai_service()).reply(prompt)
        culprit=next((s['name'] for s in game['case']['suspects'] if s['id']==game['solution']['culprit_id']),"")
        if not answer or (culprit and re.search(r"\b"+re.escape(culprit)+r"\b",answer,re.I)) or len(answer)>1000: raise ValueError("unsafe response")
    except Exception:
        answer={"Hindi":"मैं केवल वही बता सकता हूँ जो मुझे खुद पता है। क्या आपको कोई ऐसा सुराग मिला जो मुझे याद दिला सके?","Telugu":"నాకు స్వయంగా తెలిసిన విషయాలనే చెప్పగలను. నాకు గుర్తు చేయడంలో సహాయపడే ఆధారం మీకు దొరికిందా?"}.get(language,"I can only speak to what I personally know. Have you found any evidence that might help me remember?")
    repo.add_message(sid,suspect_id,"assistant",answer)
    return answer

def submit_accusation(repo,sid,suspect_id,reasoning=""):
    reasoning=reasoning.strip()
    if len(reasoning)>1000: raise ValueError("Reasoning must be 1000 characters or fewer.")
    game=repo.get_game(sid)
    if not game: raise ValueError("Invalid session")
    difficulty=Difficulty(game['case']['difficulty'])
    return repo.submit(sid,suspect_id,reasoning,lambda correct,nc,nh: score_case(difficulty,correct,nc,nh))
