# Acceptance overview — Plot Twist

How every requirement of the BRD (`docs/product-brief.md`) is met: where it
shows in the game, and which automated tests check it. Tests are in `tests/`;
run them with `uv run pytest`.

## Summary

| BRD | Requirement | Met by |
| --- | --- | --- |
| First release | ≥ 5 scenes, ≥ 2 items, 2 reachable endings, one ending depends on a choice/item | 8 scenes (entrance, office, main path, locker room, Center Court, Court 2, back corner, inside the shed); items key, Wilson Blade, Old Yonex; Ending A (Yonex) and Ending B (Wilson) |
| PT01 | Start and resume; starting over asks for confirmation | A saved game resumes automatically when the app opens (decision Q2 in `specs/first-feature.md`); "New game" asks for confirmation |
| PT02 | Show the scene and its actions; every accepted choice has a visible result | Scene picture with clickable spots and an "All actions" list; every action moves, shows a text, changes the inventory or starts a match |
| PT03 | Inventory; an item unlocks an action; no duplicates | Inventory list top right; the key unlocks the shed; the key is collected once |
| PT04 | A remembered decision affects a later action or ending; blocked actions are explained or hidden | The racket choice decides rounds 3–4 and the ending; blocked actions show a reason (steward, padlock, locker room closed, …), others are hidden until available |
| PT05 | Endings are clearly identified; story actions stop at an ending | "ENDING A: The Racket of a Legend" / "ENDING B: Runner-up", end pages with THE END; no actions at an ending; "New game" stays available |
| PT R1 | Actions only when scene and conditions allow; blocked actions change nothing | Central rule in `logic.apply_action` |
| PT R2 | Items only where available, once per game, not consumed | Key from the groundskeeper only; stays after unlocking |
| PT R3 | Revisited scenes reflect changes | Groundskeeper's three lines, empty shed after the choice, open shed after unlocking, office lines |
| PT R4 | New game resets progress, keeps the story; every ending reachable | `logic.new_game`, "New game"; both endings played through in tests |
| Remember | Scene, items, decisions, ending; save after each accepted action | SQLite table `game` (`db.py`); `app.py` saves after every accepted action and match result |

## Scenarios A1–A6

### A1 — A locked route
The shed door without the key: the action is visible, the padlock message
appears, location and inventory do not change.

- `test_logic.py::test_open_shed_without_key_is_rejected`
- `test_logic.py::test_action_from_other_scene_is_rejected`
- `test_world.py::test_the_steward_stops_you_before_registration`
- `test_world.py::test_courts_and_back_corner_need_changed_clothes`

### A2 — An unlocked route
With the key, the player opens the shed (walks to the lock, the padlock drops)
and reaches the inside; the key stays in the inventory.

- `test_logic.py::test_open_shed_with_key_moves_inside_and_keeps_key`
- `test_story.py::test_the_shed_stays_open_after_unlocking`

### A3 — No duplicate collection
Talking to the groundskeeper again gives a hint, not a second key; after the
racket choice the other racket is gone.

- `test_logic.py::test_collect_key_adds_exactly_one_key`
- `test_logic.py::test_collect_key_twice_does_not_duplicate`
- `test_logic.py::test_talking_again_after_key_shows_hint_only`
- `test_logic.py::test_taking_a_second_racket_is_rejected`

### A4 — Resume correctly
Collect the key, choose a racket, stop and reopen the app: scene, items,
choice and the available routes are restored.

- `test_db.py::test_resume_restores_state_and_routes`
- `test_db.py::test_save_and_load_roundtrip`
- Manual check (see below)

### A5 — Two outcomes
Two valid paths from new games reach two different endings; at an ending,
story actions cannot change the game.

- `test_world.py::test_ending_a_is_reachable_through_all_screens`
- `test_world.py::test_ending_b_is_reachable_through_all_screens`
- `test_logic.py::test_no_story_actions_after_ending`
- `test_hotspots.py::test_no_hotspots_after_ending`
- `test_match.py::test_the_final_sets_the_ending`

### A6 — Restart safely
Cancel a restart: progress is kept. Confirm it: opening scene, empty
inventory, no decisions.

- `test_new_game.py::test_cancelled_restart_keeps_saved_progress`
- `test_new_game.py::test_confirmed_restart_replaces_saved_progress`
- `test_new_game.py::test_restart_from_an_ending_starts_a_playable_game`
- `test_logic.py::test_new_game_starts_at_start_scene_with_empty_progress`

## Beyond the BRD

| Feature | Spec | Tests |
| --- | --- | --- |
| Playable matches with a fixed story result (replay, blackout) | `specs/match-minigame.md` | `test_match.py`, story checks in `test_story.py` |
| Point-and-click scenes, walking, speech bubbles | `specs/point-and-click.md`, `specs/scene-polish.md` | `test_hotspots.py`, `test_dialogue.py`, `test_scene_polish.py` |
| Five outdoor screens | `specs/bigger-world.md` | `test_world.py` |
| Outfit choice | `specs/outfit-choice.md` | `test_outfits.py` |
| Moving sun | `specs/daylight.md` | `test_daylight.py` |
| Images and animations | `specs/visuals.md`, `specs/animations.md` | `test_images.py`, image checks in `test_story.py` |
| End scenes, description box | `specs/end-scene-polish.md` | caption and end-screen checks in `test_story.py` |

## Not covered by automated tests

The JavaScript in `components/` (scene view and tennis game) is checked by
playing in the browser, as part of every feature's manual check.

## Final check (2026-10-27, code as merged into `main`)

- `uv run pytest`: **96 passed**.
- App run without a browser (Streamlit AppTest), 8 of 8 checks passed:
  new game starts at the entrance; story path with the buttons to the Center
  Court in the black kit; "Start match" opens the match screen; **A4**: after
  restarting the app, scene ("Inside the shed"), items (key, Old Yonex) and the
  racket choice are restored; **A6**: "Cancel" keeps the game, "Yes, start over"
  restarts at the entrance with an empty inventory; **A5**: Ending A shows
  "Award ceremony" → "A stranger" and its title, Ending B shows
  "Award ceremony" → "The end" and its title.
- Browser check of the tennis game (round 2, pink kit, sun at the day's
  position, timing bar). Earlier browser checks per feature are listed in each
  pull request.
- Still to do by the author: one complete play-through by hand, including
  stopping and restarting the app in the middle.
