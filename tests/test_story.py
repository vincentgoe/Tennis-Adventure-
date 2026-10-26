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
