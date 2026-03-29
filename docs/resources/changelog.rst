.. _changelog:

Changelog
=========

All notable changes to PyReact Framework are documented here.

Version 1.0.1 (2026-03-28)
---------------------------

Fixed
~~~~~

- Updated README with correct GitHub username (wanbnn)
- Fixed PyPI badges to use correct package name (pyreact-framework)
- Updated project URLs in pyproject.toml

Version 1.0.0 (2026-03-28)
---------------------------

Added
~~~~~

- Initial stable release
- Core component system with Element API
- Class components with state management
- Function components with hooks
- Lifecycle methods (component_did_mount, component_did_update, component_will_unmount)
- Event handling system
- Built-in router for SPAs
- CSS Modules support
- Server-side rendering (SSR)
- Hot module replacement for development
- CLI tools (create, dev, build, serve, test)
- Comprehensive test suite
- Full documentation

Features
~~~~~~~~

**Components**

- Element creation with ``element()`` function
- Class components extending ``Component``
- Function components
- Props and state management
- Component composition

**Hooks**

- ``useState`` - State management
- ``useEffect`` - Side effects
- ``useContext`` - Context API
- ``useRef`` - Mutable references
- ``useMemo`` - Memoization
- ``useCallback`` - Callback memoization
- ``useReducer`` - Complex state logic

**Routing**

- Declarative routing
- Route parameters
- Query parameters
- Nested routes
- Route guards
- Programmatic navigation

**Styling**

- Inline styles
- CSS classes
- CSS Modules
- Styled components
- Theming support

**Developer Experience**

- Hot reload
- Error boundaries
- Source maps
- TypeScript-like type hints
- Comprehensive error messages

Documentation
~~~~~~~~~~~~~

- Getting Started guide
- Tutorial (Todo app)
- API reference
- Advanced topics
- FAQ

Roadmap
-------

Version 1.1.0 (Planned)
~~~~~~~~~~~~~~~~~~~~~~~

- TypeScript support
- More hooks (useTransition, useDeferredValue)
- Improved SSR performance
- Better error messages
- More examples

Version 1.2.0 (Planned)
~~~~~~~~~~~~~~~~~~~~~~~

- Animation library
- Form validation
- Internationalization (i18n)
- State management library
- Component library

Version 2.0.0 (Future)
~~~~~~~~~~~~~~~~~~~~~~

- Concurrent rendering
- Suspense for data fetching
- Server components
- Streaming SSR
- New architecture

Contributing
------------

We welcome contributions! See :doc:`/resources/contributing` for guidelines.

Versioning
----------

PyReact follows `Semantic Versioning <https://semver.org/>`_:

- **MAJOR** version for incompatible API changes
- **MINOR** version for new features (backwards compatible)
- **PATCH** version for bug fixes (backwards compatible)

Previous Versions
-----------------

- **1.0.0** - Initial stable release (2026-03-28)

Next Steps
----------

- :doc:`/getting-started/installation` - Install PyReact
- :doc:`/getting-started/quickstart` - Quick start guide
- :doc:`/resources/contributing` - Contribute to PyReact
