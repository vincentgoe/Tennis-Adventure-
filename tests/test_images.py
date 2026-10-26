"""Tests for state-dependent scene images (specs/visuals.md)."""

from logic import scene_image


def _image_story():
    return {
        "start_scene": "shed_inside",
        "items": {"yonex": {"name": "Old Yonex", "image": "items/yonex.svg"}},
        "scenes": {
            "shed_inside": {
                "name": "Inside the shed",
                "texts": [
                    {
                        "when": {"choice_made": "racket"},
                        "text": "Empty.",
                        "image": "scenes/shed_empty.svg",
                    },
                    {"text": "Two rackets.", "image": "scenes/shed_rackets.svg"},
                ],
                "actions": [],
            },
            "plain": {
                "name": "No image",
                "texts": [{"text": "Nothing to see."}],
                "actions": [],
            },
        },
    }


def test_scene_image_follows_the_matching_text(make_state):
    """The image belongs to the first matching text entry, like the text."""
    story = _image_story()
    before = make_state(scene="shed_inside")
    after = make_state(
        scene="shed_inside", items=["yonex"], choices={"racket": "yonex"}
    )

    assert scene_image(before, story) == "scenes/shed_rackets.svg"
    assert scene_image(after, story) == "scenes/shed_empty.svg"


def test_scene_without_image_returns_none(make_state):
    """Images are optional: a text entry without one gives None."""
    assert scene_image(make_state(scene="plain"), _image_story()) is None
