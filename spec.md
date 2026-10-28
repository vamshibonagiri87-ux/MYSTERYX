1. Purpose and product vision
MYSTERYX is an AI-powered mystery investigation game. A player creates
or selects a fictional mystery, explores a case, inspects evidence,
interrogates suspects, requests hints, submits an accusation, and
receives a verdict with an evidence-based explanation and score.

The product must feel like a polished detective game, not a generic
chatbot. Its defining promise is that the story may be generated with
AI, but the culprit, evidence, game state, and scoring remain logically
consistent and controlled by the backend.
Product principles
1. Truth is deterministic: once a case is accepted, its culprit and
   solution are fixed.
2. AI is not the authority for game rules: Python validates cases,
   controls state, checks accusations, and calculates scores.
3. No premature reveal: the culprit, solution, and undiscovered
   clues must never be sent to the player-facing UI before the Results
   stage.
4. Evidence-based outcomes: every solution must be supported by the
   case's evidence and the explanation must cite actual clue IDs.
5. Playable first release: ship one complete, reliable end-to-end
   game before adding accounts, multiplayer, or other out-of-scope
   features.
6. Failure-safe: malformed model output or API failure must not
   create a playable invalid case or destroy saved progress.
2. Required technology stack
Use this stack unless a dependency is technically unavailable; document
any substitution before making it.
- Language: Python 3.11 or later, compatible with the deployment
  host.
- UI and web app: Streamlit.
- AI provider: Google Gemini API, accessed from the backend
  through the official supported Python SDK.
- Validation: Pydantic models or equivalent strict typed
  validation.
- Persistence: SQLite for accepted cases, player progress, clue
  discoveries, hint usage, accusations, and results. JSON may be used
  for local fixtures or development seed cases, but SQLite is the
  source of truth for saved game state.
- Configuration/secrets: environment variables and Streamlit
  secrets; never hard-code API keys.
- Testing: pytest.
- Deployment: a Streamlit-compatible host. The application must
  work after deployment with its Gemini key configured through the
  host's secret manager.
Suggested structure:
mysteryx/
  app.py
  pages/
    1_Create_Mystery.py
    2_Investigation_Room.py
    3_Accusation.py
    4_Results.py
  mysteryx/
    config.py
    models.py
    ai_service.py
    case_generator.py
    case_validator.py
    game_service.py
    scoring.py
    repository.py
    prompts.py
    ui_components.py
  tests/
    test_models.py
    test_case_validator.py
    test_scoring.py
    test_game_flow.py
  .streamlit/
    config.toml
  requirements.txt
  .env.example
  README.md
The exact file layout may be adapted, but responsibilities must remain
separated. Do not put all business logic and Gemini calls directly in
Streamlit page files.
3. User journey and navigation
Required journey:

Home → Create Mystery → Investigation Room → Accusation → Results
- Home's Start Investigation opens Create Mystery.
- Create Mystery's Generate Mystery or Random Mystery creates
  a validated case and opens Investigation Room.
- Investigation Room allows clue discovery, suspect inspection,
  interrogation, and hint requests.
- Make an Accusation opens Accusation without revealing the
  answer.
- A valid accusation is recorded once, scored by the backend, and
  opens Results.
- Play Again returns to Create Mystery.
- New Mystery starts a new case.
- Back navigation must preserve the active case and progress unless
  the user explicitly abandons or resets it.
- If a player tries to leave while a change is unsaved, show a clear
  warning where technically possible.
Use Streamlit navigation that is consistent and reliable. The current
case and page state must not depend only on transient widget values.
4. Visual design system
Design direction
A cinematic, premium detective-noir interface: - Background: charcoal /
near-black. - Primary accent: muted crimson. - Secondary accents:
restrained off-white and neutral gray. - Use crime-scene imagery
sparingly; prioritize readable information and evidence. - Cards for
suspects and clues, clear progress, visible case title, and a prominent
primary action. - Avoid excessive glow, clutter, and tiny text. Do not
sacrifice accessibility for atmosphere.
Shared layout requirements
- Consistent typography, spacing, button styles, card styles, and
  navigation across all screens.
