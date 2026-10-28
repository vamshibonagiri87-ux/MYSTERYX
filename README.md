# MYSTERYX

[**▶ Play MYSTERYX online**](https://mysteryx-wmclwcffl2aabmigubmpzr.streamlit.app/)

**The Room That Thinks.** A local, anonymous detective game built with Streamlit, OpenRouter (with optional direct Gemini support), Pydantic, and SQLite. Python owns case validation, saved truth, game rules, and scoring; the AI provider supplies bounded narrative text.

## Requirements

- Python 3.11 or later
- An OpenRouter API key for generating cases and suspect dialogue (recommended), or a Google Gemini API key

## Run locally

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Put your OpenRouter key in .env, or use .streamlit/secrets.toml.
streamlit run app.py
```

Alternatively, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, replace the placeholder with your key, and restart Streamlit. That local secrets file is ignored by Git. OpenRouter is selected automatically when `OPENROUTER_API_KEY` is set; otherwise the app uses `GEMINI_API_KEY`.

The application reads `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (default `google/gemini-2.5-flash`), optional `GEMINI_API_KEY` / `GEMINI_MODEL` fallback settings, and `MYSTERYX_DB_PATH` (default `mysteryx.sqlite3`). Add the chosen provider key to Streamlit Cloud Secrets or the host's secret manager. Do not commit `.env` or secrets. Sessions are anonymous and stored in the local SQLite database; this is not cross-device account storage.

## Languages

Choose English, తెలుగు (Telugu), or हिन्दी (Hindi) from the sidebar. The interface is translated offline, and newly generated mysteries and suspect conversations use the selected language. The case's story language is saved with the case; changing the interface language during an active case does not translate that already-created story.

## Deploy

### Push to GitHub

1. Create a new repository on GitHub. For the first push, leave **Add a README**, **.gitignore**, and **license** unchecked because this project already has those files.
2. In a terminal opened at the project folder, run:

   ```powershell
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

   Replace the URL with the repository URL GitHub gives you. If Git asks you to sign in, complete the browser sign-in. Never paste an API key into a Git command or GitHub source file.

Before the first push, confirm `git status` does **not** list `.env`, `.streamlit/secrets.toml`, or `mysteryx.sqlite3`. Those are local secrets/data and are excluded by `.gitignore`. Keep `.env.example` and `.streamlit/secrets.toml.example`; they contain placeholders only.

### Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
2. Choose **Create app**, select your repository and `main` branch, and enter `app.py` as the main file path.
3. In **Advanced settings**, choose Python 3.11 or newer. Add your provider key as a secret in TOML format, for example:

   ```toml
   OPENROUTER_API_KEY = "paste-your-new-key-here"
   OPENROUTER_MODEL = "google/gemini-2.5-flash"
   ```

   Paste only the new key into the host's Secrets field. Do not paste the contents of your local secrets file into GitHub.
4. Click **Deploy** and check the app logs if startup reports an error.

Community Cloud deploys from GitHub and supports entering secrets during setup. **Its local file storage is not guaranteed to persist**, so solved-case history in this app's SQLite database may disappear after a restart. Use a host with a persistent disk and set `MYSTERYX_DB_PATH` there if saved history must survive restarts. The app currently uses SQLite and does not include a remote database service.

The application has not been published to a hosting provider from this workspace. Deployment requires your GitHub repository, a configured AI secret, and (for durable solved-case history) persistent storage.

## Tests

Run `pytest`. The test suite uses deterministic generated fixtures and does not make live Gemini calls. For a provider smoke test, configure a valid key and generate a case from the Create Mystery page.

## Game rules and safety

- Exact counts per difficulty: Easy 3 suspects / 5 clues / 2 hints; Medium 4 / 7 / 3; Hard 5 / 9 / 3.
- Score: correct-difficulty base (100/150/200) + 5 per unique clue − 10 per used hint, floored at zero.
- Accusations are one-time and backend validated. A case's persisted solution cannot be changed through game actions.
- Investigation renders only public suspect details and collected clues; the solution is revealed on Results after accusation.
- OpenRouter/Gemini output is bounded, parsed as strict JSON, and checked for schema, counts, unique IDs, and references. Invalid generation is retried up to three total attempts and is never saved.

## Limitations

Semantic review of an AI-written mystery cannot be proven by deterministic checks. The validator enforces structural consistency, references, unique IDs, and supporting-clue presence, but story-level ambiguity may still require human review. Interrogation responses are constrained with filtered context and a culprit-name disclosure check; automatic detection of every invented or indirectly revealing statement is not guaranteed. A safe fallback is used for detected disclosure or provider failure. Production deployments should use persistent storage and operational monitoring.

## Provider note

The project specification originally called for the official Gemini SDK. OpenRouter was added as the configured provider at the user's request to route requests through their OpenRouter account. The app uses OpenRouter's chat-completions API and requests JSON Schema output; the existing Pydantic validation remains authoritative. Scores and correctness are still determined only by the Python backend.
