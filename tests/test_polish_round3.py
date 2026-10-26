"""Tests for hide_when and close-ups (specs/scene-polish.md, third round)."""

from logic import apply_action, available_actions, closeup_for


def _shed_with_hide_when(story):
    """The locked door disappears once the shed is unlocked."""
    door = story["scenes"]["shed"]["actions"][0]
    assert door["id"] == "open_shed"
    door["hide_when"] = {"flags": ["shed_unlocked"]}
    door["effects"]["set_flags"] = ["shed_unlocked"]
    story["scenes"]["shed"]["actions"].insert(1, {
        "id": "enter_shed",
        "label": "Go inside",
        "requires": {"flags": ["shed_unlocked"]},
        "effects": {"move_to": "shed_inside"},
    })
    return story


def test_hide_when_hides_an_action_even_with_blocked_text(mini_story, make_state):
    story = _shed_with_hide_when(mini_story)
    state = make_state(scene="shed", flags={"shed_unlocked"})

    actions = available_actions(state, story)
    assert "open_shed" not in actions
    assert "enter_shed" in actions


def test_hidden_action_is_rejected_without_changes(mini_story, make_state):
    story = _shed_with_hide_when(mini_story)
    state = make_state(scene="shed", items=["key"], flags={"shed_unlocked"})

    new_state, accepted, message = apply_action(state, "open_shed", story)
    assert accepted is False
    assert new_state == state
    assert message == "Not available."


def test_first_unlock_sets_the_flag(mini_story, make_state):
    story = _shed_with_hide_when(mini_story)
    state = make_state(scene="shed", items=["key"])

    assert "open_shed" in available_actions(state, story)
    new_state, accepted, _ = apply_action(state, "open_shed", story)
    assert accepted is True
    assert "shed_unlocked" in new_state.flags
    assert new_state.scene == "shed_inside"


def test_hide_when_does_not_change_actions_without_it(mini_story, make_state):
    """Existing behaviour stays: the locked door is still visible and blocked."""
    state = make_state(scene="shed")
    assert "open_shed" in available_actions(state, mini_story)


def test_closeup_for_an_allowed_action(mini_story, make_state):
    inspect = mini_story["scenes"]["shed_inside"]["actions"][0]
    assert inspect["id"] == "inspect_yonex"
    inspect["closeup"] = "closeups/yonex.svg"

    allowed = make_state(scene="shed_inside", items=["key"])
    after_choice = make_state(scene="shed_inside", items=["key", "yonex"], choices={"racket": "yonex"})

    assert closeup_for(allowed, "inspect_yonex", mini_story) == "closeups/yonex.svg"
    assert closeup_for(after_choice, "inspect_yonex", mini_story) is None
    assert closeup_for(allowed, "take_yonex", mini_story) is None
