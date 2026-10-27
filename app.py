"""Streamlit screens for Plot Twist.

This file only renders the state and collects clicks. Rules live in logic.py,
saving and loading in db.py. Images live in assets/ and are referenced from
story.json.
"""

import math
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import logic
from db import DEFAULT_DB_PATH, load_game, save_game

DB_PATH = DEFAULT_DB_PATH
ASSETS = Path(__file__).parent / "assets"
IMAGE_W, IMAGE_H = 320, 180  # size of every scene image, in SVG units
PLAYER_W, PLAYER_H = 22, 42  # size of assets/sprites/player.svg at scale 1

# Small custom component: shows the scene SVG with clickable hotspots
scene_view = components.declare_component(
    "scene_view", path=str(Path(__file__).parent / "components" / "scene_view")
)
# Small custom component: the tennis minigame (specs/match-minigame.md)
match_view = components.declare_component(
    "match_view", path=str(Path(__file__).parent / "components" / "match")
)

# Fallback icons when an action in story.json has no "icon"
DEFAULT_ICONS = {
    "move_to": ":material/directions_walk:",
    "play_match": ":material/sports_tennis:",
    "add_item": ":material/back_hand:",
}

st.set_page_config(
    page_title="Plot Twist", page_icon="🎾", layout="wide", initial_sidebar_state="collapsed"
)

