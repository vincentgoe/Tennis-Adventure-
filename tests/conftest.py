import pytest

from logic import GameState


@pytest.fixture
def mini_story():
    """A tiny story with the same format as story.json.

    Rule tests use this instead of story.json, so changing the real story
    (texts, rounds, scenes) does not break them.
    """
    return {
        "start_scene": "grounds",
        "items": {
            "key": {"name": "Key"},
            "yonex": {"name": "Old Yonex"},
        },
        "scenes": {
            "grounds": {
                "name": "Grounds",
                "texts": [{"text": "The grounds."}],
                "actions": [
                    {
                        "id": "go_shed",
                        "label": "Go to the shed",
                        "effects": {"move_to": "shed"},
                    },
                    {
                        "id": "go_court",
                        "label": "Go to the court",
                        "effects": {"move_to": "court"},
                    },
                ],
            },
            "court": {
                "name": "Court",
                "texts": [{"text": "The court."}],
                "actions": [
                    {
                        "id": "start_match",
                        "label": "Start match",
                        "requires": {"match_due": True},
                        "effects": {"play_match": True},
                    },
                    {
                        "id": "go_groundskeeper",
                        "label": "Go to the groundskeeper",
                        "requires": {"flags": ["knows_groundskeeper"]},
                        "effects": {"move_to": "groundskeeper"},
                    },
                    {
                        "id": "leave_court",
                        "label": "Back to the grounds",
                        "effects": {"move_to": "grounds"},
                    },
                ],
            },
            "groundskeeper": {
                "name": "Groundskeeper",
                "texts": [{"text": "The groundskeeper."}],
                "actions": [
                    {
                        "id": "talk_first",
                        "label": "Talk",
                        "requires": {"not_items": ["key"]},
                        "effects": {"add_item": "key", "show_text": "Here is the key."},
                    },
                    {
                        "id": "talk_has_key",
                        "label": "Talk",
                        "requires": {"items": ["key"]},
                        "effects": {"show_text": "Check the shed."},
                    },
                    {
                        "id": "leave_groundskeeper",
                        "label": "Back to the court",
                        "effects": {"move_to": "court"},
                    },
                ],
            },
            "shed": {
                "name": "Shed",
                "texts": [{"text": "A locked shed."}],
                "actions": [
                    {
                        "id": "open_shed",
                        "label": "Open the door",
                        "requires": {"items": ["key"]},
                        "blocked_text": [{"text": "The door is locked."}],
                        "effects": {"move_to": "shed_inside"},
                    },
                    {
                        "id": "leave_shed",
                        "label": "Back to the grounds",
                        "effects": {"move_to": "grounds"},
                    },
                ],
            },
            "shed_inside": {
                "name": "Inside the shed",
                "texts": [{"text": "Inside the shed."}],
                "actions": [
                    {
                        "id": "inspect_yonex",
                        "label": "Inspect the old Yonex",
                        "requires": {"no_choice": "racket"},
                        "effects": {"show_text": "Roger F."},
                    },
                    {
                        "id": "take_yonex",
                        "label": "Take the old Yonex",
                        "requires": {"no_choice": "racket"},
                        "effects": {
                            "add_item": "yonex",
                            "set_choice": {"racket": "yonex"},
                            "show_text": "Hurry!",
                        },
                    },
                    {
                        "id": "leave_shed_inside",
                        "label": "Leave the shed",
                        "effects": {"move_to": "grounds"},
                    },
                ],
            },
        },
        "matches": {
            "rounds": [
                {
                    "name": "Round 1",
                    "requires": {},
                    "outcomes": [{"result": "win", "text": "Round 1 won."}],
                },
                {
                    "name": "Round 2",
                    "requires": {},
                    "outcomes": [
                        {
                            "result": "loss",
                            "text": "String broke.",
                            "effects": {"set_flags": ["needs_racket"]},
                        }
                    ],
                },
                {
                    "name": "Final",
                    "requires": {"choice_made": "racket"},
                    "outcomes": [
                        {"when": {"items": ["yonex"]}, "result": "win", "text": "Final won."}
                    ],
                },
            ],
        },
        "ui_texts": {
            "not_available": "Not available.",
        },
    }


@pytest.fixture
def make_state():
    """Build a GameState. Fields that are not given get their new-game value."""

    def _make_state(
        scene="grounds",
        items=None,
        flags=None,
        choices=None,
        match_results=None,
        ending=None,
    ):
        return GameState(
            scene=scene,
            items=items if items is not None else [],
            flags=flags if flags is not None else set(),
            choices=choices if choices is not None else {},
            match_results=match_results if match_results is not None else [],
            ending=ending,
        )

    return _make_state
