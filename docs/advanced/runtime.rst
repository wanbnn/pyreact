.. _runtime:

Execution Model
===============

PyReact is server-driven: Python remains the authoritative execution
environment and is not transpiled to JavaScript. Each browser session owns a
live component tree with its own hook and class-component state.

Request and Event Flow
----------------------

1. The browser requests a route.
2. Python creates or reuses the session and renders complete HTML.
3. A small built-in browser runtime delegates events marked by PyReact.
4. The event and serializable form/input data are posted to the session.
5. Python invokes the handler, reconciles state, and returns updated markup.
6. The browser applies the markup and preserves the current History API route.

Session cookies are ``HttpOnly`` and ``SameSite=Lax``. Application state lives
in server memory, so multi-process deployment requires sticky sessions or an
application-level shared state strategy.

Session Lifecycle and Memory Bounds
-----------------------------------

The public live runtime keeps browser state bounded by default. Inactive
sessions expire after 30 minutes and at most 1,024 sessions are retained by one
``LiveApplication`` process. When the capacity is reached, the least recently
used session is discarded before a new browser session is created. A browser
whose session has expired simply receives a fresh component tree on its next
request.

These limits can be tuned for application traffic and state size:

.. code-block:: python

   from pyreact import LiveApplication, serve

   application = LiveApplication(
       entry,
       public_dir,
       session_ttl=15 * 60,
       max_sessions=500,
   )

   serve(
       entry="src/index.py",
       session_ttl=15 * 60,
       max_sessions=500,
   )

The hard capacity makes per-process session retention predictable instead of
allowing abandoned browser sessions to accumulate for the lifetime of the
server.

Development and Hot Reload
--------------------------

Run the configured entry point with:

.. code-block:: bash

   pyreact dev --host 127.0.0.1 --port 3000

The server watches Python source modification times. A change reloads project
modules, clears stale component sessions, increments the runtime version, and
causes connected browsers to reload. The ``--port`` option overrides
``tool.pyreact.dev_port``.

Production Build
----------------

.. code-block:: bash

   pyreact build
   cd dist
   python serve.py

The build contains the Python source, public assets, project configuration,
and a production launcher bound to ``0.0.0.0:8000``. Deploy it as a Python
service behind the TLS reverse proxy of your choice.

Programmatic Server API
-----------------------

.. code-block:: python

   from pyreact import serve

   serve(
       entry="src/index.py",
       host="0.0.0.0",
       port=8000,
       public_dir="public",
       title="My application",
       session_ttl=30 * 60,
       max_sessions=1024,
   )

``LiveApplication`` and ``LiveSession`` are exported for embedding the runtime
in custom process managers or tests.
