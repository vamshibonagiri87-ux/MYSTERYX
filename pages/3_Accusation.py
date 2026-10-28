import streamlit as st
from mysteryx.ui_components import shell,repo,session_id,svg_art
from mysteryx.game_service import submit_accusation
from mysteryx.i18n import tr

r=repo(); sid=session_id(r); game=r.get_game(sid) if sid else None
if not game: st.error(tr("No active case is available.")); st.stop()
case=game['case']; shell("Who do you think did it?",case['title'])
st.markdown(svg_art("icons/accuse.svg","section-art"),unsafe_allow_html=True)
st.write(case['premise'])
with st.expander(tr("Look at the clues in your notebook"),expanded=True):
    found=[c for c in case['clues'] if c['id'] in game['discoveries']]
    if not found: st.info(tr("Your notebook is empty. You can go back and look for clues first."))
    for c in found:
        st.markdown(f"**{c['title']}**")
        st.write(c['description'])
with st.form("accuse"):
    names={s['id']:s['name'] for s in case['suspects']}
    selected=st.radio(tr("Choose one person"),list(names),format_func=lambda x:names[x])
    why=st.text_area(tr("What clues helped you decide? (optional)"),max_chars=1000)
    confirm=st.checkbox(tr("Are you ready to submit your final accusation?"))
    submit=st.form_submit_button(tr("Lock in my guess"),type="primary")
if submit:
    if not selected: st.error(tr("Select a suspect before submitting."))
    elif not confirm: st.warning(tr("Please check the box when you're ready to lock in your final guess."))
    else:
        try:
            submit_accusation(r,sid,selected,why); st.switch_page("pages/4_Results.py")
        except Exception: st.error(tr("Your accusation wasn't submitted. Please try again."))
if st.button(tr("Back to the case")): st.switch_page("pages/2_Investigation_Room.py")
