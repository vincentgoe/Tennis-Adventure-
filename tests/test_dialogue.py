"""Tests for who speaks a message (specs/point-and-click.md, dialogue box)."""

from logic import speaker_for


def _story_with_speakers(story):
    """Mark the groundskeeper and the locked door's text as spoken lines."""
    talk = story["scenes"]["groundskeeper"]["actions"][0]
    assert talk["id"] == "talk_first"
    talk["speaker"] = "Groundskeeper"

    door = story["scenes"]["shed"]["actions"][0]
    assert door["id"] == "open_shed"
    door["blocked_text"] = [
        {"when": {"flags": ["guard_present"]}, "text": "Stop!", "speaker": "Guard"},
        {"text": "The door is locked."},
    ]
    return story


def test_allowed_action_uses_its_speaker(mini_story, make_state):
    story = _story_with_speakers(mini_story)
    state = make_state(scene="groundskeeper", flags={"knows_groundskeeper"})

    assert speaker_for(state, "talk_first", story) == "Groundskeeper"


def test_blocked_action_uses_the_speaker_of_its_blocked_text(mini_story, make_state):
    story = _story_with_speakers(mini_story)
    state = make_state(scene="shed", flags={"guard_present"})

    assert speaker_for(state, "open_shed", story) == "Guard"


def test_object_text_has_no_speaker(mini_story, make_state):
    """Objects and narration appear at once: no speaker."""
    story = _story_with_speakers(mini_story)

    locked = make_state(scene="shed")
    inspecting = make_state(scene="shed_inside", items=["key"])

    assert speaker_for(locked, "open_shed", story) is None
    assert speaker_for(inspecting, "inspect_yonex", story) is None


def test_unknown_action_has_no_speaker(mini_story, make_state):
    assert speaker_for(make_state(scene="grounds"), "fly_away", mini_story) is None
