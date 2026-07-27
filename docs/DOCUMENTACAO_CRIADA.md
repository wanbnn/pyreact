# PyReact documentation structure

PyReact uses Sphinx and MyST to publish its English documentation on Read the
Docs.

## Main files

- `.readthedocs.yaml` defines the Read the Docs v2 environment.
- `docs/conf.py` configures Sphinx, the theme, extensions, and metadata.
- `docs/requirements.txt` contains documentation-only dependencies.
- `docs/index.rst` is the documentation home page and main table of contents.
- `README.md` provides the repository overview and quick start.

## Published sections

- **Getting Started:** installation, quick start, and tutorial.
- **Core Concepts:** components, props, state, events, and lifecycle.
- **Advanced:** server-side rendering, routing, styling, and testing.
- **API Reference:** elements, components, hooks, and CLI.
- **Resources:** FAQ, changelog, and contributing guide.

Operational Markdown guides cover automatic PyPI publishing, local execution
and testing, and the 1.0.5 correction report.

## Build locally

```bash
python -m pip install -r docs/requirements.txt
python -m pip install -e .
sphinx-build -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` to inspect the result.

## Publish on Read the Docs

1. Sign in to Read the Docs with GitHub.
2. Import the `wanbnn/pyreact` repository.
3. Keep English as the project language.
4. Build the `latest` version.

Read the Docs detects `.readthedocs.yaml`, installs the declared requirements
and package, builds from `docs/conf.py`, and publishes the result at
<https://pyreact-framework.readthedocs.io/>.

Automatic builds can be enabled for pull requests and pushes from the project
admin panel.
