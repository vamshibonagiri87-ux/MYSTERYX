import streamlit as st
from mysteryx.ui_components import shell, repo, session_id, svg_art
from mysteryx.i18n import tr

r=repo(); sid=session_id(r)
shell("MYSTERYX", "The Room That Thinks · Every clue tells a story. Every suspect hides a secret.",show_home=False)
st.markdown("""<section class="hero-panel"><div class="hero-kicker">{}</div><div class="hero-title">{}</div><div class="hero-copy">{}</div></section>""".format(tr("A case is waiting"),tr("Look closer. Think sharper. Solve the mystery."),tr("Step into a story of missing treasures, curious clues, and people with secrets. The answer is yours to uncover.")),unsafe_allow_html=True)
st.markdown(svg_art("mystery_manor.svg"),unsafe_allow_html=True)
start,resume,history=st.columns([1,1,1],gap="medium")
with start:
    if st.button(tr("Open a new case"),type="primary",use_container_width=True):
        st.switch_page("pages/1_Create_Mystery.py")
with resume:
    if sid and st.button(tr("Continue my case"),use_container_width=True):
        st.switch_page("pages/2_Investigation_Room.py")
with history:
    if st.button(tr("Solved Cases"),use_container_width=True):
        st.switch_page("pages/5_Solved_Cases.py")
st.markdown("### "+tr("Your investigation, in three steps"))
steps=st.columns(3,gap="medium")
for col,number,title,copy,icon in zip(steps,("01","02","03"),("Search","Question","Solve"),("Collect clues from the room.","Talk to everyone in the case.","Make your final guess."),("search.svg","question.svg","solve.svg")):
    with col,st.container(border=True):
        st.markdown(svg_art("icons/"+icon,"step-icon"),unsafe_allow_html=True)
        st.markdown(f'<div class="case-label">{number} / {tr("FIELD NOTE")}</div><h3>{tr(title)}</h3><p>{tr(copy)}</p>',unsafe_allow_html=True)
st.caption(tr("All mysteries are make-believe. Your progress is saved on this device."))
st.caption(tr("Classic detective film stills: *The Maltese Falcon* (1941) and *He Walked by Night* (1948)."))
