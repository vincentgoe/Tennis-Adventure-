# Spec: daylight — The sun moves with the tournament day

Status: **agreed** (author request on 2026-10-27).

## Why

The tournament takes a whole day. A sun that moves between the matches makes
time visible, and the award ceremony after the final happens in the evening.

## What

- **Day progress** = matches played / number of rounds (0 before round 1,
  1 after the final). New pure function `logic.day_progress(state, story)`.
- **Outdoor scenes** (those with a `sky` block in `story.json`, giving the
  `horizon`) show a sun. Its position depends only on the day progress: before
  round 1 it is high on the left, after each match it moves a step to the
  right. The sky gets a little warmer with the day. The sun does not move
  within a scene.
- The sun is drawn just above the sky, behind buildings, people and clouds.
- **Tennis minigame:** the sun stands in the sky above the stands at the same
  position.
- **Award ceremony** (after the final, win or loss): evening red sky with a low
  red sun behind the stands.

## Out of scope

- A sun moving in real time.

## Done when

- [x] New tests written first and green:
  - `day_progress` is 0 at the start, grows with each match and is 1 after the
    final.
  - Every scene with a `sky` block has a horizon inside the image, and its
    images contain the sky the sun is drawn behind.
- [x] All existing tests are still green and unchanged.
- [x] Manual check: the sun moves right after each match; the ceremony is in
      evening light.
- [ ] Committed on `daylight`, pushed, reviewed, merged into `main`.
