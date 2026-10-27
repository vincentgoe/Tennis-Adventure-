"""Tests for the moving sun (specs/daylight.md)."""

from pathlib import Path

from logic import day_progress, load_story

ASSETS = Path(__file__).parent.parent / "assets"


def test_day_progress_follows_the_matches(mini_story, make_state):
    rounds = len(mini_story["matches"]["rounds"])           # 3 in the mini story
    assert day_progress(make_state(), mini_story) == 0
    assert day_progress(make_state(match_results=["win"]), mini_story) == 1 / rounds
    assert day_progress(make_state(match_results=["win", "loss", "win"]), mini_story) == 1


def test_outdoor_scenes_have_a_sky_for_the_sun():
    story = load_story()
    outdoor = {sid: scene for sid, scene in story["scenes"].items() if "sky" in scene}
    assert {"entrance", "main_path", "court", "court_2", "shed"} <= set(outdoor)
    for scene_id, scene in outdoor.items():
        assert 0 < scene["sky"]["horizon"] < 180, scene_id
        for entry in scene["texts"]:
            svg = (ASSETS / entry["image"]).read_text(encoding="utf-8")
            assert 'fill="url(#sky)"' in svg, entry["image"]
