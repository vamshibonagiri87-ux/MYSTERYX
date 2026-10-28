import streamlit as st
import sqlite3
import base64
from functools import lru_cache
from pathlib import Path
from .repository import Repository
from .i18n import LANGUAGES, tr

ASSET_DIR=Path(__file__).resolve().parent.parent/"assets"

def svg_art(filename, class_name="scene-art"):
    """Render a trusted, local SVG asset inline so it works without external hosting."""
    markup=(ASSET_DIR/filename).read_text(encoding="utf-8")
    return f'<div class="{class_name}">{markup}</div>'

@lru_cache(maxsize=1)
def _film_backdrops():
    names=("maltese_falcon_1941.jpg","he_walked_by_night_1948.jpg")
    return [base64.b64encode((ASSET_DIR/"movie_stills"/name).read_bytes()).decode("ascii") for name in names]

@lru_cache(maxsize=1)
def _mystery_theme():
    return (ASSET_DIR/"mystery_theme.wav").read_bytes()

def repo():
    try:
        return Repository()
    except sqlite3.Error:
        st.error("Saved investigation storage is unavailable. Your existing case data has not been intentionally changed; check the database path and try again.")
        st.stop()

def session_id(repository):
    sid=st.query_params.get("sid") or st.session_state.get("sid") or repository.active_session()
    if sid: st.session_state.sid=sid
    return sid

def set_session(sid):
    st.session_state.sid=sid
    st.query_params["sid"]=sid

