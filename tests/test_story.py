"""Checks for the real story.json (specs/visuals.md).

These tests use the real story on purpose: they catch missing images when
scenes, items or endings are added later.
"""

from pathlib import Path

from logic import load_story

ASSETS = Path(__file__).parent.parent / "assets"


def _referenced_images(story):
    for scene in story["scenes"].values():
        for entry in scene["texts"]:
            yield entry.get("image")
    for item in story["items"].values():
        yield item.get("image")
    for ending in story["endings"].values():
        for page in ending["pages"]:
            yield page.get("image")


def test_every_scene_text_item_and_ending_page_has_an_image():
    story = load_story()
    missing = [image for image in _referenced_images(story) if image is None]
    assert missing == []


IMAGE_W, IMAGE_H = 320, 180


def _inside_image(x, y, w=0, h=0):
    return 0 <= x and 0 <= y and x + w <= IMAGE_W and y + h <= IMAGE_H


def test_every_action_has_a_hotspot_inside_the_image():
    """specs/point-and-click.md: every action can be clicked in the image."""
    story = load_story()
    problems = []
    for scene_id, scene in story["scenes"].items():
        for action in scene["actions"]:
            spot = action.get("hotspot")
            if spot is None or not _inside_image(spot["x"], spot["y"], spot["w"], spot["h"]):
                problems.append(f"{scene_id}.{action['id']}")
    assert problems == []


def test_every_non_exit_hotspot_has_a_name():
    """specs/point-and-click.md: names are shown as labels in the image."""
    story = load_story()
    problems = []
    for scene_id, scene in story["scenes"].items():
        for action in scene["actions"]:
            spot = action.get("hotspot", {})
            if spot.get("marker") != "exit" and not spot.get("name"):
                problems.append(f"{scene_id}.{action['id']}")
    assert problems == []


def test_every_scene_has_a_player_position_inside_the_image():
    """specs/point-and-click.md: the player stands in every scene."""
    story = load_story()
    problems = []
    for scene_id, scene in story["scenes"].items():
        player = scene.get("player")
        if player is None or not _inside_image(player["x"], player["y"]):
            problems.append(scene_id)
    assert problems == []


def test_every_referenced_image_exists():
    story = load_story()
    images = [image for image in _referenced_images(story) if image is not None]
    missing = [image for image in images if not (ASSETS / image).is_file()]
    assert missing == []


def test_every_scene_ending_and_player_image_is_animated():
    """specs/animations.md: everything moves a little."""
    story = load_story()
    images = {entry["image"] for scene in story["scenes"].values() for entry in scene["texts"]}
    images |= {page["image"] for ending in story["endings"].values() for page in ending["pages"]}
    images.add("sprites/player.svg")
    still = [image for image in sorted(images)
             if "<animate" not in (ASSETS / image).read_text(encoding="utf-8")]
    assert still == []


def test_every_player_image_exists_and_is_animated():
    """specs/scene-polish.md: street clothes and tennis outfit."""
    story = load_story()
    images = [entry["image"] for entry in story.get("player", [])]
    assert len(images) >= 2
    problems = [image for image in images
                if not (ASSETS / image).is_file()
                or "<animate" not in (ASSETS / image).read_text(encoding="utf-8")]
    assert problems == []


def test_every_speaking_action_has_a_bubble_anchor_inside_the_image():
    """specs/scene-polish.md: people speak in bubbles above their heads."""
    story = load_story()
    problems = []
    for scene_id, scene in story["scenes"].items():
        for action in scene["actions"]:
            if "speaker" not in action:
                continue
            anchor = action.get("speaker_at")
            if anchor is None or not _inside_image(anchor[0], anchor[1]):
                problems.append(f"{scene_id}.{action['id']}")
    assert problems == []


def _at_court_after_round_two(**changes):
    from logic import GameState
    state = dict(
        scene="court",
        items=["key"],
        flags={"registered", "changed", "needs_racket", "knows_groundskeeper"},
        choices={},
        match_results=["win", "loss"],
        ending=None,
    )
    state.update(changes)
    return GameState(**state)


