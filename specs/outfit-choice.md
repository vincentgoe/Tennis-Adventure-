# Spec: outfit-choice — Pick one of three tennis outfits

Status: **agreed** (author request on 2026-10-27).

## Why

Changing in the locker room is a nice moment to let the player choose how
their character looks.

## What

- Clicking the lockers opens a menu with three choices:
  - the **white** kit (as before),
  - an all **black** kit,
  - a **pink** kit.
  All three have the same design (sport shirt with stripe, shorts, socks,
  shoes, headband); only the colours differ.
- Each choice is an action in `story.json`: it sets the flag `changed` (as
  before) and one outfit flag: `outfit_white`, `outfit_black` or
  `outfit_pink`. The existing action id `change` stays for the white kit.
  The text after changing stays the same.
- The chosen outfit is shown everywhere:
  - in the scenes (the `player` list in `story.json` picks the sprite),
  - in the tennis minigame (the app passes the outfit's colours),
  - on the ending pages: a page may have `images`, a list of `when` / `image`
    entries; the first matching one is used, otherwise its `image`.
- New pure function `logic.page_image(state, page, story)`.

### Preview (author request)

- Hovering an outfit in the locker room menu shows a large preview of the
  player wearing it, next to the menu.
- Story content: an action may set `preview` (an image in `assets/`).
  `logic.scene_hotspots` passes it on; the app adds the image itself.

## Out of scope

- Changing the outfit later (the locker room closes after changing, as before).

## Done when

- [ ] New tests written first and green:
  - `page_image` returns the matching variant, or the default image.
  - `player_image` returns the black / pink sprite after choosing them.
  - `scene_hotspots` passes an action's `preview`; every outfit action has
    an existing preview image.
  - In `story.json`, the three outfit actions exist, each sets `changed`
    and exactly one outfit flag, and every page image variant exists.
- [ ] All existing tests are still green and unchanged.
- [ ] Manual check: choose each outfit once and see it in the scenes, the
      match and the ending.
- [ ] Committed on `outfit-choice`, pushed, reviewed, merged into `main`.
