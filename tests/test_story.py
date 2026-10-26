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


def test_every_referenced_image_exists():
    story = load_story()
    images = [image for image in _referenced_images(story) if image is not None]
    missing = [image for image in images if not (ASSETS / image).is_file()]
    assert missing == []
