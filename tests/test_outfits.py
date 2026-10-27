"""Tests for the outfit choice (specs/outfit-choice.md)."""

from logic import load_story, page_image, player_image

OUTFIT_FLAGS = {"outfit_white", "outfit_black", "outfit_pink"}


def test_page_image_uses_the_matching_variant(make_state, mini_story):
    page = {"name": "Ceremony", "text": "...", "image": "endings/win.svg",
            "images": [{"when": {"flags": ["outfit_pink"]}, "image": "endings/win_pink.svg"}]}

    assert page_image(make_state(flags={"outfit_pink"}), page, mini_story) == "endings/win_pink.svg"
    assert page_image(make_state(flags={"outfit_white"}), page, mini_story) == "endings/win.svg"


def test_page_image_without_variants(make_state, mini_story):
    page = {"name": "Ceremony", "text": "...", "image": "endings/win.svg"}
    assert page_image(make_state(), page, mini_story) == "endings/win.svg"


def test_player_wears_the_chosen_outfit(make_state):
    story = load_story()
    black = player_image(make_state(flags={"changed", "outfit_black"}), story)
    pink = player_image(make_state(flags={"changed", "outfit_pink"}), story)
    white = player_image(make_state(flags={"changed", "outfit_white"}), story)
    street = player_image(make_state(), story)

    assert len({black, pink, white, street}) == 4
    assert "black" in black and "pink" in pink


def test_three_outfit_actions_in_the_locker_room():
    story = load_story()
    actions = {a["id"]: a for a in story["scenes"]["locker_room"]["actions"]}
    choices = [a for a in actions.values() if "changed" in a.get("effects", {}).get("set_flags", [])]

    assert len(choices) == 3
    assert "change" in actions                       # the white kit keeps its old id
    for action in choices:
        flags = set(action["effects"]["set_flags"])
        assert len(flags & OUTFIT_FLAGS) == 1
        assert action["requires"] == {"not_flags": ["changed"]}