# Corrected per specs/bigger-world.md ("Changes to existing tests"): the
# groundskeeper now stands on Court 2 instead of the edge of the Center Court.
# What is checked stays the same: hidden before the hint, talkable without a
# scene change before and after the racket choice.


def test_groundskeeper_on_court_2_only_after_the_hint():
    """specs/bigger-world.md: he appears on Court 2 after the office's hint."""
    from logic import available_actions
    story = load_story()
    before_hint = _at_court_after_round_two(
        scene="court_2", items=[],
        flags={"registered", "changed", "needs_racket"})
    after_hint = _at_court_after_round_two(scene="court_2", items=[])

    assert not [a for a in available_actions(before_hint, story) if a.startswith("talk_groundskeeper")]
    assert "talk_groundskeeper_first" in available_actions(after_hint, story)


def test_groundskeeper_talk_on_court_2_keeps_the_scene():
    """specs/bigger-world.md (was: courtside talk in specs/scene-polish.md):
    talking to him never changes the scene, before and after the choice."""
    from logic import apply_action, available_actions, speaker_for
    story = load_story()

    before_choice = _at_court_after_round_two(scene="court_2")
    new_state, accepted, message = apply_action(before_choice, "talk_groundskeeper_has_key", story)
    assert accepted is True and new_state.scene == "court_2" and message

    after_choice = _at_court_after_round_two(
        scene="court_2", items=["key", "yonex"], choices={"racket": "yonex"})
    assert "talk_groundskeeper_after_choice" in available_actions(after_choice, story)
    new_state, accepted, message = apply_action(after_choice, "talk_groundskeeper_after_choice", story)
    assert accepted is True
    assert new_state == after_choice
    assert message
    assert speaker_for(after_choice, "talk_groundskeeper_after_choice", story) == "Groundskeeper"


def test_the_shed_stays_open_after_unlocking():
    """specs/scene-polish.md: leaving the shed and coming back does not ask to
    unlock it again. Corrected per specs/bigger-world.md: the way back now
    leads through the back corner and the main path."""
    from logic import apply_action, available_actions
    story = load_story()
    state = _at_court_after_round_two(scene="shed")

    state, accepted, _ = apply_action(state, "open_shed", story)
    assert accepted is True and state.scene == "shed_inside"
    for action_id in ["leave_shed_inside", "leave_shed", "go_back_corner"]:
        state, accepted, _ = apply_action(state, action_id, story)
        assert accepted is True, action_id
    assert state.scene == "shed"

    actions = available_actions(state, story)
    assert "open_shed" not in actions
    assert "enter_shed" in actions
    state, accepted, _ = apply_action(state, "enter_shed", story)
    assert accepted is True and state.scene == "shed_inside"


def test_every_inspect_action_has_an_existing_closeup():
    """specs/scene-polish.md: inspecting a racket shows a close-up."""
    story = load_story()
    problems = []
    for scene in story["scenes"].values():
        for action in scene["actions"]:
            if action["id"].startswith("inspect_"):
                image = action.get("closeup")
                if image is None or not (ASSETS / image).is_file():
                    problems.append(action["id"])
    assert problems == []


GAME_KEYS = {"opponent_speed", "opponent_reaction", "opponent_error", "ball_speed", "window", "reach"}


def test_every_match_outcome_has_valid_game_settings():
    """specs/match-minigame.md: every round is playable with its own settings."""
    story = load_story()
    problems = []
    for round_ in story["matches"]["rounds"]:
        for outcome in round_["outcomes"]:
            game = outcome.get("game")
            if game is None or not GAME_KEYS <= set(game):
                problems.append(round_["name"])
                continue
            if not all(isinstance(game[k], (int, float)) and game[k] >= 0 for k in GAME_KEYS):
                problems.append(round_["name"])
    assert problems == []


def test_round_two_ends_with_the_snapping_string():
    story = load_story()
    round_two = story["matches"]["rounds"][1]
    assert all(o["game"].get("event") == "string_break" for o in round_two["outcomes"])
