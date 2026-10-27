# Spec: match-minigame — Playable tennis matches (stage 2)

Status: **agreed** (author approved the "timing rally" proposal on 2026-10-27:
keyboard and mouse, one game to 4 points, aiming by timing).

## Why

Until now, "Start match" applies a fixed result. The author wants matches that
are fun to play and need some skill, while the story's fixed results stay
intact (see "Match system" in `docs/story.md`).

## What

### The game

- Top-down view from behind the baseline, block style like the scenes. The
  player is at the bottom, the opponent at the top.
- The ball flies in an arc; its **shadow** shows where it will land.
- **Move:** ← / → keys, or move the mouse over the court.
- **Swing:** space bar or mouse click, when the ball reaches the player.
  - **Perfect** timing: fast, sharp shot (screen shake, sparkle, "PERFECT!").
  - **Good** timing: normal shot.
  - **Miss** (too early, too late or too far away): the point is lost.
- **Aiming by timing:** an early hit goes to the left, a late hit to the right,
  a hit right on time goes to the middle.
- **Opponent:** runs to the ball with limited speed and a short reaction time,
  sometimes makes errors. The player wins a point when the opponent cannot
  reach the ball or makes an error.
- **Scoring:** one game with real tennis counting (15, 30, 40, deuce,
  advantage, game). The score is shown in the pixel font.
- A start screen explains the controls; clicking it starts the game (and gives
  the game keyboard focus).

### Version 2 (author feedback after the first play test)

The author did not hit a single ball and found it unclear when to swing.
Changes, inspired by timing meters in sports games (TopSpin 2K25's shot meter,
baseball and golf timing bars):

- **Keyboard only:** ← / → to move, space to swing. The mouse only starts the
  game (mouse movement caused accidental mistakes).
- **Timing bar** at the bottom: red | yellow | green | yellow | red. A line
  sweeps quickly from side to side. The bar lights up once the ball has
  bounced; from then until shortly after the contact point, space counts:
  - **green:** perfect cross-court shot (fast, to the side away from the
    opponent),
  - **yellow:** solid, safe ball over the net,
  - **red:** the ball goes out, the point is lost.
- **Direction indicator:** at the bounce point an arrow shows where the ball
  jumps after the bounce, and a marker on the player's line shows where to
  stand. The player must stand on that line (within reach), otherwise the
  swing misses ("TOO FAR").
- **Position matters** (like TopSpin): the closer the player stands to the
  marker, the slower the line sweeps.
- Aiming by early/late timing is replaced by the bar zones.
- Easier overall: more time after the bounce, larger reach and wider zones,
  especially in round 1.
- The racket is held by the grip, head up and out.
- New settings per round: `bar_speed` (sweeps per second), `green` and
  `yellow` (zone widths as fractions of the bar). `window` is the time after
  the contact point during which a swing still counts.

### Difficulty and story events (story content)

Each match outcome in `story.json` gets a `game` block with the settings for
that round: opponent speed, reaction time and error rate, ball speed, timing
window, reach, and optionally `tutorial`, `event` and an "overpowered" phase.

| Round | Feel |
| --- | --- |
| 1 (original racket) | Slow opponent, large timing window, tutorial hints |
| 2 | Very fast opponent; the **string snaps** on the last point (event `string_break`): the ball drops into the net and the match is lost |
| 3, Wilson | Normal |
| Final, Wilson | Extremely hard |
| 3, Yonex | Hard for the first points, then the racket becomes overpowered (big sweet spot, hard shots) |
| Final, Yonex | Overpowered: almost impossible to lose |

### Fixed results stay fixed

The game reports only `win` or `loss`. `logic.py` decides what it means:

| Required by the story | Reported | Result |
| --- | --- | --- |
| win | win | the round is won, the story moves on |
| loss | loss | the round is lost, the story moves on |
| loss | win | **blackout:** the round counts as lost; the blackout text is shown (the game shows the ball hitting the player's head and the screen going dark first) |
| win | loss | nothing changes; the player chooses **Replay match** or **Give up** (Give up asks for confirmation and starts a new game) |

- New pure functions in `logic.py`:
  - `match_setup(state, story)`: the next round's name, its required result
    and its `game` settings, or `None` if no match is due.
  - `apply_match_result(state, reported, story)`: returns
    `(new_state, status, message)` with `status` one of `advanced`,
    `blackout`, `replay`, `rejected`.
- Saving: only accepted results are saved (`advanced`, `blackout`). Points
  within a match are not saved (decision 22).

### App

- Clicking the net ("Start match") walks the player to the net and opens the
  match screen instead of applying a fixed result.
- After the match, the result text appears in the text box of the Center Court
  scene, or the ending pages start after the final.
- The game is a separate small component in `components/match/` (one HTML file
  with plain JavaScript and a canvas, no build step, no extra package).

## Out of scope

- Sound.
- Serving by the player (the opponent serves every point).
- Different shot types (lob, slice) — possible later polish.

## Done when

- [ ] New tests written first and green:
  - `match_setup` returns the next round's settings and required result, and
    `None` when no match is due.
  - `apply_match_result` covers all four rows of the table above, keeps the
    state unchanged for `replay` and `rejected`, and sets the ending after the
    final.
  - In `story.json`, every match outcome has a valid `game` block, round 2 has
    the `string_break` event.
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: play round 1 with keyboard and with mouse, lose round 2 by
      the snapping string, win round 3 and the final with the Yonex; try losing
      a must-win round (replay / give up) and winning a must-lose round
      (blackout).
- [ ] Committed on `match-minigame`, pushed, reviewed, merged into `main`.