# Full-window look: no Streamlit toolbar or sidebar, little padding
st.markdown(
    """
    <style>
      header[data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
      .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1500px; }
      h1 { padding-top: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_story():
    return logic.load_story()


story = get_story()


def show_image(image, width="stretch"):
    """Show an image from assets/ (path as written in story.json)."""
    if image:
        st.image(str(ASSETS / image), width=width)


@st.cache_data
def read_asset(path):
    return (ASSETS / path).read_text(encoding="utf-8")


def player_position(state):
    """Where the player stands in the current scene: where they last walked to
    in this scene (kept for this session only), otherwise the scene's default."""
    default = story["scenes"][state.scene].get("player")
    walked = st.session_state.get("player_pos")
    if default and walked and walked["scene"] == state.scene:
        return {"x": walked["x"], "y": walked["y"], "scale": default["scale"]}
    return default


def sun_svg(progress, horizon):
    """A sun for the tournament day (specs/daylight.md): high on the left in
    the morning, a step further right after each match, warmer in the evening.
    The sky tint gets warmer too."""
    x = 34 + progress * 260
    y = 26 - 12 * math.sin(math.pi * min(progress, 1))
    warm = min(progress / 0.75, 1)
    core = "#%02x%02x%02x" % (255, int(228 - 60 * warm), int(107 - 40 * warm))
    return (
        f'<rect x="0" y="0" width="{IMAGE_W}" height="{horizon}" fill="#ff9a3c" opacity="{0.22 * progress:.2f}"/>'
        f'<g shape-rendering="auto"><circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="{core}" opacity="0.3"/>'
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{core}"/></g>'
    )


def with_sun(svg, state):
    """Draw the sun into an outdoor scene, just above its sky (behind everything else)."""
    sky = story["scenes"][state.scene].get("sky")
    marker = 'fill="url(#sky)"'
    if not sky or marker not in svg:
        return svg
    end = svg.index("/>", svg.index(marker)) + 2
    return svg[:end] + sun_svg(logic.day_progress(state, story), sky["horizon"]) + svg[end:]


def scene_svg_with_player(state):
    """The scene image as SVG text, with the player figure drawn into it.

    The figure's outfit depends on the state (street clothes or tennis kit).
    It is wrapped in <g id="player"><g class="hop"> so the component can let
    it walk and hop.
    """
    svg = with_sun(read_asset(logic.scene_image(state, story)).strip(), state)
    player = player_position(state)
    sprite_path = logic.player_image(state, story)
    if player is None or sprite_path is None:
        return svg
    scale = player["scale"]
    sprite = read_asset(sprite_path).strip().replace(
        "<svg ",
        f'<svg x="{player["x"]}" y="{player["y"]}" '
        f'width="{PLAYER_W * scale}" height="{PLAYER_H * scale}" ',
        1,
    )
    head, _, _ = svg.rpartition("</svg>")
    return head + '<g id="player"><g class="hop">' + sprite + "</g></g></svg>"


def action_icon(action):
    if "icon" in action:
        return action["icon"]
    for effect, icon in DEFAULT_ICONS.items():
        if effect in action.get("effects", {}):
            return icon
    return ":material/chat:"


# --- Session start: resume a saved game, or start a new one -----------------

if "state" not in st.session_state:
    saved = load_game(DB_PATH)
    # A save from an older version may point to a scene that no longer exists
    # (e.g. the old single "grounds" screen): then start a new game.
    if saved is None or saved.scene not in story["scenes"]:
        saved = logic.new_game(story)
    st.session_state.state = saved
    st.session_state.feedback = None  # message of the last action, see below
    st.session_state.message_count = 0


def new_message(text, speaker=None, anchor=None, closeup=None):
    """Show `text` in the dialogue box. Every message gets a new id."""
    st.session_state.message_count += 1
    st.session_state.feedback = {
        "id": st.session_state.message_count,
        "text": text,
        "speaker": speaker,
        "anchor": anchor,  # where the speech bubble points to, or None
        "closeup_svg": read_asset(closeup) if closeup else None,  # item reveal
    }


def handle_action(action_id):
    """Check the action with logic.py and save only if it was accepted.

    Starting a match opens the minigame instead of applying a fixed result.
    """
    before = st.session_state.state
    action = logic.find_action(story, before.scene, action_id)
    if action and action.get("effects", {}).get("play_match") and logic.match_setup(before, story):
        st.session_state.in_match = True
        st.session_state.match_status = None
        st.session_state.match_count = st.session_state.get("match_count", 0) + 1
        st.session_state.feedback = None
        return
    speaker = logic.speaker_for(before, action_id, story)
    anchor = logic.speaker_anchor(before, action_id, story)
    closeup = logic.closeup_for(before, action_id, story)
    new_state, accepted, message = logic.apply_action(before, action_id, story)
    if accepted:
        save_game(DB_PATH, new_state)
        st.session_state.state = new_state
    new_message(message, speaker, anchor, closeup)
    st.session_state.ending_page = 0


def handle_match_result():
    """The minigame reported win or loss: logic.py decides what it means."""
    key = f"match_view_{st.session_state.match_count}"
    reported = (st.session_state.get(key) or {}).get("result")
    new_state, status, message = logic.apply_match_result(st.session_state.state, reported, story)
    if status in ("advanced", "blackout"):
        save_game(DB_PATH, new_state)
        st.session_state.state = new_state
        st.session_state.in_match = False
        st.session_state.ending_page = 0
        new_message(message)
    elif status == "replay":
        st.session_state.match_status = "replay"
        st.session_state.replay_text = message
    else:
        st.session_state.in_match = False


def replay_match():
    st.session_state.match_status = None
    st.session_state.match_count += 1      # a new key starts a fresh game


def ask_give_up():
    st.session_state.match_status = "confirm_give_up"


def cancel_give_up():
    st.session_state.match_status = "replay"


def confirm_give_up():
    """Give up = a completely new game (after confirmation)."""
    st.session_state.in_match = False
    st.session_state.match_status = None
    confirm_new_game()


def ask_new_game():
    st.session_state.confirm_new_game = True


def cancel_new_game():
    """A6: cancelling keeps the game as it is. Nothing is saved."""
    st.session_state.confirm_new_game = False


def confirm_new_game():
    """A6: replace the saved game with a new one."""
    fresh = logic.new_game(story)
    save_game(DB_PATH, fresh)
    st.session_state.state = fresh
    st.session_state.feedback = None
    st.session_state.confirm_new_game = False
    st.session_state.ending_page = 0
    st.session_state.player_pos = None
    st.session_state.in_match = False


def next_ending_page():
    st.session_state.ending_page = st.session_state.get("ending_page", 0) + 1


def handle_click():
    """A hotspot in the scene image was clicked: same path as a button."""
    clicked = st.session_state.get("scene_view")
    if clicked and "action" in clicked:
        walked = clicked.get("player")
        if walked:
            # Remember where the player walked to in this scene
            st.session_state.player_pos = {
                "scene": st.session_state.state.scene, "x": walked["x"], "y": walked["y"]}
        handle_action(clicked["action"])


state = st.session_state.state
ui = story["ui_texts"]

main_col, corner_col = st.columns([5, 1], gap="medium")


# --- Top right corner: inventory list and New game ----------------------------

with corner_col:
    with st.container(border=True):
        st.markdown("**Inventory**")
        if state.items:
            for item_id in state.items:
                item = story["items"][item_id]
                icon_col, name_col = st.columns([1, 3], vertical_alignment="center")
                with icon_col:
                    show_image(item.get("image"), width=32)
                with name_col:
                    st.markdown(item["name"])
        else:
            st.caption("Empty")

        if st.session_state.get("confirm_new_game"):
            st.warning(ui["new_game_confirm"], icon=":material/help:")
            st.button(ui["new_game_yes"], type="primary", on_click=confirm_new_game, width="stretch")
            st.button(ui["new_game_cancel"], on_click=cancel_new_game, width="stretch")
        else:
            st.button("New game", icon=":material/restart_alt:", on_click=ask_new_game, width="stretch")


# --- Main screen ------------------------------------------------------------

with main_col:
    st.title(f"🎾 {story['title']}")

    if state.ending is not None:
        # End scenes, one page at a time, so each animation starts when shown
        ending = story["endings"][state.ending]
        pages = ending["pages"]
        index = min(st.session_state.get("ending_page", 0), len(pages) - 1)
        if index == 0 and st.session_state.feedback and st.session_state.feedback["text"]:
            st.markdown(st.session_state.feedback["text"])
        page = pages[index]
        st.header(page["name"])
        show_image(logic.page_image(state, page, story), width=900)
        st.markdown(page["text"])
        if index < len(pages) - 1:
            st.button(ui["continue"], icon=":material/arrow_forward:", type="primary",
                      on_click=next_ending_page)
        else:
            st.success(ending["title"], icon=":material/emoji_events:")
        st.stop()

    setup = logic.match_setup(state, story) if st.session_state.get("in_match") else None
    if setup is not None:
        # --- The match screen ------------------------------------------------
        st.header(f"{ui['match_screen']}: {setup['round']}")
        status = st.session_state.get("match_status")
        if status == "replay":
            st.warning(st.session_state.get("replay_text"), icon=":material/sports_tennis:")
            replay_col, give_up_col, _ = st.columns([1, 1, 3])
            replay_col.button(ui["replay_match"], type="primary", on_click=replay_match, width="stretch")
            give_up_col.button(ui["give_up"], on_click=ask_give_up, width="stretch")
        elif status == "confirm_give_up":
            st.warning(ui["give_up_confirm"], icon=":material/help:")
            yes_col, no_col, _ = st.columns([1, 1, 3])
            yes_col.button(ui["new_game_yes"], type="primary", on_click=confirm_give_up, width="stretch")
            no_col.button(ui["new_game_cancel"], on_click=cancel_give_up, width="stretch")
        else:
            match_view(
                round=setup["round"],
                game=setup["game"],
                must_lose=setup["required"] == "loss",
                racket=state.choices.get("racket", "original"),
                kit=next((c for c in ("black", "pink") if f"outfit_{c}" in state.flags), "white"),
                day=logic.day_progress(state, story),
                blackout_text=story["matches"]["blackout_text"],
                ui={"start": ui["match_start"], "controls": ui["match_controls"],
                    "aim": ui["match_aim"], "tutorial": ui["match_tutorial"]},
                key=f"match_view_{st.session_state.match_count}",
                on_change=handle_match_result,
                default=None,
            )
        st.stop()
    st.session_state.in_match = False

    scene = story["scenes"][state.scene]
    st.header(scene["name"])

    # The last message is shown in the dialogue box inside the scene image
    feedback = st.session_state.feedback
    message = feedback if feedback and feedback["text"] else None
    if message:
        # e.g. the Center Court shows its story box in the middle of the picture
        message = dict(message, position=scene.get("dialog_position", "bottom"))

    scene_view(
        svg=scene_svg_with_player(state),
        hotspots=[dict(h, preview_svg=read_asset(h["preview"]) if h.get("preview") else None)
                  for h in logic.scene_hotspots(state, story)],
        player=player_position(state),  # where the player stands now, for walking
        message=message,
        width=IMAGE_W,
        height=IMAGE_H,
        key="scene_view",
        on_change=handle_click,
        default=None,
    )
    st.caption("Click on things in the picture. Arrows lead back.")
    st.markdown(logic.scene_text(state, story))

    with st.expander("All actions", icon=":material/list:"):
        for action_id in logic.available_actions(state, story):
            action = logic.find_action(story, state.scene, action_id)
            st.button(
                action["label"],
                key=action_id,
                icon=action_icon(action),
                on_click=handle_action,
                args=(action_id,),
                width="stretch",
            )
