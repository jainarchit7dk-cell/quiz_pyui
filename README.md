# PyUI — a tiny UI framework in Python + Quiz demo

Zero dependencies, zero JavaScript. Python 3.8+.

    python quiz_app.py      # open http://localhost:8000
    python test_pyui.py     # quick tests

## How it maps to the task
| Requirement | Where |
|---|---|
| 1. Components as a tree of elements with props | `Element`, `el()`, `div()/button()...` in `pyui/core.py` |
| 2. Renderer producing HTML | `_Renderer.render` in `pyui/core.py` |
| 3. State handling | `State` (marks itself dirty on change); the view re-runs on every request |
| 4. Events: click → state change → re-render | `on_click` → id → form POST → handler(state) → redirect → re-render (`pyui/server.py`) |
| 5. Demo app | `quiz_app.py` — start, questions, instant feedback, score, replay |

## Flow
click button → browser POSTs `evt=e3` → server rebuilds the tree, finds handler `e3`
→ handler mutates `State` → server redirects → GET renders the new tree as HTML.

## Notes / limits (be honest in the demo)
- Full-page re-render per click (no virtual DOM / diffing) — simple on purpose.
- State is kept per browser in server memory (cookie session).
- Deploy: push to GitHub, create a Render/Railway web service, start command `python quiz_app.py` (it reads `PORT`).
