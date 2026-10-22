# Chatbot Arcade | TP Applied AI | 26 October 2026

A local, deterministic chatbot game for the first day of the Temasek Polytechnic secondary-school chatbot workshop. It works without a model API or learner login. After the four challenges, pairs unlock a bubble-tea counter and can copy a **Conferbot** starter prompt.

## Workshop flow

- **Day 1 (26 Oct):** Spend approximately 25–30 minutes on the arcade in pairs. Complete the four fixes; free-play is optional. Move to the Conferbot Day 1 worksheet and create an ordering chatbot.
- **Day 2 (27 Oct):** Continue with Conferbot using the Day 2 worksheet to build each pair's own idea and show selected chatbots in a short presentation.
- **Device policy:** One laptop per pair. Swap who controls the keyboard after each stage. Do not exchange devices with other pairs.

## Deploy to Streamlit Community Cloud

1. Unzip this package.
2. Put **the contents of the `chatbot_arcade` folder** into the root of your GitHub repository, retaining `.streamlit/config.toml`.
3. In Streamlit Community Cloud, choose **Create app**, select the repository and branch, and set the entrypoint to `app.py`.
4. Deploy. No API keys or secrets are needed.
5. Test the four stages and the Conferbot reveal on a student laptop before the class.

Local dry-run: `pip install -r requirements.txt` then `streamlit run app.py`.

## Controls and safeguards

- All four stages are rule-based, not an LLM demonstration.
- Only fictional drink orders are used; no real payments or personal data.
- Free play has six drinks, two sizes, five sugar levels, four ice options and five toppings (up to two per order).
- Each browser session has its own in-memory state. Refreshes may restart progress; the checkpoint file can restore earned stages, but not chats or counter recipes.
- The final reveal points to **Conferbot**, not Voiceflow.
- Starter prompt is under 900 characters for short description fields. The longer flow checklist is optional and is **not** intended to be pasted into the same description field.
- Conferbot's interface, plan limits and generated flows may change. Students should use the visual editor and Preview to correct mistakes rather than assuming generation is perfect.

## How to test

Run `python -m unittest -v test_arcade.py`. The test file checks stage gating, typed inputs, repair logic, checkpoints, drink editing, session isolation, customisation and the Conferbot reveal. This package has not been deployed to your Streamlit account.

## Stage answers for the facilitator

1. **Words matter:** `Can I get a milk tea please?` followed by `order milk tea`.
2. **Remember my order:** `Lychee tea` then `25% sugar`, enable memory, redo `Lychee tea`, `Actually, no ice`, and `Confirm`.
3. **Ask, don’t guess:** `Less sweet please`, enable clarification, repeat it and answer `25% sugar`.
4. **Stick to the menu:** Ask for a `durian milkshake`, enable menu checking, ask again.

## File map

- `app.py`: game layout, guided stages, checkpoint UI.
- `engine.py`: deterministic replies, validation, stage completion, copyable Conferbot prompt.
- `play.py`: recipe builder, SVG cup preview, optional customer challenges, Conferbot reveal.
- `test_arcade.py`: automated tests.
- `.streamlit/config.toml`: TP-inspired blue theme.
