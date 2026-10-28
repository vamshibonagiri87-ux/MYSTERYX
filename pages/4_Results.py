import streamlit as st
from mysteryx.ui_components import shell,repo,session_id,svg_art
from mysteryx.i18n import tr
from mysteryx.i18n import current_language, language_name
from mysteryx.ai_service import AIUnavailable
from mysteryx.translation_service import localized_solved_record

r=repo(); sid=session_id(r); game=r.get_game(sid) if sid else None
if not game or not game['result']:
    shell("Results"); st.error(tr("Your result isn't available yet. Return to the investigation and submit an accusation."))
    if st.button(tr("Retry")): st.rerun()
    st.stop()
case=game['case']; solution=game['solution']; result=dict(game['result'])
culprit=next(s for s in case['suspects'] if s['id']==solution['culprit_id'])
chosen=next(s for s in case['suspects'] if s['id']==result['selected_suspect_id'])
record={"case":case,"solution":solution,"result":result,"chosen_suspect":chosen,"culprit":culprit,"supporting_clues":[next(c for c in case['clues'] if c['id']==cid) for cid in solution['supporting_clue_ids']]}
try:
    display=localized_solved_record(r,record,language_name(current_language()))
except AIUnavailable as exc:
    if "rate limited or out of credits" in str(exc):
        st.error(tr(str(exc)))
        st.link_button("Check OpenRouter credits and limits", "https://openrouter.ai/settings/keys")
    elif "usage quota was reached" in str(exc):
        st.error(tr(str(exc)))
        st.link_button(tr("Check Gemini quota and billing"),"https://aistudio.google.com/rate-limit")
    else:
        st.error(tr("Could not translate this saved case right now. Try again later."))
    st.stop()
except Exception:
    st.error(tr("Could not translate this saved case right now. Try again later."))
    st.stop()
shell("Case Solved!" if result['is_correct'] else "The Mystery Remains Unsolved",display['title'])
st.markdown(svg_art("icons/results.svg","section-art"),unsafe_allow_html=True)
st.markdown(f"**{tr('Your guess:')}** {display['chosen_suspect_name']}  ·  **{tr('The culprit:')}** {display['culprit_name']}")
if result['is_correct']:
    st.success(tr("Great detective work! You found the right person."))
else:
    st.info(tr("Good try! Read how the clues fit together, then solve another case."))
st.metric(tr("Final score"),result['final_score'])
c1,c2,c3=st.columns(3); c1.metric(tr("Right guess bonus"),result['base_points']); c2.metric(tr("Clues found"),result['clue_points']); c3.metric(tr("Hints used"),f"−{result['hint_penalties']}")
st.subheader(tr("How the clues fit"))
st.write(display['full_explanation'])
st.write("**"+tr("Important clues:")+"**")
for clue in display['clues']:
    cid=clue['id']
    marker=tr("Collected") if cid in game['discoveries'] else tr("Missed")
    st.markdown(f"- **{cid} · {clue['title']}** ({marker}): {clue['description']}")
play,new=st.columns(2)
with play:
    if st.button(tr("Play again"),type="primary",use_container_width=True): st.switch_page("pages/1_Create_Mystery.py")
with new:
    if st.button(tr("Start a new mystery"),use_container_width=True):
        r.new_case(sid); st.query_params.clear(); st.session_state.pop("sid",None); st.switch_page("pages/1_Create_Mystery.py")
