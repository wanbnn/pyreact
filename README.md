# 🐍 PyReact — Declarative Web Framework for Python

[![PyPI version](https://badge.fury.io/py/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![Python](https://img.shields.io/pypi/pyversions/pyreact-framework.svg)](https://pypi.org/project/pyreact-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://readthedocs.org/projects/pyreact-framework/badge/?version=latest)](https://pyreact-framework.readthedocs.io/en/latest/)

**PyReact** is a React-inspired declarative web framework built natively for
Python. It provides reactive user interfaces, components, hooks, efficient
rendering, server-side rendering, and a project CLI.

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

A functional counter:

```python
from pyreact import h, render, use_state


def Counter(props):
    count, set_count = use_state(0)

    return h(
        "div",
        {"className": "counter"},
        h("h1", None, f"Count: {count}"),
        h("button", {"onClick": lambda: set_count(count + 1)}, "+"),
        h("button", {"onClick": lambda: set_count(count - 1)}, "-"),
    )


root = document.getElementById("root")
render(h(Counter, None), root)
```

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
            {"onClick": lambda: self.set_state({"count": self.state["count"] + 1})},
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
- `render_to_string(element)` renders hydratable server-side markup.
- `render_to_static_markup(element)` renders static HTML.

See the complete [API reference](https://pyreact-framework.readthedocs.io/en/latest/).

## CLI

```bash
pyreact create <name>
pyreact dev [--port PORT] [--no-open]
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

Every push to `master` runs tests, builds distributions, and publishes to PyPI
through GitHub Actions. Authentication uses PyPI Trusted Publishing (OIDC), so
the repository does not store a permanent upload token. See the
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
