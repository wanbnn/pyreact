# Automatic publishing to PyPI

The `.github/workflows/publish.yml` workflow validates pull requests, pushes to
`master`, version tags, and manual runs. Publishing itself only occurs for a
tag whose name starts with `v`.

## Validation flow

1. Run unit tests on Python 3.10, 3.11, 3.12, and 3.13.
2. Enforce at least 95% line coverage of the `pyreact` package.
3. Install Chromium and run the generated-project and boilerplate browser tests.
4. Build the wheel and source distribution.
5. Validate both distributions with `twine check`.
6. Upload the build as a GitHub Actions artifact.

Any failure prevents publication.

## Publishing a release

Keep `pyproject.toml` and `pyreact/__init__.py` on the same version, commit the
release, and create a matching tag:

```bash
git tag v1.1.0
git push origin v1.1.0
```

The package version remains the explicit project version; CI does not rewrite
source files or create implicit post-releases.

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

The tag-triggered publish job requests a short-lived OIDC credential through
that environment. Manual workflow runs perform validation and produce an
artifact but do not publish.
