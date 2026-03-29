.. _ssr:

Server-Side Rendering (SSR)
============================

PyReact supports Server-Side Rendering (SSR) for improved SEO and initial load performance.

What is SSR?
------------

SSR renders your PyReact components on the server and sends the HTML to the client. This provides:

- **Better SEO** - Search engines can crawl your content
- **Faster initial load** - Users see content immediately
- **Better performance** - Reduced client-side JavaScript

Enabling SSR
------------

Enable SSR in your ``pyproject.toml``:

.. code-block:: toml

   [tool.pyreact]
   ssr = true

SSR Configuration
-----------------

Configure SSR in your project:

.. code-block:: python
   :caption: src/server.py

   from pyreact import render_to_string
   from my_app import App

   def handler(request):
       # Render app to HTML string
       html = render_to_string(element(App, {}))
       
       return {
           'status': 200,
           'headers': {'Content-Type': 'text/html'},
           'body': f'''
           <!DOCTYPE html>
           <html>
           <head>
               <title>My PyReact App</title>
           </head>
           <body>
               <div id="root">{html}</div>
               <script src="/static/client.js"></script>
           </body>
           </html>
           '''
       }

Hydration
---------

Hydration attaches event listeners to server-rendered HTML:

.. code-block:: python
   :caption: src/index.py

   from pyreact import hydrate
   from my_app import App

   # Hydrate the server-rendered HTML
   hydrate(element(App, {}), root='root')

Data Fetching
-------------

Fetch data on the server:

.. code-block:: python

   from pyreact import element, Component

   class ProductList(Component):
       @staticmethod
       async def get_initial_props():
           # Fetch data on server
           import aiohttp
           async with aiohttp.ClientSession() as session:
               async with session.get('/api/products') as response:
                   return await response.json()
       
       def render(self):
           products = self.props.get('products', [])
           return element('div', {},
               *[element('div', {'key': p['id']},
                   element('h3', {}, p['name']),
                   element('p', {}, f"${p['price']}")
               ) for p in products]
           )

SSR Best Practices
------------------

1. **Avoid window/document** - These don't exist on the server
2. **Check for server environment** - Use conditional logic

.. code-block:: python

   import os

   class MyComponent(Component):
       def render(self):
           # Check if running on server
           if os.environ.get('SERVER_SIDE'):
               return element('div', {}, 'Server rendered')
           
           return element('div', {},
               element('canvas', {'ref': self.canvas_ref})
           )

3. **Handle async data** - Use ``get_initial_props`` for data fetching

SSR Limitations
---------------

- No access to browser APIs (window, document)
- No lifecycle methods during SSR
- State is initialized but not interactive until hydration

Next Steps
----------

- :doc:`/advanced/routing` - Add routing to your app
- :doc:`/advanced/styling` - Learn about styling
- :doc:`/api/component` - Component API reference
