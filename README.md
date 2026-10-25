# TP NextGen Chatbot Arcade

**Workshop:** 26 October 2026, Day 1 · Temasek Polytechnic School of Informatics & IT. Students work in pairs on one laptop.

## Deploy to Streamlit Community Cloud

1. Unzip this archive and put the contents of `chatbot_arcade/` in the **root of your GitHub repository**. Include `.streamlit/config.toml`.
2. On Streamlit Community Cloud, choose `app.py` as the entry point and deploy. No API keys or database are required.
3. Open the deployed app from an incognito/student browser. Your existing public URL is `https://chatbotarcade.streamlit.app/`; updating this code in its connected repository is required to replace the existing version.
4. In the app, try all four stages, each with a broken rule, a user-selected fix, and the same request retested.

## What students do

**Stage 1 — Intent:** "Can I get a milk tea please?" fails, "order milk tea" works. Choose to recognise alternative request phrases. Retest natural phrasing.

**Stage 2 — Memory:** Set lychee tea then 25% sugar. The bot loses the earlier choice. Choose to update only a changed field, rebuild the order, choose no ice, confirm.

**Stage 3 — Clarification:** "Less sweet" is guessed as 50%. Choose to ask for an exact percentage and confirm 25%.

**Stage 4 — Validation:** The bot accepts an unavailable durian milkshake. Choose to check against the menu and confirm the same request is now refused.

Every stage shows an **Under the Hood** rule, a discussion question and a success explanation. Progress unlocks the next stage. An optional drinks counter is available after all four stages. Do not spend workshop time on free play if the students need more time in Conferbot.

## Important distinction

This is a deterministic, deliberately simplified **rule-based chatbot simulator**, not a generative language model. A correct fix changes the rule that controls future responses. The user’s actual Day 1 chatbot is built with **Conferbot**, following the separate Day 1 worksheet and its five-drink/three-size specification. The arcade’s six-flavour menu is not the Conferbot specification.

## Teaching goals and expected answers

| Stage | What went wrong? | Expected explanation |
| --- | --- | --- |
| Intent | Exact phrase only | Several requests can express one intent |
| Memory | Previous fields vanish | Update one value without overwriting all stored state |
| Clarification | Bot guesses at an ambiguous request | Ask a follow-up question |
| Validation | Unavailable item accepted | Check user input against accepted values |

Related G3 Computing concepts: inputs/outputs; flowchart sequence and selection; variables; IF/THEN rules; testing and debugging; iterative development (MOE G3 Computing syllabus 7155).

## Files

- `app.py`: Streamlit classroom interface and stage progression.
- `engine.py`: deterministic parsing, state transitions and events.
- `play.py`: optional drinks counter after stage completion.
- `test_engine_smoke.py`: dependency-free regression tests. Run `python -m unittest test_engine_smoke.py -v`.
- `test_arcade.py`: optional Streamlit AppTest checks. Run `python -m unittest test_arcade.py -v` after installing requirements.
- `.streamlit/config.toml`: theme settings.

## Correctness / classroom preflight

Run the unit tests, then start `streamlit run app.py`. Check stage-by-stage: the correct rule becomes available only after seeing a bug; a wrong rule is rejected; the same input works differently after fixing; no stage unlocks early; Replay does not erase completed stamps; no chatbot asks for real data.

The optional drinks counter uses local session state. Refreshed sessions may reset local progress; students can export/import a completed-stage checkpoint from Game Settings. This is a no-payment, no-personal-data classroom activity.
