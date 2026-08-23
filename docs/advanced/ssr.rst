.. _ssr:

SSR, Hydration and Streaming
============================

Server-side rendering evaluates functional and class components in Python and
returns escaped HTML. Functional components may use hooks during SSR; state is
initialized and IDs are deterministic, while effects are deferred until a DOM
commit.

Rendering HTML
--------------

.. code-block:: python

   from pyreact import h, render_to_static_markup, render_to_string, use_id

   def App(props):
       heading_id = use_id()
       return h("main", None,
           h("h1", {"id": heading_id}, props["title"]),
       )

   hydratable_html = render_to_string(h(App, {"title": "Dashboard"}))
   static_html = render_to_static_markup(h(App, {"title": "Dashboard"}))

``render_to_string`` adds a marker to the root for hydration.
``render_to_static_markup`` omits it and is appropriate for email or pages that
will never become interactive. Text and attributes are escaped. Raw HTML is
accepted only through ``dangerouslySetInnerHTML={"__html": value}`` and must be
trusted by the application.

Hydration
---------

Hydration attaches component state, refs, effects, and event handlers to an
existing matching DOM tree instead of recreating it:

.. code-block:: python

   from pyreact import h, hydrate_root, use_hydration

   def App(props):
       status = use_hydration()
       return h("p", None, "Hydrating" if status["is_hydrating"] else "Ready")

   root = hydrate_root(container, h(App, None))

The component tree used for hydration must produce the same h structure
as the server render. Matching DOM elements preserve their identity. The
``hydrate(h, container)`` form is also available.

Streaming
---------

Use the synchronous iterator when writing to a WSGI-like response and the
async iterator in an asynchronous server:

.. code-block:: python

   from pyreact import h, render_to_async_stream, render_to_node_stream

   for chunk in render_to_node_stream(h(App, {"title": "Dashboard"})):
       response.write(chunk)

   async for chunk in render_to_async_stream(h(App, {"title": "Dashboard"})):
       await response.write(chunk)

Static equivalents are available through ``render_to_static_node_stream``.
The iterators preserve the same escaping and hook semantics as string SSR.

Effects and Browser APIs
------------------------

SSR does not run effect callbacks or mount lifecycles because there is no DOM
commit. They run after render or hydration in the DOM renderer. Components
rendered directly through SSR should not read browser-only APIs while their
render function is executing.

Next Steps
----------

- :doc:`/advanced/runtime` - Understand browser sessions and hot reload
- :doc:`/advanced/routing` - Add application routes
- :doc:`/api/hooks` - Hook API