- Accessible contrast and descriptive labels.
- Keyboard-accessible controls where supported.
- Status must not be conveyed by color alone.
- Desktop: make good use of available width.
- Tablet: collapse multi-column layouts as needed.
- Mobile: stack sections or use tabs/expanders for Story, Suspects,
  Evidence, and Chat; avoid horizontal overflow.
- Streamlit UI should use supported Streamlit components rather than
  relying on unsupported browser hacks.
5. Page specifications
5.1 Home
Purpose: Introduce MYSTERYX and start the experience.

Required elements - Product name: MYSTERYX --- The Room That
Thinks. - Tagline: "Every clue tells a story. Every suspect hides a
secret." - Short explanation of the game. - Primary Start
Investigation button. - How to Play instructions or expandable
section. - Optional Resume Case only if a resumable case exists.

Interactions - Start Investigation → Create Mystery. - How to Play →
show rules: inspect evidence, question suspects, use hints carefully,
then accuse. - Resume Case → reopen the saved active case if supported.

States - Loading transition should be brief and never look like a
frozen page. - If navigation or state restoration fails: "Unable to open
the investigation. Please try again." - Hide or disable Resume Case when
no active case exists.
5.2 Create Mystery
Purpose: Gather a premise and difficulty, then create a playable
mystery.

Required elements - Text area for the user's fictional mystery
premise. - Placeholder example, e.g. "A priceless diamond disappears
from a locked mansion." - Difficulty selector: Easy, Medium, Hard. -
Generate Mystery button. - Random Mystery button that uses a
safe built-in premise or chooses one from a small curated list. -
Validation and generation status.

Rules - A premise is required for Generate Mystery. - Trim
whitespace and enforce a reasonable length, recommended 20--500
characters. - Random Mystery must not require manual premise input. -
Difficulty must be one of the three supported values. - Do not save or
open a case until generation and validation succeed.

Errors - Empty premise: "Enter a mystery premise or choose Random
Mystery." - Premise too short/long: explain the accepted length. -
Invalid premise: "Please provide a fictional mystery scenario we can
investigate." - Gemini/API unavailable: "We couldn't generate your
mystery. Please try again." - Invalid generated response after retry:
"The generated case failed validation. No case was saved; try again."

Loading - Show "Building your case..." and a spinner/progress
indicator. - Disable duplicate generation submissions while a request is
in progress. - Do not claim a percentage unless real progress is known.
5.3 Investigation Room
Purpose: Main gameplay screen.

Required elements - Case title, premise/story, and selected
difficulty. - Investigation progress (for example, clues discovered /
total clues). - Suspect cards containing only player-visible profile
details. - Evidence/clue inventory. - Suspect interrogation chat. -
Request Hint button with remaining hints. - Make an Accusation
button. - Clear indication of clues already discovered.

Interactions - Clicking a suspect opens their profile and
interrogation panel. - Players can ask natural-language questions about
the case. - A suspect response must remain consistent with the stored
case facts and that suspect's knowledge. - Discovering a clue adds it to
the player's collected evidence and awards clue points once. - Reopening
a clue does not award points again. - Request Hint returns the next
eligible hint and deducts the hint penalty once per hint actually
used. - Once the configured hint limit is reached, disable the button
and explain that no hints remain. - Make an Accusation opens the
Accusation page without revealing the solution.

Clue behavior - Each case contains the exact number of clues
required by its difficulty. - The case can expose clues as interactive
objects/cards. A clue may be available to inspect, but it is only
"discovered" for scoring when the player explicitly opens/collects it. -
Clue text must not contain a direct answer unless that is a deliberate
late-game clue; never show the hidden solution object. - The clue
inventory should show discovered clues only. Undiscovered clue
titles/details must not be leaked to the UI/API response.

Interrogation behavior - User questions are sent to the backend. -
Backend sends Gemini only the minimum relevant case context and the
selected suspect's public profile, testimony constraints, and allowed
knowledge. - Do not send the entire hidden answer key to a general
dialogue call unless strictly required; prefer a filtered context that
prevents accidental disclosure. - AI must not invent new evidence,
suspects, locations, dates, or facts. - AI must not reveal the culprit
directly or indirectly before Results. - If a question is unrelated,
respond briefly and guide the player back to the case. - Chat history
should be preserved for the active case. - Apply a reasonable input
limit and handle empty questions.

