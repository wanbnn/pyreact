# PyReact 1.0.5 correction and test report

Validation date: 2026-07-24

## Summary

The project was analyzed from a clean test-suite run. The initial run reported
12 failures and 6 errors. After the fixes and release-pipeline work, all 106
tests passed.

## Problems and fixes

### Component state

`Component.set_state()` previously kept the new state in a queue when no
renderer was connected. It now applies state synchronously in that scenario
and runs pending callbacks.

### Hooks

The hook cursor was global and could be shared across components. It now belongs
to the current component and resets on each render. `use_effect`, `use_ref`,
`use_memo`, and `use_id` preserve their values correctly between renders.

### Reconciliation and rendering

Functional components did not receive an updater, so `use_state` changes never
reached the DOM. The reconciler now connects mounted components, reapplies hooks,
updates child lists and text without duplication, and preserves DOM references.

### Server-side rendering

`render_to_string()` omitted `data-reactroot` when the root had no properties.
The marker is now emitted only on the root element.
`render_to_static_markup()` continues to omit hydration markers.

### Testing utilities

`pyreact.testing` imports pointed to missing modules. The test renderer now
mounts the real tree, connects `screen`, supports `rerender()` and `cleanup()`,
and forwards events to DOM listeners.

### CLI and generated projects

- Added the `pyreact` console entry while preserving `pyreact-framework`.
- Added `public/index.html` and `public/.gitkeep` to the scaffold.
- Added `--no-open` to `dev` for CI environments.
- Made `build` produce a usable `dist`.
- Fixed generated hooks that incorrectly used `use_effect` as a decorator.
- Aligned the public version at 1.0.5.

### End-to-end tests

The old tests relied on an installed executable, fixed directories, sleeps, and
fixed ports. Their isolated replacements create temporary projects, select a
free port, wait for the server, validate generation and builds, exercise the
counter in Chromium, and always stop the server.

## Final result

```bash
python -m pytest -q
```

```text
106 passed
```

Package loading, reactive rendering, the CLI, HTTP server, production build,
and real browser interaction were also verified.
