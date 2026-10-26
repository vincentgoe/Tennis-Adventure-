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
- Hovering a hotspot highlights it and shows the action's label. Other
  hotspots show a small pulsing dot, so they can be found without hovering
  (e.g. on touch screens).
- If several visible actions share the same rectangle (e.g. "Inspect" and
  "Take" on a racket), clicking it opens a small menu with these actions.

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
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: play from the start to an ending using only clicks in the
      image. The locked door shows its message, the racket opens a menu,
      hidden actions are not clickable. Restarting the app still resumes.
- [ ] Committed on `point-and-click`, pushed, reviewed, merged into `main`.
