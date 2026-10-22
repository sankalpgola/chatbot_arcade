# Chatbot Arcade: Fix the bubble-tea bot

Version 3 keeps the four guided stages and adds a BBT free-play counter. The game runs entirely inside Streamlit without API keys or model services. After completing the stages, students can reveal Voiceflow and copy instructions for later. No generated images are used; the cup preview is drawn in SVG from the current order.

## Deploy

1. Extract the ZIP and upload the contents of `chatbot_arcade` to your GitHub repository root.
2. Keep `.streamlit/config.toml` inside its folder. If the uploader hides it, use GitHub's Add file > Create new file with `.streamlit/config.toml` as the filename.
3. At https://share.streamlit.io choose Create app, select your repository, and set the entrypoint to `app.py`.
4. Choose Python 3.11 or 3.12. No secrets are required.
5. Deploy and rehearse once on a student-network device.

To update your existing app, replace its source files with this package. Delete the old `live_ai.py` and `.streamlit/secrets.example.toml` if present. This version does not use any model service or old secrets. Streamlit normally rebuilds when the connected repository changes.

Local launch:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Student experience

Four numbered stage buttons show the current, completed and locked stages. Students start at stage 1 and use Next to proceed. Completed stages remain available for replay.

Every stage has a short next-step instruction, a chat, an order card and suggested messages. Clicking a suggestion sends it immediately. Students can also type their own message and press Enter or Send. The text box clears after sending. The latest exchange stays visible without an inner scrolling box. Earlier messages are in a comparison expander. The chat retains up to 30 messages.

Only one behaviour is introduced at a time. A repair button appears after students observe the problem. No radio selectors or collections of unexplained toggles.

| Stage | Student task | Lesson |
|---|---|---|
| 1. Words matter | Ask naturally, then send the supported command. | Exact matching misses equivalent wording. |
| 2. Remember my order | See the bot forget, enable memory, build and confirm an order. | Keep conversation state and update only changed details. |
| 3. Ask, don't guess | Say less sweet, see it guess, enable clarification and choose 25%. | Resolve ambiguity by asking. |
| 4. Stick to the menu | Request durian milkshake, see it accept an unavailable item, enable menu checking. | Reply from known facts. |

The finish screen unlocks a free-play counter. Students use a recipe builder, send their recipe to the same chatbot, then change it through chat. A cup preview and order card show the accepted choices. “Surprise me” sends a random valid recipe. Three optional customer orders award stamps when the exact order is confirmed.

The builder is a message composer, not a live view of the accepted order. The order card is authoritative. Changing builder selections does not change the order until Send my recipe is clicked. Chat changes affect the order card, not the form selections.

A bot name and four reply styles let students personalise the counter. These are simple scripted styles; they do not turn the game into an AI model.

Only here, after the four stages, does Reveal the next step introduce Voiceflow. It includes a link, a code box with Streamlit's copy control, and a text download. Instructions include the student's chosen name and style, all menu options, memory, clarification, topping limits and example tests. Students do not need to sign in or leave the game to finish playing.

## Teaching run: 20 to 30 minutes

Allow about 15 to 20 minutes for the guided stages and 5 to 10 minutes for free play. Use pairs and switch keyboard control after each stage. Ask students to predict the reply before sending. After a repair, have them explain what changed. Encourage a self-written message after the guided examples. The suggestions make the first attempt approachable; the conversation and explanation are the learning activity.

This is a rule-based teaching simulation, not a live generative AI model. The game menu and finish screen explain this. The deliberately broken behaviours make each lesson repeatable. Do not claim that every AI system works this way.

## Supported conversation

The menu is prominently displayed in the main page and summarised in the sidebar:

- Six flavours: milk tea, lychee tea, lemon tea, taro milk tea, matcha milk tea and brown sugar milk tea.
- Two sizes: regular or large.
- Five sugar levels: 0%, 25%, 50%, 75%, 100%.
- Four ice options: no ice, less ice, normal ice, extra ice.
- Up to two different toppings: pearls, pudding, grass jelly, aloe vera, coconut jelly. No toppings is also allowed.

Size defaults to regular and toppings to none. The card and summaries make these defaults explicit. Drink, sugar and ice are required before confirmation.

Examples: `one large taro milk tea, 75% sugar, extra ice, with pearls and pudding`, `add aloe vera`, `remove pearls`, `no toppings`, `make it large`, `actually, no ice`, `make it 25%`, `sugar 25`, and `less sweet`.

Adding a topping preserves existing toppings. Removing one keeps the others. A topping list without add/remove replaces the current selection. A third distinct topping is rejected without changing the order. Any accepted order change cancels confirmation. For clarity, topping additions and removals in the same message need to be sent separately.

The expanded menu also works from stage 2 onwards. Optional “Play a little” buttons appear after completed stages. Extra size or topping choices do not prevent completion of the memory lesson. Stage 1 deliberately retains its exact-command limitation.

This parser is intentionally limited. Unrecognised messages offer examples and do not penalise the student or corrupt the order. Unusual wording may need rephrasing. Exact-command matching applies only to stage 1.

## Progress and stability

- Each browser session has separate progress and chats.
- Stages award a stamp once. The stage bar updates after messages.
- Restart this stage resets that conversation and repair, retaining earned stamps.
- Full restart requires confirmation.
- Save checkpoint downloads completed stages and navigation position as JSON. Load it after a refresh or on another device. Chats, the unfinished stage, counter customisations and customer stamps restart, as stated in the interface. Checkpoint format remains compatible with version 2.
- Checkpoint imports validate size, format, version and a sequential list of stages. They are classroom convenience files, not secure graded-assessment records.
- There is no database, provider call, shared leaderboard or real purchase.

## Facilitator answers

1. Send `Can I get a milk tea please?`, then `order milk tea`.
2. Send `Lychee tea`, then `25% sugar`. The drink disappears. Enable memory. Send `Lychee tea`, then `Actually, no ice`, then `Confirm`. The sugar is retained from before the repair.
3. Send `Less sweet please`. Enable clarification. Repeat it, then send `25% sugar`.
4. Send `Can I get a durian milkshake?`. Enable menu checking. Repeat the request.

Suggested message buttons adapt along this path. They use the same reply engine as typed input. A checkpoint or replay can retain an earned stamp while starting that conversation again.

## Files and tests

`app.py`: guided stages and navigation. `engine.py`: replies, menu, instructions, completion and checkpoints. `play.py`: free-play counter, cup preview, optional customers and final reveal. `.streamlit/config.toml`: theme. `test_arcade.py`: interaction tests and recovery cases.

Run from the project folder:

```bash
python -m unittest -v test_arcade.py
```

Automated verification uses Streamlit 1.50.0 with Python 3.12. Seven automated tests pass. They check the guided journey, typed replies, stage gating, replay, session isolation, parser edge cases, checkpoint validation, all six fully customised recipes, topping swaps and limits, customer stamps and the gated final reveal. The app has not been deployed to your account. Rehearse in a browser before class.

Deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

Voiceflow quick-start reference: https://www.voiceflow.com/docs/courses/chat-agent-quick-start
The current setup guide starts at Projects > New project > Start from scratch and the global agent description. Students should follow the lecturer’s account and usage arrangements. These exported prompts have not been run in the user’s Voiceflow account.
