# Spec: end-scene-polish — Description box, ceremony ground, slower stranger

Status: **agreed** (author request on 2026-10-27).

## Why

In the evening ceremony, sky and ground look too similar. Descriptions of the
surroundings should sit in the picture instead of below it, and the last scene
should give the player time to read.

## What

- **Description box:** texts that describe the surroundings or the situation
  (a scene's description, the text of an ending page) are shown in a small,
  transparent black box in the **top left corner** of the picture, in the same
  style as the Center Court box. The box does not block clicks. Conversations
  and object texts keep their places.
- **Ending pages** are shown in the scene view (no hotspots), so their
  animation starts when the page appears and the description box can be shown
  on top. The result text of the final appears in the centered box on the
  first page.
- **Timed captions:** an ending page may set `captions`, a list of
  `{at, text}` (seconds since the page appeared). The box shows the latest
  caption that has started. Used in the stranger scene (texts given by the
  author):
  - at 0 s: "As the crowd drifts away, a stranger in a cap walks up to you."
  - after the racket is handed over: "He turns it slowly in his hands, his
    thumb resting on the faded letters on the frame. A smile spreads across
    his face."
  - His two lines stay in his speech bubbles; the caption disappears when
    "THE END" fades in.
- **Stranger scene timing:** about 4 seconds to read before the stranger
  enters; he walks more slowly (about 4.5 s instead of 2.5 s).
- **Award ceremony ground:** a meadow with a square of stone tiles on which
  the podium stands (evening sky stays).

### End screen for Ending B (author request)

- After the award ceremony page, Ending B gets a last page "The end": the
  empty Center Court at sunset, the player sitting alone on the players'
  bench with the Wilson next to them; after a few seconds "THE END" fades in
  (like Ending A). The page has no description text. Shown in the chosen
  outfit.

## Done when

- [x] New tests written first and green: the stranger page has the two
      captions above, in order, the first at 0 s; Ending B ends with an end
      screen page.
- [x] All existing tests are still green and unchanged.
- [x] Manual check: description boxes in scenes and endings, the ceremony
      ground, and the stranger scene timing and captions.
- [ ] Committed on `end-scene-polish`, pushed, reviewed, merged into `main`.
