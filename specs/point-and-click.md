# Spec: point-and-click — Click in the scene image to act

Status: **agreed** (author chose approach "B-light" on 2026-10-26).

## Why

The block-style images make the game feel like a place, but the player still
acts through a list of buttons. In a point-and-click adventure, the player
stands in the scene and clicks on things: the door, a person, the way out.
This makes exploring more fun and is a step towards the world map (stage 3).

## What

### Player figure

- The player is drawn into every scene image as a small block figure.
- Each scene in `story.json` has a `player` position (`x`, `y`, `scale`) in
  image coordinates (the image is 320 × 180 units).

### Hotspots

- Every action in `story.json` has a `hotspot`: a rectangle `x`, `y`, `w`,
  `h` in image coordinates, e.g. the shed door for "Open the door".
- Exits (`move_to` actions that lead back) have `"marker": "exit"` and are
  shown as an arrow badge at the edge of the image.
- Only **visible** actions have a clickable hotspot (same rule as the buttons):
  - Allowed actions are clickable.
  - Blocked actions with a `blocked_text` are clickable and show the blocked
    message (e.g. the locked shed door).
  - Hidden actions have no hotspot (e.g. the groundskeeper before the hint).
- Every non-exit hotspot has a short `name` (e.g. "Office", "Groundskeeper",
  "Old Yonex"). The name is shown as a label above the thing it belongs to,
  so clickable things can be found without hovering. Hotspots have no white
  borders and no dots (author feedback). The label is highlighted on hover.
- A hotspot may set `label_at` (`[x, y]`) when the label does not fit above it.
- The building signs that were painted into the grounds image ("OFFICE",
  "LOCKERS") are removed, because the labels replace them.
- If several visible actions share the same rectangle (e.g. "Inspect" and
  "Take" on a racket), clicking it opens a small menu with these actions.

### Dialogue box

- After an action, its message pops up in a text box at the bottom of the
  scene image, instead of below the image.
- If a **person** speaks, the box shows the speaker's name and the text
  appears letter by letter. Who speaks is story content: an action, or an
  entry in its `blocked_text`, may set a `speaker` (e.g. "Groundskeeper",
  "Steward").
- Text about **objects** and narration (inspecting, matches, the locked door)
  has no speaker and appears all at once.
- Clicking the box while text is still appearing shows the full text.
  Clicking it again closes it.
- A new pure function `logic.speaker_for(state, action_id, story)` returns the
  speaker of the message an action would produce in this state (the action's
  speaker if it is allowed, otherwise the speaker of the matching blocked text,
  otherwise `None`).

### Rules and saving

- A click goes through the same path as a button: `logic.apply_action`, then
  saving only if the action was accepted. No rule changes.
- A new pure function `logic.scene_hotspots(state, story)` returns the hotspots
  of the visible actions, so the rule "only visible actions are clickable" is
  tested in Python.

### Buttons

- The action buttons stay as a fallback, collapsed under "All actions".

### Component

- A small custom Streamlit component in `components/scene_view/` (one HTML
  file with plain JavaScript, no build step, no extra package). It shows the
  SVG image with the hotspots on top and reports the clicked action id.
- The JavaScript is not covered by pytest. It is checked in the manual
  walkthrough.

## Out of scope

- Walking animations and free movement (stage 3).
- The match minigame (stage 2).
- Changing any rule. Existing tests must stay green without changes.

## Done when

- [ ] New tests are written first and are green:
  - `scene_hotspots` returns hotspots only for visible actions, including
    blocked actions with a `blocked_text`.
  - In `story.json`, every action has a hotspot inside the image, and every
    scene has a player position inside the image.
  - Every non-exit hotspot has a name, and `scene_hotspots` passes it on.
  - `speaker_for` returns the action's speaker, the blocked text's speaker, or
    `None` for objects and narration.
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: play from the start to an ending using only clicks in the
      image. The locked door shows its message, the racket opens a menu,
      hidden actions are not clickable, people's lines appear letter by letter
      and object texts at once. Restarting the app still resumes.
- [ ] Committed on `point-and-click`, pushed, reviewed, merged into `main`.
