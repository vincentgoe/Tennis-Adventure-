# AGENTS.md

Guidance for AI coding agents (and humans) working on **Plot Twist**, a short
text-based tennis mystery / escape-room game built for the course
"Introduction to Programming" (Nova SBE).

The requirements are in `docs/product-brief.md` (the BRD). Read it before
changing behaviour. Each feature has a task spec in `specs/`.

## Commands

All commands go through `uv`. Do not use `pip` or a manually activated venv.

| Task             | Command                         |
| ---------------- | ------------------------------- |
| Install / sync   | `uv sync`                       |
| Run the app      | `uv run streamlit run app.py`   |
| Run all tests    | `uv run pytest`                 |
| Add a dependency | `uv add <package>`              |
| Add a dev tool   | `uv add --dev <package>`        |

Note: the parent folder name ends with a space
(`Introduction to Programming `). Always quote paths in shell commands.

## Project structure

```
app.py               Streamlit screens only: render state, collect clicks
logic.py             Game rules: pure functions, no Streamlit, no SQLite
db.py                Persistence: save / load / reset game progress in SQLite
story.json           Story content: scenes, actions, conditions, items, matches, endings
tests/               pytest tests
docs/                BRD (product-brief.md) and story design (story.md)
specs/               Task specs, one per feature (Why / What / Out of scope / Done when)
AGENTS.md            This file
```

Dependencies point in one direction only: `app.py` → `logic.py` and `db.py`.
`logic.py` must not import Streamlit or `db.py`, so it can be tested without a UI
or database.

## Story as data

- Story content (scenes, texts, actions, conditions, item locations, endings)
  is **data**, kept separate from the code. `logic.py` reads it and must not
  hard-code scene names, items, or texts.
- SQLite stores **only the player's progress** for the active game: current
  scene, collected items, remembered decisions, and whether an ending was
  reached. The story content is never written to the database.
- A new game resets progress and keeps the story content (BRD PT R4).
- The local database file is not committed (`*.db`, `*.sqlite` are in
  `.gitignore`). Neither are secrets (`.env`).

## Testing rules

- Tests are written **first**, reviewed, and only then is the feature
  implemented.
- After review, tests must **not** be weakened, skipped, marked xfail, or
  deleted to make the code pass.
- A test that turns out to be wrong is corrected only explicitly, with a
  reference to the BRD rule or scenario it contradicts (e.g. "fix per PT R2"),
  and that change is stated in the commit message.
- Rule tests target `logic.py` directly. Persistence tests use a temporary
  database file (e.g. pytest's `tmp_path`), never the real game database.

## Branch and feature workflow

1. `main` holds the initial commit. Features are never developed on `main`.
2. Create a feature branch (the first one is `first-feature`).
3. Write or update the spec in `specs/<branch-name>.md`.
4. Write the tests and get them reviewed.
5. Implement until `uv run pytest` is fully green.
6. Verify by hand: run `uv run streamlit run app.py`, play the feature,
   **stop the app, start it again**, and check that progress was restored.
7. Commit, push, open a pull request, review, merge into `main`.

A feature is not done until steps 5 and 6 have both passed.

## Working agreement for agents

- The author wants to understand and write game logic and tests themselves.
  Explain, propose, and review. Do **not** implement logic or tests unless
  explicitly asked.
- Work in small steps and wait for approval after each step.
- If the BRD or a spec is ambiguous, ask instead of filling the gap.
- Code, file contents, and commit messages are in English. Explanations to the
  author are in German.
