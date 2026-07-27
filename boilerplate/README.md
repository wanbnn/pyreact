# Orbit Board — PyReact Boilerplate

A task-management application created by the PyReact CLI and expanded to show
the framework in a realistic project with structure, state, and tests.

## What this example demonstrates

- a scaffold created with `pyreact create boilerplate`;
- reusable functional components;
- `use_state` for tasks and the active filter;
- `use_memo` and a custom hook for derived metrics;
- creation, completion, deletion, and filtering events;
- DOM reconciliation after multiple updates;
- static SSR for presentation components;
- integration tests against the Python DOM;
- an end-to-end Chromium test;
- development server and static build.

## Layout

```text
boilerplate/
├── public/index.html          # Web interface served by the CLI
├── src/
│   ├── components/
│   │   ├── stat_card.py
│   │   └── task_card.py
│   ├── hooks/use_task_stats.py
│   └── index.py               # Application built with the PyReact API
├── tests/
│   ├── test_app.py            # Python runtime integration
│   └── test_browser_e2e.py    # Real Chromium flow
└── pyproject.toml
```

## Installation

Because this boilerplate lives inside the framework repository, install the
local framework in editable mode:

```bash
cd ..
python -m pip install -e ".[e2e]"
cd boilerplate
python -m playwright install chromium
```

## Run

```bash
pyreact dev
```

Open `http://127.0.0.1:3000`. To avoid opening a browser automatically:

```bash
pyreact dev --no-open --port 3000
```

## Test and build

```bash
python -m pytest -q
pyreact build
```

The static build is written to `dist/index.html`.

## Current runtime note

`src/index.py` exercises the Python runtime in integration tests. The current
CLI does not transpile Python to JavaScript, so the web server delivers the
equivalent self-contained implementation from `public/index.html`. Both paths
represent the same application and are validated independently.
