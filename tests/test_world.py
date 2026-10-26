"""Tests for the five outdoor screens (specs/bigger-world.md), on story.json."""

from logic import apply_action, available_actions, load_story, new_game, speaker_for

COMMON_START = [
    # Entrance -> office: register
    "go_office", "register", "leave_office",
    # Entrance -> main path -> locker room: change
    "go_main_path", "go_locker_room", "change", "leave_locker_room",
    # Main path -> Center Court: rounds 1 and 2
    "go_center_court", "start_match", "start_match",
    # Back to the office for the hint
    "leave_court", "back_to_entrance", "go_office", "ask_for_racket", "leave_office",
    # Court 2: the groundskeeper hands over the key
    "go_main_path", "go_center_court", "go_court_2", "talk_groundskeeper_first",
    # Back corner: unlock the shed
    "leave_court_2", "leave_court", "go_back_corner", "open_shed",
]
FINISH = ["leave_shed_inside", "leave_shed", "go_center_court", "start_match", "start_match"]


def play(story, action_ids):
    state = new_game(story)
    for action_id in action_ids:
        state, accepted, message = apply_action(state, action_id, story)
        assert accepted is True, f"{action_id} was rejected in {state.scene}: {message}"
    return state


def test_new_game_starts_at_the_entrance():
    assert new_game(load_story()).scene == "entrance"


def test_ending_a_is_reachable_through_all_screens():
    """BRD PT R4 / A5: every ending is reachable through valid play."""
    story = load_story()
    state = play(story, COMMON_START + ["take_yonex"] + FINISH)
    assert state.ending == "A"


def test_ending_b_is_reachable_through_all_screens():
    story = load_story()
    state = play(story, COMMON_START + ["take_wilson"] + FINISH)
    assert state.ending == "B"


def test_the_steward_stops_you_before_registration():
    """The main path is blocked until registration; the steward explains."""
    story = load_story()
    state = new_game(story)

    new_state, accepted, message = apply_action(state, "go_main_path", story)
    assert accepted is False
    assert new_state == state
    assert "register" in message
    assert speaker_for(state, "go_main_path", story) == "Steward"


def test_courts_and_back_corner_need_changed_clothes():
    story = load_story()
    state = play(story, ["go_office", "register", "leave_office", "go_main_path"])
    assert state.scene == "main_path"

    for action_id in ["go_center_court", "go_back_corner"]:
        assert action_id in available_actions(state, story)        # visible ...
        new_state, accepted, message = apply_action(state, action_id, story)
        assert accepted is False and new_state == state and message  # ... but blocked


def test_locker_room_closes_after_changing():
    story = load_story()
    state = play(story, ["go_office", "register", "leave_office", "go_main_path",
                         "go_locker_room", "change", "leave_locker_room"])

    new_state, accepted, message = apply_action(state, "go_locker_room", story)
    assert accepted is False and new_state == state
    assert "closed" in message


def test_old_screens_are_gone():
    """The single grounds picture and the separate groundskeeper scene are
    replaced by the new screens."""
    scenes = load_story()["scenes"]
    assert "grounds" not in scenes and "groundskeeper" not in scenes
    for scene_id in ["entrance", "main_path", "court", "court_2", "shed"]:
        assert scene_id in scenes
