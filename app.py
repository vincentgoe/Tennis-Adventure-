"""Streamlit screens for Plot Twist.

This file only renders the state and collects clicks. Rules live in logic.py,
saving and loading in db.py.
"""

import streamlit as st

import logic
from db import DEFAULT_DB_PATH, load_game, save_game

DB_PATH = DEFAULT_DB_PATH


@st.cache_data
def get_story():
    return logic.load_story()


story = get_story()


# --- Session start: resume a saved game, or start a new one -----------------

if "state" not in st.session_state:
    saved = load_game(DB_PATH)
    st.session_state.state = saved if saved is not None else logic.new_game(story)
    st.session_state.feedback = None  # (accepted, message) of the last action


def handle_action(action_id):
    """Check the action with logic.py and save only if it was accepted."""
    new_state, accepted, message = logic.apply_action(
        st.session_state.state, action_id, story
    )
    if accepted:
        save_game(DB_PATH, new_state)
        st.session_state.state = new_state
    st.session_state.feedback = (accepted, message)


state = st.session_state.state


# --- Sidebar: inventory (always visible) ------------------------------------

with st.sidebar:
    st.header("Inventory")
    if state.items:
        for item_id in state.items:
            st.markdown(f"- {story['items'][item_id]['name']}")
    else:
        st.caption("Empty")


# --- Main screen ------------------------------------------------------------

st.title(story["title"])

if state.ending is not None:
    ending = story["endings"][state.ending]
    if st.session_state.feedback and st.session_state.feedback[1]:
        st.markdown(st.session_state.feedback[1])
    for page in ending["pages"]:
        st.subheader(page["name"])
        st.markdown(page["text"])
    st.success(ending["title"])
    st.stop()

scene = story["scenes"][state.scene]
st.header(scene["name"])
st.markdown(logic.scene_text(state, story))

if st.session_state.feedback is not None:
    accepted, message = st.session_state.feedback
    if message:
        if accepted:
            st.info(message)
        else:
            st.warning(message)

st.divider()

for action_id in logic.available_actions(state, story):
    action = logic.find_action(story, state.scene, action_id)
    st.button(
        action["label"],
        key=action_id,
        on_click=handle_action,
        args=(action_id,),
        width="stretch",
    )
