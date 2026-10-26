# Spec: visuals — Block-style images, tennis theme, icons

Status: **agreed** (author approved the plan on 2026-10-26).

## Why

The game works, but plain text and buttons feel flat. The BRD allows images
("images and sound are optional"). A simple block-style look, inspired by
Crossy Road, makes the tournament feel like a place to explore. It is also a
first step towards the world map (stage 3).

## What

### Scene images

- Every scene shows an image in a simple block style above its text.
- The image depends on the state in the same way as the scene text (PT R3).
  Examples: the shed shows two rackets before the choice and is empty
  afterwards. At the court, the net shows an indicator when a match is due,
  and the groundskeeper is visible once the player knows about him.
- Images are story content. Each entry in a scene's `texts` list in
  `story.json` gets an `image` field. The image of the first matching entry is
  shown, so text and image always belong together.
- Ending pages (`endings.*.pages`) get an `image` field as well.

### Items

- Each item in `story.json` gets an `image` field.
- The inventory in the sidebar shows each item's image next to its name.

### Theme and buttons

- Tennis colours: clay orange as the main colour, grass green, warm off-white
  background. Set in `.streamlit/config.toml`.
- Action buttons get an icon. Actions may set an `icon` in `story.json`.
  Without one, the app picks an icon from the action's effect (e.g. walking for
  `move_to`).

### Ending A

- The trophy in the award-ceremony image is animated (it shines and bounces).

### Files

- Images are SVG files in `assets/`, drawn for this project. No external
  service or download is needed at runtime.

## Out of scope

- Moving around freely (stage 3) and the match minigame (stage 2).
- Sound.
- Changing any rule. Existing tests must stay green without changes.

## Done when

- [x] New tests are written first and are green:
  - `scene_image` returns the image of the first matching text entry.
  - Every image referenced in `story.json` exists in `assets/`.
- [x] All existing tests are still green and unchanged.
- [x] Manual check: play from the start to an ending. Every scene, item and
      ending page shows a fitting image, and the shed and court images change
      with the state.
- [ ] Committed on `visuals`, pushed, reviewed, merged into `main`.
