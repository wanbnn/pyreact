# PyReact execution and testing guide

## Preparation

From the repository root:

```bash
python -m pip install -e ".[dev]"
```

For end-to-end tests, also install Playwright and Chromium:

```bash
python -m pip install playwright
python -m playwright install chromium
```

## Test the framework

```bash
# Complete suite
python -m pytest -q

# End-to-end only
python -m pytest tests/e2e -q

# Coverage
python -m pytest --cov=pyreact --cov-report=term-missing
```

## Create and run a project

```bash
pyreact create my-app
cd my-app
pyreact dev
```

In CI or when a browser window should not open:

```bash
pyreact dev --no-open --port 3000
```

Open `http://127.0.0.1:3000`.

## Generate files

```bash
pyreact generate component Button
pyreact generate component Counter --class
pyreact generate hook useCounter
```

## Build

```bash
pyreact build
```

Public files are copied to `dist`, which can be served by any static HTTP
server.

## Regenerate PDF files

```bash
python scripts/generate_pdfs.py
```

The command refreshes the three PDF files stored under `docs/`.
