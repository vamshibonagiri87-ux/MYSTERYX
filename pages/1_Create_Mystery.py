import random, streamlit as st
from mysteryx.ui_components import shell, repo, set_session, svg_art
from mysteryx.i18n import current_language, language_name, tr
from mysteryx.models import Difficulty
from mysteryx.case_generator import generate_case, GenerationError
from mysteryx.config import ai_provider_configured

shell("Pick a mystery","Make up a mystery, or let us surprise you. Then choose how tricky it should be.")
art,description=st.columns([1,5],vertical_alignment="center")
with art: st.markdown(svg_art("icons/case-file.svg","section-art"),unsafe_allow_html=True)
with description: st.markdown(f"**{tr('Every great case starts with a question. Add your idea, or pick a surprise case.')}**")
premises={
    "en":["A priceless diamond disappears from a locked mansion during a storm.","The original map vanishes from a museum archive just before its unveiling.","A rare signed score disappears from a music conservatory before the concert."],
    "te":["?????? ??????, ???? ????? ????????? ?? ????? ????????.","?????????? ?????????? ????????? ??? ?????? ???????????? ???????.","????? ???????? ????? ????? ?????? ????? ??????? ???? ??????? ????????."],
    "hi":["तूफ़ान के दौरान बंद हवेली से एक अनमोल हीरा गायब हो जाता है।","प्रदर्शनी से ठीक पहले संग्रहालय के अभिलेख से असली नक्शा गायब हो जाता है।","संगीत कार्यक्रम से पहले संगीत विद्यालय से हस्ताक्षर वाला दुर्लभ स्वर-पत्र गायब हो जाता है।"],
}[current_language()]
if not ai_provider_configured():
    st.warning("Mystery generation is not connected yet. Add an OpenRouter API key to `.streamlit/secrets.toml` or set `OPENROUTER_API_KEY` in your environment, then restart Streamlit.")
with st.form("generate"):
    premise=st.text_area(tr("What goes missing or goes wrong?"),placeholder=tr("A shiny diamond disappears from a locked mansion..."),max_chars=500,height=100,help=tr("Write one or two sentences. Keep it make-believe!"))
    difficulty=st.selectbox(tr("How tricky should it be?"),list(Difficulty),index=0,format_func=lambda x:tr({Difficulty.EASY:"Easy · a good first mystery",Difficulty.MEDIUM:"Medium · a few more twists",Difficulty.HARD:"Hard · ready for a challenge"}[x]))
    a,b=st.columns(2)
    generate=a.form_submit_button(tr("Make my mystery"),type="primary",use_container_width=True)
    random_case=b.form_submit_button(tr("Random Mystery"),use_container_width=True)
if generate or random_case:
    text=random.choice(premises) if random_case else premise.strip()
    if not text:
        st.error(tr("Enter a mystery premise or choose Random Mystery."))
    elif len(text)<20 or len(text)>500:
        st.error(tr("Your premise must be between 20 and 500 characters."))
    else:
        with st.spinner(tr("Building your case...")):
            try:
                selected_language=language_name(current_language())
                case=generate_case(text,Difficulty(difficulty),language=selected_language)
                sid=repo().save_case(case,language=selected_language); set_session(sid)
                st.success(tr("Your case is ready.")); st.switch_page("pages/2_Investigation_Room.py")
            except GenerationError as exc:
                st.error(tr(str(exc)))
                if "rate limited or out of credits" in str(exc):
                    st.link_button("Check OpenRouter credits and limits", "https://openrouter.ai/settings/keys")
                elif "usage quota was reached" in str(exc):
                    st.link_button(tr("Check Gemini quota and billing"),"https://aistudio.google.com/rate-limit")
            except ValueError as exc: st.error(str(exc))
            except Exception:
                st.error(tr("We couldn't generate your mystery. Please try again."))
if st.button(tr("Back home")):
    st.switch_page("pages/0_MYSTERYX.py")
