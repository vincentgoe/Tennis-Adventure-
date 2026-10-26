"""Rule tests for logic.py, based on specs/first-feature.md.

All tests use the small `mini_story` fixture from conftest.py, not story.json.
"""

from logic import GameState, apply_action, available_actions, new_game


# --- New game ---------------------------------------------------------------


def test_new_game_starts_at_start_scene_with_empty_progress(mini_story):
    """Spec "App start": a new game starts at the start scene with no progress."""
    state = new_game(mini_story)

    assert state == GameState(
        scene="grounds",
        items=[],
        flags=set(),
        choices={},
        match_results=[],
        ending=None,
    )


# --- Locked shed (cases 2 and 3) --------------------------------------------


def test_open_shed_without_key_is_rejected(mini_story):
    """BRD A1 / PT R1: a blocked action does not move the player or change
    their inventory, and the player is told why."""
    # Given: the player stands at the shed without the key
    state = GameState(
        scene="shed",
        items=[],
        flags=set(),
        choices={},
        match_results=[],
        ending=None,
    )

    # When: they try to open the door
    new_state, accepted, message = apply_action(state, "open_shed", mini_story)

    # Then: the action is rejected ...
    assert accepted is False
    # ... the player is still at the shed with an empty inventory ...
    assert new_state.scene == "shed"
    assert new_state.items == []
    # ... nothing else changed either ...
    assert new_state == state
    # ... and the blocked text explains why
    assert message == "The door is locked."


def test_open_shed_with_key_moves_inside_and_keeps_key(mini_story, make_state):
    """BRD A2 / PT R2: with the key, the player reaches the intended scene and
    the key stays in the inventory."""
    state = make_state(scene="shed", items=["key"])

    new_state, accepted, _ = apply_action(state, "open_shed", mini_story)

    assert accepted is True
    assert new_state.scene == "shed_inside"
    assert new_state.items == ["key"]


def test_blocked_action_with_text_is_visible(mini_story, make_state):
    """PT04: blocked actions with a blocked_text are shown, not hidden."""
    state = make_state(scene="shed")

    assert "open_shed" in available_actions(state, mini_story)


# --- Collecting the key (case 1) --------------------------------------------


def test_collect_key_adds_exactly_one_key(mini_story, make_state):
    """Spec case 1: talking to the groundskeeper hands over the key."""
    state = make_state(scene="groundskeeper", flags={"knows_groundskeeper"})

    new_state, accepted, message = apply_action(state, "talk_first", mini_story)

    assert accepted is True
    assert new_state.items == ["key"]
    assert new_state.scene == "groundskeeper"
    assert message == "Here is the key."


def test_collect_key_twice_does_not_duplicate(mini_story, make_state):
    """BRD A3 / PT R2 / PT R3: the key can be collected only once."""
    state = make_state(
        scene="groundskeeper", items=["key"], flags={"knows_groundskeeper"}
    )

    # The collect action is no longer offered ...
    assert "talk_first" not in available_actions(state, mini_story)

    # ... and triggering it anyway is rejected without changing anything
    new_state, accepted, message = apply_action(state, "talk_first", mini_story)

    assert accepted is False
    assert new_state.items == ["key"]
    assert new_state == state
    assert message == "Not available."


def test_talking_again_after_key_shows_hint_only(mini_story, make_state):
    """PT R3: the revisited scene reflects the change, without a second key."""
    state = make_state(
        scene="groundskeeper", items=["key"], flags={"knows_groundskeeper"}
    )

    new_state, accepted, message = apply_action(state, "talk_has_key", mini_story)

    assert accepted is True
    assert new_state == state
    assert message == "Check the shed."


# --- Racket choice (case 4) -------------------------------------------------


def test_take_racket_sets_item_and_choice(mini_story, make_state):
    """Spec case 4: taking a racket adds the item and records the choice."""
    state = make_state(scene="shed_inside", items=["key"])

    new_state, accepted, message = apply_action(state, "take_yonex", mini_story)

    assert accepted is True
    assert new_state.items == ["key", "yonex"]
    assert new_state.choices == {"racket": "yonex"}
    assert new_state.scene == "shed_inside"
    assert message == "Hurry!"