States and errors - AI typing/loading: "The suspect is
thinking..." - No clues discovered: "No evidence collected yet. Explore
the room." - API failure: "The response couldn't be generated. Your
investigation is saved; try again." - Empty question: "Enter a question
for the suspect." - Rate limit: show a friendly retry message; do not
crash. - If the app reruns, restore the current case and progress from
durable state.

Responsive behavior - Desktop: three conceptual areas for suspects,
investigation/chat, and evidence. - Tablet: two columns or tabs. -
Mobile: stacked sections or tabs: Story, Suspects, Evidence, Chat.
5.4 Accusation
Purpose: Let the player submit a final suspect selection.

Required elements - Brief case recap. - Selectable suspect cards. -
Optional text area: "Why do you suspect this person?" - Evidence review
showing discovered clues only. - Submit Accusation button. -
Return to Investigation button.

Rules - Exactly one suspect must be selected. - The selected suspect
ID must exist in the active case. - Confirmation dialog/message before
final submission: "Are you ready to submit your final accusation?" - A
final accusation is immutable for that attempt; prevent double
submission. - If the player returns to the investigation before
submission, preserve progress. - Do not reveal correctness until
Results.

Errors - No selection: "Select a suspect before submitting." -
Invalid suspect: reject on backend and show "That suspect is not part of
this case." - Submission failure: "Your accusation wasn't submitted.
Please try again." - Duplicate submission: return the existing result
rather than scoring again.
5.5 Results
Purpose: Reveal the outcome and explain the score.

Required elements - Outcome: Case Solved! for a correct
accusation, otherwise The Mystery Remains Unsolved. - Player's
selected suspect. - Actual culprit's identity. - Final score and
breakdown. - Explanation that links the solution to actual
discovered/available case clue IDs and established facts. - Supporting
clues and relevant contradictions. - Missed evidence/feedback. - Play
Again and New Mystery actions.

Rules - Results must use the stored case solution and backend
score. - The explanation must not introduce facts or evidence that were
absent from the accepted case. - Show the correct culprit only after the
accusation is submitted. - If result retrieval fails, preserve the
accusation and score state and offer retry. - Do not calculate or trust
the score in the UI.
6. Difficulty and case content requirements
The case generator must produce exactly these counts:

  Difficulty     Suspects   Clues   Hints
  Easy                  3       5       2
  Medium                4       7       3
  Hard                  5       9       3

All counts are exact, not minimums.
Mystery quality requirements
Every accepted mystery must: 1. Have exactly one intended culprit. 2.
Have a coherent timeline and plausible motive/opportunity. 3. Include
evidence that supports the intended solution. 4. Give each suspect a
distinct identity and plausible profile. 5. Include plausible but
non-decisive information for innocent suspects. 6. Avoid contradictions
that make the mystery unsolvable or make multiple suspects equally
correct. 7. Have hints that progressively guide the player without
immediately naming the culprit. 8. Have a solution explanation that
cites valid clue IDs. 9. Be safe, fictional, and suitable for a general
student project. 10. Remain fixed after validation; do not regenerate or
silently alter the truth mid-game.
7. Gemini output contract
Gemini mystery generation must return JSON only, with no Markdown
fences or surrounding prose. Validate the result with strict typed
models before saving it.
Required generation JSON shape
{
  "case_id": "generated-on-backend",
  "title": "The Missing Diamond",
  "premise": "A diamond vanished from a locked mansion.",
  "difficulty": "Easy",
  "story": "A concise opening narrative for the player.",
  "suspects": [
    {
      "id": "S1",
      "name": "Alex",
      "profile": "A brief public-facing profile.",
      "motive": "A possible motive, not proof of guilt.",
      "public_alibi": "The statement the player can learn.",
      "private_truth": "Internal consistency note; never send directly to the player."
    }
  ],
  "clues": [
    {
      "id": "C1",
      "title": "Muddy Footprint",
      "description": "A footprint is found near the display case.",
      "details": "Additional inspectable detail.",
      "implicates_suspect_ids": ["S1"],
      "solution_relevance": "Internal note explaining how this clue supports or eliminates a theory."
    }
  ],
  "hints": [
    {
      "id": "H1",
      "text": "Look closely at the route into the room.",
      "reveal_level": 1
    }
  ],
  "solution": {
    "culprit_id": "S1",
    "reasoning": "The culprit's established timeline conflicts with the physical evidence.",
    "supporting_clue_ids": ["C1"],
    "full_explanation": "A complete explanation grounded in the case facts."
  },
  "timeline": [
    {
      "time": "20:00",
      "event": "The display case was last confirmed secure."
    }
  ]
}
This is the logical contract, not a literal requirement to trust
model-supplied IDs. The backend should assign case_id and preferably
normalize or validate all IDs. Every required object must be present.
Fields designated internal (private_truth, solution_relevance,
solution, and any hidden timeline details) must never be rendered in
player-facing screens before Results.
Recommended model constraints
- difficulty: enum Easy | Medium | Hard.
- suspects: exact count based on difficulty.
- clues: exact count based on difficulty.
- hints: exact count based on difficulty.
- IDs must be unique within their categories.
- solution.culprit_id must match one suspect ID.
- Every supporting_clue_id must match an existing clue ID.
- Every implicates_suspect_ids item must match an existing suspect
  ID.
