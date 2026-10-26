# Spec: first-feature — Key, locked shed, racket choice, resume

Status: **agreed** (open questions Q1–Q4 decided, see the end of this file).

## Why

This is the core loop of the BRD: an item unlocks a path, a decision is
remembered, and progress survives restarting the app.

- PT03: at least one item unlocks an action. Collecting twice creates no duplicate.
- PT04: a remembered decision affects later play. Blocked actions are explained.
- PT R1: a blocked action does not move the player or change the inventory.
- PT R2: the key is not consumed when used.
- Scenarios **A1** (locked route), **A2** (unlocked route), **A3** (no duplicate
  collection), **A4** (resume correctly).

In this story: the groundskeeper hands over the **key**, the key unlocks the
**shed**, and inside the player makes the **racket choice** (the consequential
decision).

## What

### Game state

A game state consists of:

| Field          | Example                                   |
| -------------- | ----------------------------------------- |
| current scene  | `"shed"`                                  |
| items          | `["key"]`                                 |
| flags          | `["registered", "changed", "needs_racket", "knows_groundskeeper"]` |
| choices        | `{}` or `{"racket": "yonex"}`             |
| match results  | `["win", "loss"]`                         |

### Starting point for this feature

All cases below start from the state a player has after round 2 and the second
visit to the tournament office:

- scene: `court`
- items: none
- flags: `registered`, `changed`, `needs_racket`, `knows_groundskeeper`
- choices: none
- match results: `win`, `loss`

### Case 1: collect the key (allowed)

| | Before | After |
|---|---|---|
| Scene | `groundskeeper` | `groundskeeper` |
| Items | none | `key` |
| Visible result | — | the groundskeeper's key text |

Talking to him again gives the "spare rackets in the shed" text. The inventory
still contains **one** key (A3).

### Case 2: open the shed without the key (rejected, A1)

| | Before | After |
|---|---|---|
| Scene | `shed` | `shed` (unchanged) |
| Items | none | none (unchanged) |
| Visible result | — | "You pull at the door, but the padlock won't budge. You'll need a key." |

The "Open the door" action is **visible** but rejected. Nothing is saved,
because nothing changed.

### Case 3: open the shed with the key (allowed, A2)

| | Before | After |
|---|---|---|
| Scene | `shed` | `shed_inside` |
| Items | `key` | `key` (not consumed) |
| Visible result | — | the "lock clicks open" text |

### Case 4: take a racket (the consequential choice)

| | Before | After |
|---|---|---|
| Scene | `shed_inside` | `shed_inside` |
| Items | `key` | `key`, `yonex` |
| Choices | none | `racket = yonex` |
| Visible result | — | the "hurry back to the courts" text |

After the choice, the inspect and take actions are hidden, and the shed shows
the "empty" text. The same applies to `wilson`. Inspecting is allowed before the
choice, shows a text, and changes nothing else.

### Case 5: resume after restarting the app (A4)

1. Play to case 4 (key collected, Yonex taken).
2. Stop the app and start it again.
3. The game resumes with the **same** scene, items (`key`, `yonex`), choice
   (`racket = yonex`), flags, and match results.
4. The **same routes** are available as before stopping. In `shed_inside`: only
   "Leave the shed". At `shed`: "Open the door" is allowed. At the
   groundskeeper: the "did you find a racket?" text.

Progress is saved **after each accepted action**. Rejected actions do not
change the saved data.

### Case 6: start a match (stage 1, fixed result)

Needed so the manual check can follow the real path to the key (Q1).

| | Before | After |
|---|---|---|
| Scene | `court` | `court` |
| Match results | none | `win` |
| Flags | `registered`, `changed` | unchanged |
| Visible result | — | the round 1 text |

- "Start match" is offered only when a match is due (`match_due`): the next
  round exists and its `requires` are met. Otherwise it is hidden.
- The result is the first matching outcome of the next round in `story.json`.
  No minigame yet.
- After round 2 (`loss`), the flag `needs_racket` is set, and no further match
  is due until a racket has been chosen.

### App start (Q2)

- If a saved game exists, it is loaded automatically.
- If not, a new game starts in `grounds` with an empty inventory, no flags, no
  choices, and no match results.

### Inventory (Q4)

The inventory is **always visible** (e.g. in the sidebar) and shows each item's
name from `story.json`.

## Out of scope

- The match minigame (stage 2) and the world map (stage 3).
- Replay match / give up.
- Endings and the award ceremony (A5).
- The "New game" / "Resume" choice with confirmation (A6). This is a separate
  later feature (Q3).
- Story texts are not tested word for word.

## Done when

- [ ] Tests for cases 1–6 exist, were reviewed, and are green with `uv run pytest`.
- [ ] Rule tests use a small test story and do not depend on `story.json`.
- [ ] Persistence tests use a temporary database (`tmp_path`).
- [ ] Manual check: start the app, play from the start to the racket choice,
      stop the app (Ctrl+C), start it again, and see the same state and routes.
- [ ] Committed on `first-feature`, pushed, reviewed, merged into `main`.

## Decisions

- **Q1 – How far must the app work for the manual check?** The real path to
  the key must be playable. Registering, changing and moving use the same
  data-driven mechanism as the shed. "Start match" with a fixed result is part
  of this feature (case 6).
- **Q2 – App start:** a saved game is loaded automatically. Otherwise a new
  game starts.
- **Q3 – A6:** a separate, later feature.
- **Q4 – Inventory:** always visible.
