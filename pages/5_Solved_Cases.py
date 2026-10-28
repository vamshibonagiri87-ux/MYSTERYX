from datetime import datetime
import streamlit as st

from mysteryx.i18n import tr
from mysteryx.ui_components import repo, shell
from mysteryx.ai_service import AIUnavailable
from mysteryx.i18n import current_language, language_name
from mysteryx.translation_service import localized_solved_record

r=repo()
shell("Solved Cases","Cases you finish are saved here with their scores and explanations.")
records=r.list_solved_cases()

if not records:
    st.info(tr("No completed cases yet. Finish an investigation and it will be saved here."))
    if st.button(tr("Open a new case"),type="primary"):
        st.switch_page("pages/1_Create_Mystery.py")
else:
    st.caption(tr("Completed cases: {count}",count=len(records)))
    for record in records:
        case=record["case"]
        result=record["result"]
        target_language=language_name(current_language())
        try:
            display=localized_solved_record(r,record,target_language)
        except AIUnavailable as exc:
            if "rate limited or out of credits" in str(exc):
                st.error(tr(str(exc)))
                st.link_button("Check OpenRouter credits and limits", "https://openrouter.ai/settings/keys")
            elif "usage quota was reached" in str(exc):
                st.error(tr(str(exc)))
                st.link_button(tr("Check Gemini quota and billing"),"https://aistudio.google.com/rate-limit")
            else:
                st.error(tr("Could not translate this saved case right now. Try again later."))
            break
        except Exception:
            st.error(tr("Could not translate this saved case right now. Try again later."))
            break
        with st.container(border=True):
            st.markdown(f"### {display['title']}")
            submitted=datetime.fromisoformat(result["submitted_at"]).astimezone().strftime("%d-%m-%Y")
            source_language_label={"English":"English","తెలుగు":"Telugu","हिन्दी":"Hindi"}.get(case.get("language","English"),"English")
            st.caption(f"{tr('Completed on')}: {submitted} · {tr(case['difficulty'])} · {tr(source_language_label)}")
            if result["is_correct"]:
                st.success(tr("Great detective work! You found the right person."))
            else:
                st.info(tr("This investigation is complete. Review the solution and clues below."))
            st.markdown(f"**{tr('Your guess:')}** {display['chosen_suspect_name']} · **{tr('The culprit:')}** {display['culprit_name']}")
            st.metric(tr("Final score"),result["final_score"])
            st.markdown(f"**{tr('How the clues fit')}:** {display['full_explanation']}")
            with st.expander(tr("Important clues:")):
                for clue in display["clues"]:
                    st.markdown(f"- **{clue['id']} · {clue['title']}**: {clue['description']}")