- reveal_level must be an integer within the available hint
  sequence.
- Strings must be non-empty where required and bounded in length.
- Reject unexpected fields where practical (extra="forbid" in
  Pydantic).
- The final case must be stored only after semantic checks pass.
Validation pipeline
1. Call Gemini with the structured output contract and selected
   difficulty.
2. Parse JSON; reject Markdown wrappers, trailing text, invalid JSON,
   or missing fields.
3. Validate types, enums, counts, unique IDs, references, and lengths.
4. Run semantic checks for one culprit, timeline coherence, clue
   support, and hint safety.
5. If invalid, retry generation a limited number of times (recommended
   maximum: 2 retries after the first attempt).
6. If still invalid, save nothing and show the generation error.
7. Assign a backend-generated unique case ID and persist the accepted
   case.
8. Separate public case data from private answer-key data in storage
   and service responses.
Semantic validation limitation
A model can assist with drafting and reviewing a mystery, but an LLM's
self-assessment is not proof of logical consistency. Use deterministic
checks where possible and a separate review call as an additional
quality gate if desired. The accepted solution must be grounded in the
same immutable stored facts. Never let a review call silently change the
culprit after gameplay begins.
8. Suspect interrogation contract
Interrogation is conversational, but the case truth is fixed.
System behavior
- Speak as the selected suspect, in their established voice.
- Answer only from that suspect's knowledge and approved case facts.
- Do not invent facts, clues, witnesses, events, or alibis.
- Do not expose internal fields or the answer key.
- Do not explicitly reveal the culprit before Results.
- A suspect may be evasive or deceptive only if that behavior is
  consistent with their stored profile and truth.
- Keep answers concise and useful for gameplay.
- If asked to reveal the answer, respond in character without giving
  it away.
- If the question is unrelated, redirect gently.
Backend request/response
Use a typed internal structure, for example:
{
  "suspect_id": "S1",
  "question": "Why were you near the study?",
  "response": "I passed the hallway earlier, but I never entered the study."
}
Validate the response before showing it. If it asserts an unknown fact,
reveals the answer, or conflicts with a hard case constraint, reject it
and use a safe fallback response. Do not rely on prompt instructions
alone for confidentiality.
9. Hint contract
- Easy: 2 hints.
- Medium: 3 hints.
- Hard: 3 hints.
- Hints are delivered in order, one request at a time.
- A hint is counted as used only when a valid hint is actually
  returned to the player.
- Repeated clicks must not charge the same hint twice.
- Once all hints are used, further requests do not deduct points and
  must return a clear "No hints remaining" message.
- Hints must guide attention to evidence or reasoning and must not
  directly state the culprit's identity.
- Hint use and score impact are stored on the backend.
10. Scoring rules
Formula
final_score = max(0, base_points + clue_points - hint_penalties)

Where: -
base_points = difficulty base points if correct, otherwise 0. -
clue_points = 5 × number of distinct clues discovered. -
hint_penalties = 10 × number of hints used.
  Difficulty     Correct accusation         Clue value       Hint penalty
                        base points                    
  Easy                          100    +5 per distinct           −10 each
                                                  clue 

  Medium                        150    +5 per distinct           −10 each
                                                  clue 

  Hard                          200    +5 per distinct           −10 each
                                              clue 
