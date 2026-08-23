.. _routing:

Routing
=======

PyReact includes a dependency-free router integrated with the server-driven
runtime and the browser History API.

Route Table
-----------

.. code-block:: python

   from pyreact import Link, Router, h, route, use_location, use_params

   def Home(props):
       return h("h1", None, "Home")

   def User(props):
       params = use_params()
       location = use_location()
       return h("section", None,
           h("h1", None, f"User {params['user_id']}"),
           h("p", None, f"Query: {location.search}"),
       )

   def NotFound(props):
       return h("h1", {"role": "alert"}, "Not found")

   routes = [
       route("/", Home),
       route("/users/:user_id", User),
   ]

   def App(props):
       return h("main", None,
           h("nav", None,
               h(Link, {"to": "/"}, "Home"),
               h(Link, {"to": "/users/42?tab=profile"}, "Profile"),
           ),
           h(Router, {"routes": routes, "fallback": NotFound}),
       )

Routes match exactly by default. Pass ``exact=False`` to ``route`` for a
prefix route. Named segments use ``:name`` and a trailing ``*`` captures the
remaining path in ``wildcard``.

Location and Parameters
-----------------------

``use_params()`` returns a copy of the parameters for the active route.
``use_location()`` returns an immutable ``Location`` with ``pathname``, raw
``search``, and parsed ``query`` values. Query values are lists so repeated
parameters are preserved.

Links and Redirects
-------------------

``Link`` renders an anchor marked for client-side navigation. The runtime
uses ``history.pushState`` and requests the destination without a full page
load. ``Navigate`` emits an immediate refresh marker and is useful for simple
server-side redirects:

.. code-block:: python

   from pyreact import Navigate, h

   def PrivatePage(props):
       if not props.get("authenticated"):
           return h(Navigate, {"to": "/login"})
       return h("h1", None, "Private page")

For unit tests or custom SSR adapters, use ``routing_context(url)`` from
``pyreact.routing`` while rendering.
