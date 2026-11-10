# Campus Tycoon · Price War

A business game for Nova students. Each player runs a campus stand selling Café,
Croissant and Water: buy stock, set prices and trade for five days. In a tournament,
all players share the same customers, so the cheapest stand sells first.

**Live app:** https://price-war-game.streamlit.app/

## Team

| Name | Student number |
|---|---|
| Patrick Siaulys Pfeiffer | 74488 |
| Filippo Venturini | 74863 |
| Filippo Bortignon | 74819 |
| Zoe Mormile | 65404 |
| Edoardo Giovanni Panetta | 72795 |

## Run the app

You need [uv](https://docs.astral.sh/uv/). In the project folder:

    uv run streamlit run app.py

The app opens in your browser at http://localhost:8501.

## Run the tests

    uv run pytest

## Project structure

- `app.py`: the Streamlit screens
- `logic.py`: the game rules and calculations
- `db.py`: the only file that reads and writes the database
- `tests/`: pytest tests
- `docs/`: the original product brief and the team project brief (`team-brief.md`)
- `specs/`: one spec per feature
- `AGENTS.md`: the rules every coding agent follows

## How we work

Each feature has a spec in `specs/`, its tests are written first, and it is built on
its own branch. Every pull request is reviewed by another team member before merging.
