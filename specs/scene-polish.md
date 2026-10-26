# Spec: scene-polish — Outfits, speech bubbles, unlock animation, livelier scenes

Status: **agreed** (author feedback list on 2026-10-26).

## Why

The author played the game and asked for a list of improvements so that the
world looks more believable and alive, and conversations feel like real
conversations.

## What

### Player outfit (state-dependent)

- Before changing in the locker room, the player wears **street clothes**
  (jeans, hoodie, street shoes). After changing: **tennis outfit** (sport
  shirt, shorts, socks, sport shoes, headband).
- Story content: `story.json` has a top-level `player` list with `when` /
  `image` entries. The first matching entry is used, like scene texts.
- New pure function `logic.player_image(state, story)`.

### Speech bubbles

- If a person in the picture speaks, the spoken part appears in a **speech
  bubble above that person**. Narration stays in the text box at the bottom.
- Texts that mix narration and speech are split at the double quotes and shown
  piece by piece: narration in the box (all at once), speech in the bubble
  (letter by letter). A click shows the next piece; the last click closes it.
- Story content: an action with a `speaker` may set `speaker_at` (`[x, y]`,
  above the person's head). A blocked text entry may set it too.
- Without `speaker_at` (e.g. the steward, who is not in the picture yet), the
  text box with the speaker's name is used as before.
- New pure function `logic.speaker_anchor(state, action_id, story)`: the
  `speaker_at` of the message this action would produce, or `None`.
- Object texts and interactions keep the text box.

### Unlock animation

- Clicking the shed door **with** the key: the player walks to the lock, the
  padlock falls down, then the inside of the shed appears.
- Clicking it **without** the key: no animation, the blocked message appears
  as before.
- Story content: a hotspot may set `walk_to` (`[x, y]`, where the player walks
  to) and `drop` (the id of an element in the scene image that falls down).
- `logic.scene_hotspots` also returns `allowed` for each hotspot, so the
  component plays the animation only for allowed actions. The rule itself stays
  in Python.

### Livelier and more believable scenes (art only)

- Grounds: two players rally on the court instead of a lone bouncing ball.
- Locker room: a bucket under the dripping pipe catches the drops.
- Office: the clock moves more slowly.
- Courts: a few spectators, a ball kid, a bench left and right of the umpire's
  chair. The umpire's chair looks realistic (ladder, seat) and the umpire sits
  on it. He **sleeps** with floating "z"s when no match is due, and is
  **awake** when a match is due.
- Groundskeeper: realistic proportions. The player and the groundskeeper have
  the same size, the court lies in the background.
- Shed: the Wilson Blade is dark green like the real one, the old Yonex light
  blue. Both rackets are smaller (realistic next to the player) and lean
  against the wall head down, handle up.

## Out of scope

- An opponent and a ball during matches: that is the minigame (stage 2).
- The bigger world with more screens (next feature).
- Walking animations for every click (only the unlock animation for now).
- Any rule change.

## Done when

- [ ] New tests written first and green:
  - `player_image` returns street clothes before and the tennis outfit after
    changing.
  - `scene_hotspots` marks the locked door as not allowed without the key and
    allowed with it, and passes `walk_to` / `drop`.
  - `speaker_anchor` returns the action's or blocked text's `speaker_at`, or
    `None`.
  - In `story.json`, every player image exists and is animated, and every
    action with a `speaker` has a `speaker_at` inside the image.
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: outfit changes in the locker room, speech bubbles above the
      woman and the groundskeeper, the unlock animation, the sleeping and awake
      umpire, and the new details in each scene.
- [ ] Committed on `scene-polish`, pushed, reviewed, merged into `main`.
