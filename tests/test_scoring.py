from mysteryx.scoring import score_case
from mysteryx.models import Difficulty

def test_scoring_examples():
    assert score_case(Difficulty.MEDIUM,True,5,1)["final_score"]==165
    assert score_case(Difficulty.EASY,False,3,2)["final_score"]==0
    assert score_case(Difficulty.HARD,True,9,3)["final_score"]==215

def test_score_floor(): assert score_case(Difficulty.EASY,False,0,9)["final_score"]==0