def shell(title, subtitle=None, show_home=True):
    st.sidebar.selectbox(
        tr("Language / భాష / भाषा"),
        list(LANGUAGES),
        format_func=lambda code: LANGUAGES[code],
        key="mysteryx_language",
    )
    language_code=st.session_state.get("mysteryx_language", "en")
    if language_code == "te":
        font_stack="'Noto Sans Telugu','Nirmala UI','Gautami',sans-serif"
        font_import="@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap');"
        script_styles=".stApp{line-height:1.75}.stApp h1,.stApp h2,.stApp h3,.hero-title{letter-spacing:normal!important;line-height:1.45!important}.stApp button,.stApp input,.stApp textarea{line-height:1.6!important}"
    else:
        font_stack="'Noto Sans','Nirmala UI','Noto Sans Devanagari',sans-serif"
        font_import=""
        script_styles=""
    title=tr(title)
    subtitle=tr(subtitle) if subtitle else subtitle
    music_enabled=st.sidebar.toggle(tr("Mystery theme music"),value=True,key="mysteryx_theme_music")
    if music_enabled:
        st.sidebar.audio(_mystery_theme(),format="audio/wav",loop=True,autoplay=True,alt="Soft, original MYSTERYX mystery theme music")
    maltese,walked_by_night=_film_backdrops()
    styles="""<style>
    FONT_IMPORT
    .stApp,.stApp :is(h1,h2,h3,p,label,input,textarea,[data-testid='stMarkdownContainer']){font-family:FONT_STACK!important;font-feature-settings:'kern' 1;text-rendering:optimizeLegibility}
    .stApp [data-testid='stIconMaterial'],.stApp .material-symbols-rounded,.stApp .material-symbols-outlined{font-family:'Material Symbols Rounded'!important;font-feature-settings:'liga'!important;font-style:normal;font-weight:normal;line-height:1;white-space:nowrap}
    SCRIPT_STYLES
    .stApp{background-color:#0b0e14;background-image:linear-gradient(90deg,rgba(7,10,16,.78),rgba(7,10,16,.70)),url(data:image/jpeg;base64,MALTESE_DATA),url(data:image/jpeg;base64,WALKED_DATA),radial-gradient(ellipse 62% 35% at 82% 0%,rgba(154,42,52,.20),transparent 72%),linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);background-size:auto,58vw 100vh,42vw 100vh,auto,54px 54px,54px 54px;background-position:center,left top,right top,center,0 0,0 0;background-repeat:no-repeat,no-repeat,no-repeat,no-repeat,repeat,repeat;background-attachment:fixed}
    .block-container{max-width:1160px;padding-top:1.5rem;padding-bottom:3rem}
    h1,h2,h3{color:#f4f0e9;letter-spacing:-.025em}
    h1{font-family:Georgia,'Times New Roman',serif;font-size:clamp(2.2rem,5vw,3.7rem)!important}
    h2,h3{font-family:Georgia,'Times New Roman',serif}
    .eyebrow{color:#e27777;text-transform:uppercase;letter-spacing:.2em;font-size:.72rem;font-weight:750}
    .stCaption,.stMarkdown p{color:#c2c0bd}
    .stButton>button{min-height:2.85rem;border-radius:10px;border:1px solid #4b3035;font-weight:700;transition:transform .15s ease,border-color .15s ease}
    .stButton>button:hover{border-color:#e27777;transform:translateY(-1px)}
    .stButton>button:focus-visible{outline:3px solid #f1b0a7;outline-offset:2px}
    .stProgress>div>div>div>div{background-color:#d45357}
    [data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px;border-color:rgba(202,164,151,.22)!important;background:linear-gradient(145deg,rgba(28,31,39,.96),rgba(17,20,27,.96))!important}
    [data-testid="stTabs"] button{font-weight:650}
    .hero-panel{position:relative;overflow:hidden;padding:clamp(1.4rem,4vw,3rem);margin:.75rem 0 1.4rem;border:1px solid rgba(226,119,119,.35);border-left:4px solid #c84e54;border-radius:18px;background:radial-gradient(ellipse at 85% 15%,rgba(167,44,53,.3),transparent 42%),linear-gradient(120deg,rgba(25,29,37,.98),rgba(13,16,23,.96));box-shadow:0 22px 70px rgba(0,0,0,.28)}
    .hero-panel:before{content:'';position:absolute;right:-7rem;top:-11rem;width:25rem;height:25rem;border:1px solid rgba(230,128,119,.18);border-radius:50%;box-shadow:0 0 0 2rem rgba(230,128,119,.025),0 0 0 5rem rgba(230,128,119,.018)}
    .hero-kicker{position:relative;color:#e58b83;font-size:.72rem;font-weight:750;letter-spacing:.2em;text-transform:uppercase}
    .hero-title{position:relative;max-width:720px;margin:.6rem 0;color:#f7f0e7;font-family:Georgia,'Times New Roman',serif;font-size:clamp(1.8rem,4.3vw,3.2rem);line-height:1.12}
    .hero-copy{position:relative;max-width:580px;color:#cbc8c2;font-size:1.06rem;line-height:1.65}
    .case-label{color:#e58b83;font-size:.7rem;text-transform:uppercase;letter-spacing:.15em;font-weight:750}
    .scene-art{overflow:hidden;border:1px solid rgba(211,154,126,.28);border-radius:18px;background:#131923;box-shadow:0 22px 70px rgba(0,0,0,.3)}
    .scene-art svg{display:block;width:100%;height:auto}
    .step-icon{width:64px;height:64px;margin-bottom:.75rem;padding:8px;border:1px solid rgba(211,154,126,.24);border-radius:14px;background:rgba(212,83,87,.07)}
    .step-icon svg{display:block;width:100%;height:100%}
    .section-art{width:84px;height:72px;margin:.25rem 0 .8rem;padding:6px;border:1px solid rgba(211,154,126,.24);border-radius:14px;background:radial-gradient(circle at 50% 45%,rgba(212,83,87,.13),rgba(23,27,35,.65) 72%)}
    .section-art svg{display:block;width:100%;height:100%}
    @media(max-width:700px){.block-container{padding:1rem .85rem 2rem}.stButton>button{min-height:3rem}.hero-panel:before{right:-16rem}}
    </style>"""
    styles=styles.replace("MALTESE_DATA",maltese).replace("WALKED_DATA",walked_by_night)
    styles=styles.replace("FONT_IMPORT",font_import).replace("FONT_STACK",font_stack).replace("SCRIPT_STYLES",script_styles)
    st.markdown(styles,unsafe_allow_html=True)
    if show_home:
        brand,home=st.columns([5,1])
        with brand: st.markdown(f'<div class="eyebrow">{tr("MYSTERYX · YOUR MYSTERY CLUB")}</div>',unsafe_allow_html=True)
        with home: st.page_link("pages/0_MYSTERYX.py",label="MYSTERYX")
    else:
        st.markdown(f'<div class="eyebrow">{tr("MYSTERYX · YOUR MYSTERY CLUB")}</div>',unsafe_allow_html=True)
    st.title(title)
    if subtitle: st.caption(subtitle)

def nav_button(label, page, key):
    if st.button(label,key=key,use_container_width=True): st.switch_page(page)
