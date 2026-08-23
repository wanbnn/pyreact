# 🐍 PyReact — Declarative Web Framework for Python

[![PyPI version](https://badge.fury.io/py/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![Python](https://img.shields.io/pypi/pyversions/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://readthedocs.org/projects/pyreact-framework/badge/?version=latest)](https://pyreact-framework.readthedocs.io/en/latest/)

**PyReact** is a React-inspired declarative web framework built natively for
Python. It provides reactive components and hooks, keyed reconciliation,
server-side rendering and hydration, routing, streaming, hot reload, and a
project CLI.

## Installation

```bash
pip install pyreact-framework
```

Install the current GitHub version:

```bash
pip install git+https://github.com/wanbnn/pyreact.git
```

Set up a local development checkout:

```bash
git clone https://github.com/wanbnn/pyreact.git
cd pyreact
pip install -e ".[dev]"
```

## Quick start

Create and run a project:

```bash
pyreact create my-app
cd my-app
pyreact dev
```

A functional counter in ``src/index.py``:

```python
from pyreact import h, use_state


def Counter(props):
    count, set_count = use_state(0)

    return h(
        "div",
        {"className": "counter"},
        h("h1", None, f"Count: {count}"),
        h("button", {"onClick": lambda event: set_count(count + 1)}, "+"),
        h("button", {"onClick": lambda event: set_count(count - 1)}, "-"),
    )
```

The development server discovers ``App`` (or the first component) in the
configured entry module and serves it directly.

## Execution model

PyReact uses a server-driven model. Python is the authority for component
state and rendering; each browser session owns an isolated component tree.
The first request produces complete HTML, while a small built-in browser
runtime forwards DOM events to Python and applies the updated markup. Links
using the router integrate with the History API. In development, source-file
changes invalidate sessions and trigger a browser reload.

This model does not transpile Python into JavaScript. Production therefore
runs a Python server created by ``pyreact build``. Static assets continue to
be served from ``public/``.

## Components

Functional components are plain Python callables:

```python
def Button(props):
    return h(
        "button",
        {"className": "btn", "onClick": props.get("onClick")},
        props.get("children"),
    )
```

Class components extend `Component`:

```python
from pyreact import Component, h


class Counter(Component):
    def __init__(self, props):
        super().__init__(props)
        self.state = {"count": 0}

    def render(self):
        return h(
            "button",
            {"onClick": lambda event: self.set_state({"count": self.state["count"] + 1})},
            f"Count: {self.state['count']}",
        )
```

## Hooks

```python
from pyreact import h, use_effect, use_ref, use_state


def MyComponent(props):
    count, set_count = use_state(0)
    use_effect(lambda: print(f"Count: {count}"), [count])
    input_ref = use_ref(None)
    return h("div", None, f"Count: {count}")
```

## Main API

- `h(type, props, *children)` creates a virtual element (`VNode`).
- `render(element, container)` renders an element into a DOM container.
- `create_root(container)` creates a modern rendering root.
- `hydrate_root(container, element)` hydrates an existing DOM tree without
  replacing matching nodes.
- `render_to_string(element)` renders hydratable server-side markup.
- `render_to_static_markup(element)` renders static HTML.
- `render_to_node_stream(element)` and `render_to_async_stream(element)` stream
  server-rendered markup.
- `Router`, `route`, `Link`, `use_location`, and `use_params` provide routing.
- `serve(...)` starts the server-driven production runtime.

Routing is explicit and dependency-free:

```python
from pyreact import Link, Router, h, route, use_params


def User(props):
    return h("h1", None, f"User {use_params()['user_id']}")


def App(props):
    return h("main", None,
        h(Link, {"to": "/users/42"}, "Profile"),
        h(Router, {
            "routes": [route("/users/:user_id", User)],
            "fallback": h("h1", None, "Not found"),
        }),
    )
```

See the complete [API reference](https://pyreact-framework.readthedocs.io/en/latest/).

## CLI

```bash
pyreact create <name>
pyreact dev [--host HOST] [--port PORT] [--no-open]
pyreact generate component <name>
pyreact generate hook <name>
pyreact build
```

## Testing

```bash
# Complete test suite
python -m pytest -q

# End-to-end tests
python -m pytest tests/e2e -q

# Coverage
python -m pytest --cov=pyreact --cov-report=term-missing
```

See the [execution and testing guide](docs/GUIA_EXECUCAO_E_TESTES.md).

## Project layout

```text
pyreact/
├── pyreact/              # Framework source
│   ├── cli/              # Command-line interface
│   ├── core/             # Components, hooks, and VNodes
│   ├── dom/              # DOM operations
│   ├── server/           # Server-side rendering
│   └── utils/            # Utilities
├── tests/                # Unit and end-to-end tests
├── examples/             # Usage examples
├── boilerplate/          # Complete generated application
├── docs/                 # Sphinx and Markdown documentation
├── pyproject.toml
└── LICENSE
```

## Development

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -e ".[dev,e2e]"
python -m playwright install chromium
python -m pytest -q
python -m build
```

## Publishing

Pull requests and pushes to `master` run the Python matrix, enforce at least
95% line coverage, execute browser tests, and build validated distributions.
Only a `v*` tag publishes to PyPI through Trusted Publishing (OIDC), so the
repository does not store a permanent upload token. See the
[automatic publishing guide](docs/PUBLICACAO_AUTOMATICA.md).

## Contributing

Contributions are welcome:

1. Fork the repository.
2. Create a focused branch.
3. Include tests with your change.
4. Run the complete test suite.
5. Open a pull request explaining the problem and solution.

## Documentation

The complete English documentation is published at
<https://pyreact-framework.readthedocs.io/>.

## License

PyReact is licensed under the MIT License. See [LICENSE](LICENSE).
