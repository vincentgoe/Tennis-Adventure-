"""Tests for playable matches (specs/match-minigame.md)."""

from logic import apply_match_result, match_setup

EASY = {"opponent_speed": 40, "window": 0.25}
HARD = {"opponent_speed": 120, "window": 0.08, "event": "string_break"}


def _with_games(story):
    rounds = story["matches"]["rounds"]
    rounds[0]["outcomes"][0]["game"] = EASY
    rounds[1]["outcomes"][0]["game"] = HARD
    rounds[2]["outcomes"][0]["game"] = EASY
    story["matches"]["blackout_text"] = "Everything goes dark."
    story["matches"]["replay_prompt"] = "Replay or give up?"
    story["endings"] = {"A": {"when_final": "win", "title": "A", "pages": []}}
    return story


# --- match_setup ---------------------------------------------------------------


def test_setup_of_the_next_round(mini_story, make_state):
    story = _with_games(mini_story)
    setup = match_setup(make_state(scene="court"), story)

    assert setup["round"] == "Round 1"
    assert setup["required"] == "win"
    assert setup["game"] == EASY


def test_setup_follows_the_round_and_its_outcome(mini_story, make_state):
    story = _with_games(mini_story)
    setup = match_setup(make_state(scene="court", match_results=["win"]), story)

    assert setup["round"] == "Round 2"
    assert setup["required"] == "loss"
    assert setup["game"]["event"] == "string_break"


def test_no_setup_when_no_match_is_due(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court", flags={"needs_racket"}, match_results=["win", "loss"])
    assert match_setup(state, story) is None


# --- apply_match_result ------------------------------------------------------------


def test_win_in_a_round_that_must_be_won_advances(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court")

    new_state, status, message = apply_match_result(state, "win", story)
    assert status == "advanced"
    assert new_state.match_results == ["win"]
    assert message == "Round 1 won."


def test_loss_in_a_round_that_must_be_won_offers_a_replay(mini_story, make_state):
    """Nothing changes: the player chooses Replay match or Give up."""
    story = _with_games(mini_story)
    state = make_state(scene="court")

    new_state, status, message = apply_match_result(state, "loss", story)
    assert status == "replay"
    assert new_state == state
    assert message == "Replay or give up?"


def test_loss_in_a_round_that_must_be_lost_advances(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court", match_results=["win"])

    new_state, status, message = apply_match_result(state, "loss", story)
    assert status == "advanced"
    assert new_state.match_results == ["win", "loss"]
    assert "needs_racket" in new_state.flags
    assert message == "String broke."


def test_win_in_a_round_that_must_be_lost_is_a_blackout(mini_story, make_state):
    """The story result wins: the round counts as lost, with the blackout text."""
    story = _with_games(mini_story)
    state = make_state(scene="court", match_results=["win"])

    new_state, status, message = apply_match_result(state, "win", story)
    assert status == "blackout"
    assert new_state.match_results == ["win", "loss"]
    assert "needs_racket" in new_state.flags
    assert message == "Everything goes dark."


def test_the_final_sets_the_ending(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court", items=["key", "yonex"], flags={"needs_racket"},
                       choices={"racket": "yonex"}, match_results=["win", "loss"])

    new_state, status, _ = apply_match_result(state, "win", story)
    assert status == "advanced"
    assert new_state.ending == "A"


def test_result_without_a_due_match_is_rejected(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court", flags={"needs_racket"}, match_results=["win", "loss"])

    new_state, status, _ = apply_match_result(state, "win", story)
    assert status == "rejected"
    assert new_state == state


def test_unknown_result_is_rejected(mini_story, make_state):
    story = _with_games(mini_story)
    state = make_state(scene="court")

    new_state, status, _ = apply_match_result(state, "draw", story)
    assert status == "rejected"
    assert new_state == state
