import streamlit as st
from mysteryx.ui_components import shell,repo,session_id,svg_art
from mysteryx.game_service import discover_clue,request_hint,interrogate
from mysteryx.i18n import current_language, language_name, tr

r=repo(); sid=session_id(r); game=r.get_game(sid) if sid else None
if not game:
    shell("Investigation room","Your next mystery is waiting.")
    if st.button(tr("Choose a mystery"),type="primary"): st.switch_page("pages/1_Create_Mystery.py")
    st.stop()

case=game["case"]
total=len(case["clues"]); found=len(game["discoveries"]); hint_total=len(case["hints"]); hints_used=set(game["hints_used"])
shell(case["title"],tr("{difficulty} mystery",difficulty=tr(case['difficulty'])))
st.progress(found/total,text=tr("Clues found: {found} of {total}",found=found,total=total))
if language_name(current_language()) != case.get("language", "English"):
    st.caption(f"{tr('Story language')}: {case['language']}")
names={s["id"]:s["name"] for s in case["suspects"]}
selected=st.selectbox(tr("Choose someone to talk to"),list(names),format_func=lambda x:names[x],key="active_suspect")
suspect=next(s for s in case["suspects"] if s["id"]==selected)

tab_case,tab_people,tab_clues,tab_talk=st.tabs([tr("Case"),tr("People"),tr("Clues"),tr("Talk")])
with tab_case:
    st.markdown(svg_art("icons/case-file.svg","section-art"),unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(tr("What happened?"))
        st.write(case["story"])
        st.caption(case["premise"])
    st.info(tr("Your job: find clues, ask questions, and decide who did it."))

with tab_people:
    st.markdown(svg_art("icons/suspects.svg","section-art"),unsafe_allow_html=True)
    st.subheader(tr("People in the story"))
    for person in case["suspects"]:
        with st.container(border=True):
            st.markdown(f"### {person['name']}")
            st.write(person["profile"])
            st.markdown(f"**{tr('Possible reason:')}** {person['motive']}")
            with st.expander(tr("What they say")):
                st.write(person["public_alibi"])

with tab_clues:
    st.markdown(svg_art("icons/clues.svg","section-art"),unsafe_allow_html=True)
    st.subheader(tr("Look around for clues"))
    st.caption(tr("Open a clue to add it to your notebook."))
    for index,clue in enumerate(case["clues"],start=1):
        found_clue=clue["id"] in game["discoveries"]
        with st.container(border=True):
            st.markdown(f"### {clue['title'] if found_clue else tr('Clue {index}',index=index)}")
            if found_clue:
                st.write(clue["description"])
                st.caption(clue["details"])
                st.success(tr("Added to your notebook"))
            else:
                st.write(tr("Something here might help solve the mystery."))
                if st.button(tr("Look at this clue"),key="collect_"+clue["id"]):
                    discover_clue(r,sid,clue["id"]); st.rerun()

with tab_talk:
    st.markdown(svg_art("icons/question.svg","section-art"),unsafe_allow_html=True)
    st.subheader(tr("Ask {name} a question",name=suspect['name']))
    st.caption(tr("Ask about the story or something you found. Keep your question short."))
    messages=[m for m in game["messages"] if m["suspect_id"]==selected]
    for msg in messages[-12:]:
        st.chat_message("user" if msg["role"]=="user" else "assistant").write(msg["message"])
    with st.form("question"):
        question=st.text_input(tr("Your question"),max_chars=500,placeholder=tr("Where were you when it happened?"))
        ask=st.form_submit_button(tr("Ask"),type="primary")
    if ask:
        if not question.strip():
            st.error(tr("Type a question first."))
        else:
            with st.spinner(f"{suspect['name']} is thinking..."):
                try:
                    interrogate(r,sid,selected,question)
                except Exception:
                    st.error(tr("That answer didn't come through. Your clues are safe. Please try again."))
            st.rerun()

hint_col,guess_col=st.columns([1,1],gap="medium")
with hint_col:
    remaining=hint_total-len(hints_used)
    if st.button(tr("Get a hint · {remaining} left",remaining=remaining),disabled=remaining==0,use_container_width=True):
        hint=request_hint(r,sid)
        if hint: st.rerun()
    if remaining==0: st.caption(tr("You used all your hints. You can still solve the case!"))
    for hint in case["hints"]:
        if hint["id"] in hints_used:
            st.info(hint["text"])
with guess_col:
    if st.button(tr("Make my guess"),type="primary",use_container_width=True):
        st.switch_page("pages/3_Accusation.py")
