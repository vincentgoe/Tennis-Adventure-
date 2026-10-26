"""Game rules for Plot Twist.

Pure functions only: no Streamlit, no SQLite. The story content comes in as a
dict with the format of story.json, so nothing here knows scene or item names.

Rule functions never change the state they get. They return a new state, so a
rejected action can simply return the old one.
"""

import json
from dataclasses import dataclass
from pathlib import Path

STORY_PATH = Path(__file__).parent / "story.json"
DEFAULT_NOT_AVAILABLE = "You can't do that right now."


@dataclass
class GameState:
    scene: str
    items: list[str]
    flags: set[str]
    choices: dict[str, str]
    match_results: list[str]
    ending: str | None = None


def load_story(path=STORY_PATH):
    """Read the story content from a JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def new_game(story):
    """A fresh game at the start scene with no progress (PT R4)."""
    return GameState(
        scene=story["start_scene"],
        items=[],
        flags=set(),
        choices={},
        match_results=[],
        ending=None,
    )


# --- Conditions -------------------------------------------------------------


def conditions_met(state, conditions, story):
    """True if every condition in a `requires` / `when` block holds."""
    for key, value in conditions.items():
        if key == "items":
            ok = all(item in state.items for item in value)
        elif key == "not_items":
            ok = not any(item in state.items for item in value)
        elif key == "flags":
            ok = all(flag in state.flags for flag in value)
        elif key == "not_flags":
            ok = not any(flag in state.flags for flag in value)
        elif key == "choice_made":
            ok = value in state.choices
        elif key == "no_choice":
            ok = value not in state.choices
        elif key == "match_due":
            ok = match_due(state, story) == value
        else:
            raise ValueError(f"Unknown condition in story data: {key!r}")
        if not ok:
            return False
    return True


def first_matching_entry(entries, state, story):
    """The first entry whose `when` holds. An entry without `when` always
    matches, so it works as the default."""
    for entry in entries:
        if conditions_met(state, entry.get("when", {}), story):
            return entry
    return None


def first_matching_text(entries, state, story):
    """The text of the first matching entry."""
    entry = first_matching_entry(entries, state, story)
    return entry["text"] if entry is not None else None


# --- Matches ----------------------------------------------------------------


def _rounds(story):
    return story.get("matches", {}).get("rounds", [])


def next_round(state, story):
    """The next round to play, or None if all rounds are played."""
    rounds = _rounds(story)
    index = len(state.match_results)
    return rounds[index] if index < len(rounds) else None


def match_due(state, story):
    """True if a next round exists and its conditions are met."""
    if state.ending is not None:
        return False
    round_ = next_round(state, story)
    return round_ is not None and conditions_met(
        state, round_.get("requires", {}), story
    )


# --- Scenes and actions -----------------------------------------------------


def find_action(story, scene_id, action_id):
    """The action with this id in this scene, or None."""
    for action in story["scenes"][scene_id]["actions"]:
        if action["id"] == action_id:
            return action
    return None


def scene_text(state, story):
    """The description of the current scene, depending on the state (PT R3)."""
    return first_matching_text(story["scenes"][state.scene]["texts"], state, story)


def scene_image(state, story):
    """The image of the current scene. It comes from the same text entry as
    scene_text, so text and image always match. None if there is no image."""
    entry = first_matching_entry(story["scenes"][state.scene]["texts"], state, story)
    return entry.get("image") if entry is not None else None


def is_hidden(state, action, story):
    """True while the action's `hide_when` conditions hold. A hidden action is
    neither shown nor allowed, even if it has a blocked_text."""
    hide_when = action.get("hide_when")
    return hide_when is not None and conditions_met(state, hide_when, story)


def available_actions(state, story):
    """Ids of the actions to show: allowed ones, plus blocked ones that have a
    blocked_text (those are shown and explained). All others are hidden."""
    if state.ending is not None:
        return []
    visible = []
    for action in story["scenes"][state.scene]["actions"]:
        if is_hidden(state, action, story):
            continue
        allowed = conditions_met(state, action.get("requires", {}), story)
        if allowed or "blocked_text" in action:
            visible.append(action["id"])
    return visible


def scene_hotspots(state, story):
    """Clickable areas of the current scene image: one per visible action, in
    the same order as available_actions. Hidden actions are not clickable."""
    hotspots = []
    for action_id in available_actions(state, story):
        action = find_action(story, state.scene, action_id)
        spot = action.get("hotspot")
        if spot is None:
            continue
        hotspots.append(
            {
                "id": action_id,
                "label": action["label"],
                "x": spot["x"],
                "y": spot["y"],
                "w": spot["w"],
                "h": spot["h"],
                "marker": spot.get("marker"),
                "direction": spot.get("direction"),
                "name": spot.get("name"),
                "label_at": spot.get("label_at"),
                # Blocked-but-visible actions are clickable too. `allowed`
                # tells the component whether to play an animation first.
                "allowed": conditions_met(state, action.get("requires", {}), story),
                "walk_to": spot.get("walk_to"),
                "drop": spot.get("drop"),
            }
        )
    return hotspots


def player_image(state, story):
    """The player's sprite for this state (e.g. street clothes or tennis
    outfit), from the top-level `player` list in the story. None if unset."""
    entry = first_matching_entry(story.get("player", []), state, story)
    return entry["image"] if entry is not None else None


def _message_source(state, action_id, story):
    """The action itself if it is allowed, otherwise its matching blocked
    text entry. None if there is no such action or no blocked text."""
    if state.ending is not None:
        return None
    action = find_action(story, state.scene, action_id)
    if action is None or is_hidden(state, action, story):
        return None
    if conditions_met(state, action.get("requires", {}), story):
        return action
    return first_matching_entry(action.get("blocked_text", []), state, story)


def closeup_for(state, action_id, story):
    """The close-up image this action shows (e.g. a spinning racket), if the
    action is allowed in this state. None otherwise."""
    source = _message_source(state, action_id, story)
    action = find_action(story, state.scene, action_id) if source is not None else None
    if action is None or source is not action:
        return None
    return action.get("closeup")


def speaker_anchor(state, action_id, story):
    """Where the speech bubble for this action's message points to (above the
    speaker's head), or None if it is not spoken by someone in the picture.
    Call it with the state from *before* the action."""
    source = _message_source(state, action_id, story)
    return source.get("speaker_at") if source is not None else None


def speaker_for(state, action_id, story):
    """Who speaks the message this action would produce in this state.

    The action's own speaker if it is allowed, otherwise the speaker of the
    matching blocked text. None for objects, narration and unknown actions.
    Call it with the state from *before* the action.
    """
    source = _message_source(state, action_id, story)
    return source.get("speaker") if source is not None else None


def apply_action(state, action_id, story):
    """Try an action. Returns (new_state, accepted, message).

    Rejected actions return the unchanged state (PT R1).
    """
    not_available = story.get("ui_texts", {}).get(
        "not_available", DEFAULT_NOT_AVAILABLE
    )

    # 1. The game has not ended (PT05)
    if state.ending is not None:
        return state, False, not_available

    # 2. The action belongs to the current scene and is not hidden (PT R1)
    action = find_action(story, state.scene, action_id)
    if action is None or is_hidden(state, action, story):
        return state, False, not_available

    # 3. All prerequisites are met (PT R1)
    if not conditions_met(state, action.get("requires", {}), story):
        if "blocked_text" in action:
            message = first_matching_text(action["blocked_text"], state, story)
            return state, False, message or not_available
        return state, False, not_available

    new_state = _copy(state)
    message = _apply_effects(new_state, action.get("effects", {}), story)
    return new_state, True, message


# --- Effects ----------------------------------------------------------------


def _copy(state):
    return GameState(
        scene=state.scene,
        items=list(state.items),
        flags=set(state.flags),
        choices=dict(state.choices),
        match_results=list(state.match_results),
        ending=state.ending,
    )


def _apply_effects(state, effects, story):
    """Change `state` in place (it is already a copy). Returns the message."""
    message = None

    if "move_to" in effects:
        if effects["move_to"] not in story["scenes"]:
            raise ValueError(f"Unknown scene in story data: {effects['move_to']!r}")
        state.scene = effects["move_to"]

    if "add_item" in effects:
        item = effects["add_item"]
        if item not in story["items"]:
            raise ValueError(f"Unknown item in story data: {item!r}")
        if item not in state.items:  # never a duplicate (PT R2)
            state.items.append(item)

    state.flags.update(effects.get("set_flags", []))
    state.choices.update(effects.get("set_choice", {}))

    if "show_text" in effects:
        message = effects["show_text"]

    if effects.get("play_match"):
        message = _play_match(state, story)

    return message


def _play_match(state, story):
    """Stage 1: apply the fixed result of the next round."""
    round_ = next_round(state, story)
    outcome = None
    for candidate in round_["outcomes"]:
        if conditions_met(state, candidate.get("when", {}), story):
            outcome = candidate
            break
    if outcome is None:
        raise ValueError(f"No matching outcome in story data for {round_['name']!r}")

    state.match_results.append(outcome["result"])
    _apply_effects(state, outcome.get("effects", {}), story)

    # After the last round, the result decides the ending
    if len(state.match_results) == len(_rounds(story)):
        for ending_id, ending in story.get("endings", {}).items():
            if ending.get("when_final") == outcome["result"]:
                state.ending = ending_id
                break

    return outcome["text"]
