# Automatic publishing to PyPI

The `.github/workflows/publish.yml` workflow runs on every push to `master`.

## Flow

1. Install PyReact and its development dependencies.
2. Install Chromium for the end-to-end tests.
3. Run the framework and boilerplate tests.
4. Generate a unique PEP 440 version from the base version:
   `1.0.5.post<run ID>`.
5. Build the wheel and source distribution.
6. Validate artifacts with `twine check`.
7. Publish to PyPI with a temporary OIDC credential.

Publishing is skipped if any test or validation fails.

## One-time PyPI setup

Do not add permanent PyPI tokens to GitHub secrets. In the
`pyreact-framework` project on PyPI:

1. Open **Manage → Publishing**.
2. Add a **GitHub Trusted Publisher**.
3. Enter:

| Field | Value |
| --- | --- |
| Owner | `wanbnn` |
| Repository | `pyreact` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

After saving, rerun any workflow that failed before this configuration.

## Versioning

The version in `pyproject.toml` is the base for the next publishing series.
Every automatic run creates a unique post-release, for example:

```text
1.0.5.post1234501
1.0.5.post1234601
```

To start a new stable series, update `pyproject.toml` and
`pyreact/__init__.py` to the same version, such as `1.0.6`.

## Manual run

The workflow can also be started from **Actions → Test and publish PyReact →
Run workflow**. Publishing only occurs when the run targets `master`.