An incorrect accusation earns zero base points, but the player retains
discovered-clue points and receives hint penalties; final score is never
below zero.
Scoring examples
- Medium, correct, 5 clues, 1 hint: 150 + 25 - 10 = 165.
- Easy, incorrect, 3 clues, 2 hints: 0 + 15 - 20 = 0.
- Hard, correct, 9 clues, 3 hints: 200 + 45 - 30 = 215.
Integrity
- Score is calculated only in backend Python code.
- Never accept a client-provided score.
- Count each clue at most once.
- Count each delivered hint at most once.
- Validate difficulty and IDs against the stored case.
- Make accusation submission idempotent: duplicate requests return the
  existing result and never award points twice.
- Store the score breakdown for auditability.
- Results UI only displays backend-calculated values.
11. Data model and persistence
Use SQLite tables or equivalent normalized storage for:
Cases
- case_id (primary key)
- title
- premise
- difficulty
- public_case_json
- private_solution_json
- created_at
- schema_version
- status (accepted/archived)
Game sessions
- session_id (primary key)
- case_id (foreign key)
- status (investigating/accused/completed)
- current_page
- created_at
- updated_at
Clue discoveries
- session_id
- clue_id
- discovered_at
- Unique constraint on (session_id, clue_id)
Hint usage
- session_id
- hint_id
- used_at
- Unique constraint on (session_id, hint_id)
Interrogation messages
- session_id
- suspect_id
- role (user/assistant)
- message
- created_at
Accusations/results
- session_id (unique for one final attempt)
- selected_suspect_id
- reasoning_text (optional)
- is_correct
- base_points
- clue_points
- hint_penalties
- final_score
- submitted_at
Persist all state needed to survive Streamlit reruns and refreshes. Do
not rely exclusively on st.session_state for durable state. If
authentication is not part of the first release, make it clear that
sessions are local/anonymous and do not imply cross-device accounts.
12. Error handling and loading behavior
All AI calls must have timeouts, exception handling, and user-safe error
messages. Never show raw API keys, stack traces, or internal prompts to
the player.
  Situation                           Required user-facing behavior
  Empty premise                       Ask the player to enter a premise
                                      or choose Random Mystery

  Gemini timeout/unavailable          Explain generation failed and offer
                                      retry

  Invalid JSON/schema                 Retry limited times; do not save
                                      invalid case

  Semantic case validation failure    Retry limited times; do not save
                                      invalid case

  Interrogation API failure           Preserve progress and offer retry

  Hint API/data failure               Do not deduct a hint unless a valid
                                      hint is delivered

  Invalid suspect selection           Reject on backend and ask for a
                                      valid selection

  Duplicate accusation                Return the existing result; do not
                                      rescore

  SQLite/storage error                Preserve recoverable state and show
                                      a friendly error

  Missing Gemini key                  Show a clear setup error to the
                                      developer/operator, not the secret

  No remaining hints                  Explain that all hints have been
                                      used

  Result retrieval failure            Keep saved accusation and score;
                                  offer retry
Log technical details server-side without logging API keys or
unnecessary sensitive data.
13. Security and reliability
- Store Gemini API keys in environment variables or Streamlit secrets.
- Never expose secrets in source control, UI, logs, client payloads,
  or generated files.
- Treat player premise and chat messages as untrusted input.
- Do not let user prompts override the game rules or reveal internal
  data.
- Keep private solution fields separate from public case data.
- Validate every action on the backend, even if the UI already
  validates it.
- Use parameterized SQL queries.
- Bound input length and model output size.
- Apply sensible request limits and handle provider rate limits.
- Avoid writing private answer keys to debug logs.
- Ensure a case's culprit and facts cannot change after it is
  accepted.
- Do not claim that the AI can reliably detect lies from emotion or
  facial expression; contradiction detection must be based on recorded
  facts and evidence.
14. Testing requirements
Use pytest for automated tests.
Unit tests
- Difficulty configuration returns the exact suspect/clue/hint counts.
- JSON parsing rejects malformed JSON.
- Schema validation rejects missing fields, invalid enums, and
  unexpected types.
