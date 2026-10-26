"""Save and load the player's progress in SQLite.

Only progress is stored, never story content. There is one saved game: a
single row in the table `game`. Lists, sets and dicts are stored as JSON text.
"""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from logic import GameState

DEFAULT_DB_PATH = Path(__file__).parent / "plot_twist.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS game (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    scene         TEXT NOT NULL,
    items         TEXT NOT NULL,
    flags         TEXT NOT NULL,
    choices       TEXT NOT NULL,
    match_results TEXT NOT NULL,
    ending        TEXT
)
"""


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_TABLE)
    return conn


def save_game(db_path, state):
    """Store the state, replacing any previous save."""
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO game "
            "(id, scene, items, flags, choices, match_results, ending) "
            "VALUES (1, ?, ?, ?, ?, ?, ?)",
            (
                state.scene,
                json.dumps(state.items),
                json.dumps(sorted(state.flags)),
                json.dumps(state.choices),
                json.dumps(state.match_results),
                state.ending,
            ),
        )


def load_game(db_path):
    """The saved state, or None if there is no save."""
    if not Path(db_path).exists():
        return None
    with closing(_connect(db_path)) as conn:
        row = conn.execute(
            "SELECT scene, items, flags, choices, match_results, ending "
            "FROM game WHERE id = 1"
        ).fetchone()
    if row is None:
        return None
    scene, items, flags, choices, match_results, ending = row
    return GameState(
        scene=scene,
        items=json.loads(items),
        flags=set(json.loads(flags)),
        choices=json.loads(choices),
        match_results=json.loads(match_results),
        ending=ending,
    )
