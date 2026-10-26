"""Tests for clickable hotspots (specs/point-and-click.md)."""

from logic import scene_hotspots


def _hotspot_ids(state, story):
    return [hotspot["id"] for hotspot in scene_hotspots(state, story)]


def _add_hotspots(story):
    """Give every action in the mini story a hotspot (test data only)."""
    for scene in story["scenes"].values():
        for i, action in enumerate(scene["actions"]):
            action["hotspot"] = {"x": 10 + i * 40, "y": 20, "w": 30, "h": 30}
    return story


def test_hotspots_only_for_visible_actions(mini_story, make_state):
    """Hidden actions have no hotspot: no groundskeeper before the hint."""
    story = _add_hotspots(mini_story)

    before_hint = make_state(scene="court")
    after_hint = make_state(scene="court", flags={"knows_groundskeeper"})

    assert "go_groundskeeper" not in _hotspot_ids(before_hint, story)
    assert "go_groundskeeper" in _hotspot_ids(after_hint, story)


def test_blocked_action_with_text_has_a_hotspot(mini_story, make_state):
    """The locked door is clickable, so clicking it can explain why."""
    story = _add_hotspots(mini_story)
    state = make_state(scene="shed")

    assert "open_shed" in _hotspot_ids(state, story)


def test_hotspot_carries_label_and_rectangle(mini_story, make_state):
    """Each hotspot has what the component needs to draw and report it."""
    story = _add_hotspots(mini_story)
    state = make_state(scene="shed")

    door = next(h for h in scene_hotspots(state, story) if h["id"] == "open_shed")

    assert door["label"] == "Open the door"
    assert (door["x"], door["y"], door["w"], door["h"]) == (10, 20, 30, 30)


def test_hotspots_match_visible_actions(mini_story, make_state):
    """Hotspots and buttons always offer the same actions, in the same order."""
    from logic import available_actions

    story = _add_hotspots(mini_story)
    state = make_state(scene="shed_inside", items=["key"])

    assert _hotspot_ids(state, story) == available_actions(state, story)


def test_no_hotspots_after_ending(mini_story, make_state):
    """PT05: once an ending is reached, nothing is clickable."""
    story = _add_hotspots(mini_story)
    state = make_state(scene="shed", items=["key"], ending="A")

    assert scene_hotspots(state, story) == []


def test_hotspot_carries_name_and_label_position(mini_story, make_state):
    """The label above a hotspot comes from its name (author feedback:
    labels instead of borders and dots)."""
    door = mini_story["scenes"]["shed"]["actions"][0]
    door["hotspot"] = {"x": 10, "y": 20, "w": 30, "h": 30,
                       "name": "Shed door", "label_at": [25, 15]}
    state = make_state(scene="shed")

    spot = next(h for h in scene_hotspots(state, mini_story) if h["id"] == "open_shed")

    assert spot["name"] == "Shed door"
    assert spot["label_at"] == [25, 15]