- Validation rejects duplicate IDs and broken references.
- Validation rejects a culprit ID not present in suspects.
- Validation rejects supporting clue IDs that do not exist.
- Scoring formula returns correct values for correct and incorrect
  accusations.
- Score minimum is zero.
- Duplicate clue discovery does not add points.
- Duplicate hint use does not charge twice.
- Duplicate accusation does not create a second result.
- Player-facing case serializer omits private solution fields.
Integration tests
- Generate a case using a mocked Gemini response and save it only
  after validation.
- Invalid Gemini response is retried and eventually fails safely.
- Player can discover clues, question suspects, use hints, and submit
  an accusation.
- Results show the stored culprit and stored score.
- State survives app reruns/refreshes.
- API failures do not lose progress.
End-to-end manual tests
- Complete a case at Easy, Medium, and Hard.
- Verify all counts and hint limits.
- Verify the answer is not exposed before accusation.
- Verify score breakdown against manual calculations.
- Test wrong and correct accusations.
- Test desktop, tablet-width, and mobile-width layouts.
- Test deployed website with a valid Gemini secret.
- Test missing/invalid secret and provider failure behavior.
15. Acceptance criteria --- definition of done
The project is complete only when all mandatory criteria pass:
1. Users can generate mysteries at Easy, Medium, and Hard.
2. Each accepted case has exactly the required number of suspects,
   clues, and hints.
3. Generated responses are schema-validated and semantically checked
   before saving.
4. The mystery has one fixed, logically consistent culprit supported by
   the stored clues.
5. Players can investigate, collect clues, interrogate suspects, and
   request hints.
6. The number of hints is limited by difficulty and hint penalties are
   applied correctly.
7. The solution is not revealed before the Results page.
8. Players can submit one valid accusation per game session.
9. Backend Python calculates and validates all scores.
10. Results display the correct culprit, verdict, score breakdown, and
    evidence-based explanation.
11. Invalid input, malformed model output, API errors, and storage
    errors are handled gracefully.
12. Progress persists across Streamlit reruns and normal page
    navigation.
13. The deployed website completes the full Home → Create → Investigate
    → Accuse → Results flow.
14. The app works at desktop and mobile screen sizes.
15. Automated tests for validation, scoring, and core game flow pass.
16. Setup instructions, environment variable documentation, and
    deployment instructions are included in README.md.
16. Explicit out-of-scope items for version 1
Do not add these before the required core game is complete: - User
accounts, social login, or profiles. - Multiplayer or live co-op. -
Payments, subscriptions, or leaderboards. - Voice input/output. -
Real-world crime data or real-person accusations. - Complex 3D
environments. - Face/emotion-based lie detection. - Unbounded automatic
case generation without validation.

These can be considered later, but must not delay the first complete
playable release.
17. Implementation order for Codex
Build in this order and keep the app runnable at every milestone:
1. Create the project structure, requirements, configuration, and
   README.
2. Define strict Pydantic models and difficulty configuration.
3. Implement scoring and deterministic unit tests.
4. Implement SQLite repository and durable session state.
5. Implement Gemini generation, parsing, validation, retry, and safe
   failure behavior.
6. Create one known-good deterministic seed case for development and
   tests.
7. Build Home and Create Mystery.
8. Build Investigation Room, clue discovery, suspect interrogation, and
   hints.
9. Build Accusation and Results.
10. Add error/loading states and responsive polish.
11. Add unit, integration, and end-to-end tests.
12. Verify secrets configuration and deploy.
13. Run the acceptance checklist against the deployed website.
Do not use a live Gemini call in every automated test; mock the provider
and keep deterministic test fixtures. A real API smoke test can be run
separately when a valid key is configured.
18. Final instruction to the implementation agent
Treat this document as the single source of truth. Do not silently
remove requirements, alter scoring, change difficulty counts, expose the
answer early, or let Gemini control correctness. If a requirement
conflicts with a technical constraint, explain the conflict and choose
the smallest change that preserves the product principles.

Required final deliverable: a deployed, playable MYSTERYX
application with source code, dependency list, .env.example, README
setup/deployment instructions, and passing tests for schema validation,
game rules, scoring, and the main gameplay flow.