# Spec: bigger-world — Five outdoor screens instead of one

Status: **agreed** (author approved the new texts and the test changes on
2026-10-27).

## Why

The whole tournament grounds are one picture with all destinations on it.
The author wants to click from screen to screen, so the world feels bigger and
exploring takes a little more effort.

## What

### Map

```
                       [Center Court] ──▶ [Court 2]
                             ▲              (groundskeeper)
                             │
 [Entrance] ──▶ [Main path] ─┘
  (office)      (locker room)
                     │
                     ▼
              [Back corner]
                (shed)
```

| Screen | Scene id | What is there | Blocked until |
| --- | --- | --- | --- |
| Entrance (start) | `entrance` | Gate, office building, the steward at the gate | – |
| Main path | `main_path` | Locker room building, fountain with two visitors, signpost | Registration (the steward stops you at the gate) |
| Center Court | `court` | Net with the match indicator, umpire, benches, spectators | Changing |
| Court 2 | `court_2` | Side court; the groundskeeper appears here after the hint | Changing (reached via the Center Court) |
| Back corner | `shed` | Path with trees and the shed | Changing |

- The indoor scenes stay as they are: office, locker room, inside the shed.
- The old screen `grounds` is replaced by `entrance` and `main_path`. The old
  scene `groundskeeper` becomes `court_2`.
- Exits are arrows at the edge pointing in the walking direction: ◀ ▶ ▲ ▼. A
  hotspot marker may set a `direction`. Exits show only the arrow, without a
  name (author feedback).

### Rules (unchanged in substance, only where they sit)

- Before registration, going from the entrance to the main path is blocked by
  the steward (existing text). The office is reachable at any time.
- The locker room is entered from the main path, after registration and only
  until the player has changed (existing texts).
- The Center Court and the back corner are reached from the main path after
  changing (existing texts "street clothes" and "Not now. Get changed first…").
- The groundskeeper stands on Court 2 and is visible and clickable only after
  the hint from the office. Talking to him happens there, without a scene
  change, before and after the racket choice (his three lines stay the same).
- The shed rules stay: locked without key, open after the first unlock.
- Matches are started at the net of the Center Court, as before.

### Texts

Existing approved texts are reused wherever they fit. New texts (drafts, need
approval) are marked **NEW** in the chat message that introduces this spec.

## Changes to existing tests

Two story tests in `tests/test_story.py` describe the old map and must be
corrected explicitly (not weakened), with reference to this spec:

- `test_groundskeeper_scene_is_reachable_before_the_racket_choice` and
  `test_groundskeeper_is_a_courtside_talk_after_the_racket_choice`: the
  groundskeeper is no longer reached from the Center Court but stands on
  Court 2. They become tests for Court 2: hidden before the hint, talkable
  without scene change before and after the racket choice.
- `test_the_shed_stays_open_after_unlocking`: leaving the shed now leads to the
  back corner (`shed`) instead of the old grounds; the test walks back via the
  main path. What it checks (the shed stays open) does not change.

## Out of scope

- The match minigame (stage 2).
- Free walking between screens (stage 3); screens are still changed by clicking.

## Done when

- [ ] New tests written first and green: every screen is reachable in the
      intended order from a new game, blocked exits show their existing texts,
      the groundskeeper is on Court 2 only after the hint, both endings are
      still reachable.
- [ ] The two corrected story tests are green; all other existing tests are
      unchanged and green.
- [ ] Manual check: play from the start to an ending through all five screens.
- [ ] Committed on `bigger-world`, pushed, reviewed, merged into `main`.
