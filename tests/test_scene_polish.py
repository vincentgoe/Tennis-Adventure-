"""Tests for outfits, speech bubble anchors and allowed hotspots
(specs/scene-polish.md)."""

from logic import player_image, scene_hotspots, speaker_anchor

OUTFITS = [
    {"when": {"flags": ["changed"]}, "image": "sprites/tennis.svg"},
    {"image": "sprites/street.svg"},
]


# --- Player outfit ------------------------------------------------------------


def test_street_clothes_before_changing(mini_story, make_state):
    mini_story["player"] = OUTFITS
    assert player_image(make_state(), mini_story) == "sprites/street.svg"


def test_tennis_outfit_after_changing(mini_story, make_state):
    mini_story["player"] = OUTFITS
    state = make_state(flags={"changed"})
    assert player_image(state, mini_story) == "sprites/tennis.svg"


def test_no_player_image_without_outfits(mini_story, make_state):
    assert player_image(make_state(), mini_story) is None


# --- Allowed hotspots, walk and drop --------------------------------------------


def _door_with_animation(story):
    door = story["scenes"]["shed"]["actions"][0]
    assert door["id"] == "open_shed"
    door["hotspot"] = {"x": 10, "y": 20, "w": 30, "h": 30, "name": "Shed door",
                       "walk_to": [20, 40], "drop": "padlock"}
    return story


def _door(state, story):
    return next(h for h in scene_hotspots(state, story) if h["id"] == "open_shed")


def test_locked_door_hotspot_is_not_allowed_without_key(mini_story, make_state):
    """No unlock animation without the key: the component checks `allowed`."""
    story = _door_with_animation(mini_story)
    assert _door(make_state(scene="shed"), story)["allowed"] is False


def test_door_hotspot_is_allowed_with_key(mini_story, make_state):
    story = _door_with_animation(mini_story)
    door = _door(make_state(scene="shed", items=["key"]), story)

    assert door["allowed"] is True
    assert door["walk_to"] == [20, 40]
    assert door["drop"] == "padlock"


# --- Speech bubble anchors --------------------------------------------------------


def _story_with_anchors(story):
    talk = story["scenes"]["groundskeeper"]["actions"][0]
    assert talk["id"] == "talk_first"
    talk["speaker"] = "Groundskeeper"
    talk["speaker_at"] = [120, 60]

    door = story["scenes"]["shed"]["actions"][0]
    door["blocked_text"] = [
        {"when": {"flags": ["guard_present"]}, "text": "\"Stop!\"",
         "speaker": "Guard", "speaker_at": [40, 30]},
        {"text": "The door is locked."},
    ]
    return story


def test_anchor_of_an_allowed_action(mini_story, make_state):
    story = _story_with_anchors(mini_story)
    state = make_state(scene="groundskeeper", flags={"knows_groundskeeper"})

    assert speaker_anchor(state, "talk_first", story) == [120, 60]


def test_anchor_of_a_blocked_text(mini_story, make_state):
    story = _story_with_anchors(mini_story)
    state = make_state(scene="shed", flags={"guard_present"})

    assert speaker_anchor(state, "open_shed", story) == [40, 30]


def test_no_anchor_for_objects_and_unknown_actions(mini_story, make_state):
    story = _story_with_anchors(mini_story)

    assert speaker_anchor(make_state(scene="shed"), "open_shed", story) is None
    assert speaker_anchor(make_state(scene="grounds"), "fly_away", story) is None
