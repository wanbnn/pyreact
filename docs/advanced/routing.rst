.. _routing:

Routing
=======

PyReact provides a built-in router for Single Page Applications (SPAs).

Basic Routing
-------------

Set up routing in your app:

.. code-block:: python

   from pyreact import element, Component
   from pyreact.router import Router, Route, Link

   class App(Component):
       def render(self):
           return element(Router, {},
               element('nav', {},
                   element(Link, {'to': '/'}, 'Home'),
                   element(Link, {'to': '/about'}, 'About'),
                   element(Link, {'to': '/contact'}, 'Contact')
               ),
               element('main', {},
                   element(Route, {'path': '/', 'component': Home}),
                   element(Route, {'path': '/about', 'component': About}),
                   element(Route, {'path': '/contact', 'component': Contact})
               )
           )

Route Parameters
----------------

Access route parameters:

.. code-block:: python

   from pyreact.router import useParams

   class UserProfile(Component):
       def render(self):
           params = useParams()
           user_id = params['id']
           
           return element('div', {},
               element('h1', {}, f'User Profile: {user_id}'),
               element('p', {}, 'User details here...')
           )

   # Route definition
   element(Route, {
       'path': '/users/:id',
       'component': UserProfile
   })

Query Parameters
----------------

Access query parameters:

.. code-block:: python

   from pyreact.router import useLocation

   class SearchResults(Component):
       def render(self):
           location = useLocation()
           query = location.get('query', '')
           page = int(location.get('page', 1))
           
           return element('div', {},
               element('h1', {}, f'Search: {query}'),
               element('p', {}, f'Page {page}')
           )

Nested Routes
-------------

Create nested routes:

.. code-block:: python

   class Dashboard(Component):
       def render(self):
           return element('div', {'class': 'dashboard'},
               element('aside', {},
                   element(Link, {'to': '/dashboard'}, 'Overview'),
                   element(Link, {'to': '/dashboard/settings'}, 'Settings'),
                   element(Link, {'to': '/dashboard/profile'}, 'Profile')
               ),
               element('main', {},
                   element(Route, {'path': '/dashboard', 'exact': True, 'component': DashboardHome}),
                   element(Route, {'path': '/dashboard/settings', 'component': Settings}),
                   element(Route, {'path': '/dashboard/profile', 'component': Profile})
               )
           )

Programmatic Navigation
-----------------------

Navigate programmatically:

.. code-block:: python

   from pyreact.router import useHistory

   class LoginForm(Component):
       def __init__(self, props):
           super().__init__(props)
           self.history = useHistory()
       
       def handle_submit(self, event):
           event.preventDefault()
           # Perform login
           success = self.login()
           
           if success:
               # Redirect to dashboard
               self.history.push('/dashboard')
       
       def render(self):
           return element('form', {'onSubmit': self.handle_submit},
               # ... form fields
           )

Route Guards
------------

Protect routes with guards:

.. code-block:: python

   from pyreact.router import Route, Redirect

   class PrivateRoute(Component):
       def render(self):
           is_authenticated = self.props.get('isAuthenticated', False)
           
           if not is_authenticated:
               return element(Redirect, {'to': '/login'})
           
           Component = self.props['component']
           return element(Component, self.props)

   # Usage
   element(PrivateRoute, {
       'path': '/dashboard',
       'component': Dashboard,
       'isAuthenticated': user.is_authenticated
   })

404 Not Found
-------------

Handle 404 pages:

.. code-block:: python

   from pyreact.router import Switch, Route

   class App(Component):
       def render(self):
           return element(Router, {},
               element(Switch, {},
                   element(Route, {'path': '/', 'component': Home}),
                   element(Route, {'path': '/about', 'component': About}),
                   element(Route, {'component': NotFound})  # 404 fallback
               )
           )

   class NotFound(Component):
       def render(self):
           return element('div', {'class': 'not-found'},
               element('h1', {}, '404 - Page Not Found'),
               element(Link, {'to': '/'}, 'Go Home')
           )

Best Practices
--------------

1. **Use meaningful routes** - ``/users/123`` instead of ``/u/123``
2. **Handle 404s** - Always provide a fallback route
3. **Protect sensitive routes** - Use route guards
4. **Lazy load routes** - Improve performance with code splitting

Next Steps
----------

- :doc:`/advanced/ssr` - Server-side rendering
- :doc:`/advanced/styling` - Styling options
- :doc:`/api/hooks` - Router hooks
