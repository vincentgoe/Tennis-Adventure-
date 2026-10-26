# Spec: new-game — Start over with confirmation

Status: **agreed** (author asked for a restart button on 2026-10-26).

## Why

BRD PT01 / A6: starting over must ask for confirmation before replacing
existing progress. PT05: at an ending, the player can start a new game.
Until now, the only way to start over was to delete `plot_twist.db`.

## What

- The sidebar has a **"New game"** button, always visible (also at an ending).
- Clicking it shows the confirmation text from `ui_texts.new_game_confirm`
  with two buttons: **"Yes, start over"** and **"Cancel"**.
- **Cancel (A6):** the question disappears. Scene, items, flags, choices,
  match results and ending stay exactly as they were. Nothing is saved.
- **Confirm (A6):** a new game replaces the saved one: opening scene, empty
  inventory, no flags, no choices, no match results, no ending. The new game is
  saved at once, so restarting the app also starts from the opening scene.
- The last message (dialogue box) is cleared.
- Resume stays automatic (decision Q2 in `specs/first-feature.md`): opening
  the app continues the saved game.

## Out of scope

- "Give up" after losing a match (stage 2, minigame).
- Several save slots.

## Done when

- [ ] New tests written first and green:
  - A confirmed restart replaces the saved progress with a new game.
  - A cancelled restart leaves the saved progress unchanged.
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: "New game" → "Cancel" keeps the game; "New game" →
      "Yes, start over" shows the grounds with an empty inventory; restarting
      the app after that also shows the grounds.
- [ ] Committed on `new-game`, pushed, reviewed, merged into `main`.
