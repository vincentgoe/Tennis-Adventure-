"""Tests for starting over (BRD A6, specs/new-game.md)."""

from db import load_game, save_game
from logic import new_game


def _progress(make_state):
    """A game in the middle of the story."""
    return make_state(
        scene="shed_inside",
        items=["key", "yonex"],
        flags={"registered", "changed", "needs_racket"},
        choices={"racket": "yonex"},
        match_results=["win", "loss"],
    )


def test_confirmed_restart_replaces_saved_progress(tmp_path, mini_story, make_state):
    """A6: confirm a restart -> opening scene, empty inventory, initial decisions."""
    db_path = tmp_path / "game.db"
    save_game(db_path, _progress(make_state))

    # What the app does on "Yes, start over"
    save_game(db_path, new_game(mini_story))

    restored = load_game(db_path)
    assert restored.scene == mini_story["start_scene"]
    assert restored.items == []
    assert restored.flags == set()
    assert restored.choices == {}
    assert restored.match_results == []
    assert restored.ending is None


def test_cancelled_restart_keeps_saved_progress(tmp_path, make_state):
    """A6: cancel a restart -> progress is retained (nothing is written)."""
    db_path = tmp_path / "game.db"
    progress = _progress(make_state)
    save_game(db_path, progress)

    # "Cancel" writes nothing, so the save is still the old progress
    assert load_game(db_path) == progress


def test_restart_from_an_ending_starts_a_playable_game(tmp_path, mini_story, make_state):
    """PT05: from an ending, a new game is possible and has no ending."""
    db_path = tmp_path / "game.db"
    save_game(db_path, make_state(scene="court", match_results=["win", "loss", "win"], ending="A"))

    save_game(db_path, new_game(mini_story))

    assert load_game(db_path).ending is None
