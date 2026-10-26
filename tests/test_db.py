"""Persistence tests for db.py, based on specs/first-feature.md.

Every test uses a temporary database file (pytest's tmp_path), never the
real game database.
"""

from db import load_game, save_game
from logic import apply_action, available_actions


def test_load_without_save_returns_none(tmp_path):
    """Spec "App start": without a save, there is nothing to resume."""
    assert load_game(tmp_path / "game.db") is None


def test_save_and_load_roundtrip(tmp_path, make_state):
    """BRD "What the product must remember": all six fields come back."""
    db_path = tmp_path / "game.db"
    state = make_state(
        scene="shed_inside",
        items=["key", "yonex"],
        flags={"registered", "changed", "needs_racket"},
        choices={"racket": "yonex"},
        match_results=["win", "loss"],
        ending=None,
    )

    save_game(db_path, state)

    assert load_game(db_path) == state


def test_saving_again_replaces_the_previous_save(tmp_path, make_state):
    """Spec decision: there is one saved game (a single row)."""
    db_path = tmp_path / "game.db"
    save_game(db_path, make_state(scene="shed"))
    save_game(db_path, make_state(scene="shed_inside", items=["key"]))

    assert load_game(db_path) == make_state(scene="shed_inside", items=["key"])


def test_resume_restores_state_and_routes(tmp_path, mini_story, make_state):
    """BRD A4 / spec case 5: after a restart, scene, item and choice are
    restored, and the same routes remain available."""
    db_path = tmp_path / "game.db"
    state = make_state(scene="shed", items=["key"])

    # Play: open the shed, then take the racket. Save after each accepted action.
    for action_id in ["open_shed", "take_yonex"]:
        state, accepted, _ = apply_action(state, action_id, mini_story)
        assert accepted is True
        save_game(db_path, state)

    # "Restart": load the game again from the same file
    resumed = load_game(db_path)

    assert resumed == state
    assert resumed.scene == "shed_inside"
    assert resumed.items == ["key", "yonex"]
    assert resumed.choices == {"racket": "yonex"}
    assert available_actions(resumed, mini_story) == available_actions(
        state, mini_story
    )
