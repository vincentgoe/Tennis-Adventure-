# Spec: animations — Idle animations everywhere

Status: **agreed** (author approved on 2026-10-26).

## Why

The scenes look good but still feel static. Small idle animations make the
tournament feel alive, in the spirit of block-style games like Crossy Road.

## What

- **People** (including the player figure) bob gently up and down and blink
  now and then. Each person has a slightly different rhythm, so they do not
  move in sync.
- **Clouds** drift slowly, **trees** sway slightly. The existing animations
  stay: flags, the match indicator, dust in the shed, trophy and confetti.
- In the award ceremonies, the **crowd** bobs as well.
- Author feedback: everything except the people moves **faster**, so the
  scenes feel more dynamic. People keep their calm rhythm.
- More **life and detail** everywhere: grass tufts and a few swaying flowers
  on green areas, distant birds in the sky, a bouncing ball on the grounds'
  court, butterflies, a wall clock and a swaying plant in the office, a
  dripping pipe in the locker room, a swinging padlock on the shed, a spider in
  the shed, camera flashes at the ceremonies, a glowing sunset.
- Animations are part of the SVG files in `assets/` (SVG `<animate>`), so they
  need no JavaScript and also work in the plain image views (endings).
- Animations are subtle: at most a few units of movement in a 320 × 180 image.

## Out of scope

- Walking animations between screens.
- The bigger world with more screens (next feature).
- Any rule or story change.

## Done when

- [x] New test written first and green: every scene image, every ending image
      and the player sprite contain at least one animation.
- [x] All existing tests are still green and unchanged.
- [x] Manual check: people bob and blink, clouds drift, trees sway, and nothing
      jitters or looks distracting.
- [x] Committed on `animations`, pushed, reviewed, merged into `main`.
