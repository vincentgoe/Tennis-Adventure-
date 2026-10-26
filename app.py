"""Streamlit screens for Plot Twist.

This file only renders the state and collects clicks. Rules live in logic.py,
saving and loading in db.py. Images live in assets/ and are referenced from
story.json.
"""

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


def scene_svg_with_player(state):
    """The scene image as SVG text, with the player figure drawn into it.

    The figure's outfit depends on the state (street clothes or tennis kit).
    It is wrapped in <g id="player"> so the component can let it walk.
    """
    svg = read_asset(logic.scene_image(state, story)).strip()
    player = story["scenes"][state.scene].get("player")
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
    return head + '<g id="player">' + sprite + "</g></svg>"


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
    st.session_state.state = saved if saved is not None else logic.new_game(story)
    st.session_state.feedback = None  # message of the last action, see below
    st.session_state.message_count = 0


def handle_action(action_id):
    """Check the action with logic.py and save only if it was accepted."""
    before = st.session_state.state
    speaker = logic.speaker_for(before, action_id, story)
    anchor = logic.speaker_anchor(before, action_id, story)
    closeup = logic.closeup_for(before, action_id, story)
    new_state, accepted, message = logic.apply_action(before, action_id, story)
    if accepted:
        save_game(DB_PATH, new_state)
        st.session_state.state = new_state
    # Every action gets a new id, so the dialogue box knows it is a new message
    st.session_state.message_count += 1
    st.session_state.feedback = {
        "id": st.session_state.message_count,
        "text": message,
        "speaker": speaker,
        "anchor": anchor,  # where the speech bubble points to, or None
        "closeup_svg": read_asset(closeup) if closeup else None,  # item reveal
    }
    st.session_state.ending_page = 0


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


def next_ending_page():
    st.session_state.ending_page = st.session_state.get("ending_page", 0) + 1


def handle_click():
    """A hotspot in the scene image was clicked: same path as a button."""
    clicked = st.session_state.get("scene_view")
    if clicked and "action" in clicked:
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
        show_image(page.get("image"), width=900)
        st.markdown(page["text"])
        if index < len(pages) - 1:
            st.button(ui["continue"], icon=":material/arrow_forward:", type="primary",
                      on_click=next_ending_page)
        else:
            st.success(ending["title"], icon=":material/emoji_events:")
        st.stop()

    scene = story["scenes"][state.scene]
    st.header(scene["name"])

    # The last message is shown in the dialogue box inside the scene image
    feedback = st.session_state.feedback
    message = feedback if feedback and feedback["text"] else None

    scene_view(
        svg=scene_svg_with_player(state),
        hotspots=logic.scene_hotspots(state, story),
        player=scene.get("player"),  # start position, for the walk animation
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
