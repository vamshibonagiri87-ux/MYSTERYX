import os

def _secret(name):
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None

def gemini_api_key():
    return os.getenv("GEMINI_API_KEY") or _secret("GEMINI_API_KEY")

def openrouter_api_key():
    return os.getenv("OPENROUTER_API_KEY") or _secret("OPENROUTER_API_KEY")

def gemini_key_configured():
    return bool(gemini_api_key())

def ai_provider_configured():
    return bool(openrouter_api_key() or gemini_api_key())