def test_after_choice_rackets_are_gone(mini_story, make_state):
    """Spec case 4: after the choice, inspect and take are hidden."""
    state = make_state(
        scene="shed_inside", items=["key", "yonex"], choices={"racket": "yonex"}
    )

    assert available_actions(state, mini_story) == ["leave_shed_inside"]


def test_taking_a_second_racket_is_rejected(mini_story, make_state):
    """Story decision 12: the choice is final."""
    state = make_state(
        scene="shed_inside", items=["key", "yonex"], choices={"racket": "yonex"}
    )

    new_state, accepted, _ = apply_action(state, "take_yonex", mini_story)

    assert accepted is False
    assert new_state == state


def test_inspect_shows_text_and_changes_nothing(mini_story, make_state):
    """Story decision 13: inspecting is optional and not remembered."""
    state = make_state(scene="shed_inside", items=["key"])

    new_state, accepted, message = apply_action(state, "inspect_yonex", mini_story)

    assert accepted is True
    assert new_state == state
    assert message == "Roger F."


# --- General rules (PT R1) --------------------------------------------------


def test_action_from_other_scene_is_rejected(mini_story, make_state):
    """PT R1: an action is allowed only in its own scene."""
    state = make_state(scene="grounds", items=["key"])

    new_state, accepted, _ = apply_action(state, "open_shed", mini_story)

    assert accepted is False
    assert new_state == state


def test_unknown_action_is_rejected(mini_story, make_state):
    """Spec decision: unknown actions are rejected without changes."""
    state = make_state(scene="grounds")

    new_state, accepted, message = apply_action(state, "fly_away", mini_story)

    assert accepted is False
    assert new_state == state
    assert message == "Not available."


def test_hidden_action_is_not_visible_until_condition_is_met(mini_story, make_state):
    """Story decision 15: the groundskeeper appears only after the hint."""
    before_hint = make_state(scene="court")
    after_hint = make_state(scene="court", flags={"knows_groundskeeper"})

    assert "go_groundskeeper" not in available_actions(before_hint, mini_story)
    assert "go_groundskeeper" in available_actions(after_hint, mini_story)


def test_no_story_actions_after_ending(mini_story, make_state):
    """Spec central rule / PT05: once an ending is reached, actions stop."""
    state = make_state(scene="shed", items=["key"], ending="A")

    new_state, accepted, _ = apply_action(state, "open_shed", mini_story)

    assert accepted is False
    assert new_state == state
    assert available_actions(state, mini_story) == []


# --- Matches (case 6) -------------------------------------------------------


def test_start_match_applies_fixed_result(mini_story, make_state):
    """Spec case 6: "Start match" applies the fixed result of the next round."""
    state = make_state(scene="court")

    new_state, accepted, message = apply_action(state, "start_match", mini_story)

    assert accepted is True
    assert new_state.match_results == ["win"]
    assert new_state.scene == "court"
    assert message == "Round 1 won."


def test_second_match_is_lost_and_sets_needs_racket(mini_story, make_state):
    """Spec case 6: after round 2 the flag needs_racket is set."""
    state = make_state(scene="court", match_results=["win"])

    new_state, accepted, _ = apply_action(state, "start_match", mini_story)

    assert accepted is True
    assert new_state.match_results == ["win", "loss"]
    assert "needs_racket" in new_state.flags


def test_no_match_due_without_racket(mini_story, make_state):
    """Spec case 6: no further match is due until a racket has been chosen."""
    state = make_state(
        scene="court", flags={"needs_racket"}, match_results=["win", "loss"]
    )

    assert "start_match" not in available_actions(state, mini_story)

    new_state, accepted, _ = apply_action(state, "start_match", mini_story)

    assert accepted is False
    assert new_state == state


def test_match_due_again_after_racket_choice(mini_story, make_state):
    """Spec case 6: the next match is due once a racket has been chosen."""
    state = make_state(
        scene="court",
        items=["key", "yonex"],
        flags={"needs_racket"},
        choices={"racket": "yonex"},
        match_results=["win", "loss"],
    )

    assert "start_match" in available_actions(state, mini_story)
