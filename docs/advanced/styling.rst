.. _styling:

Styling
=======

PyReact supports multiple styling approaches for your components.

Inline Styles
-------------

Apply styles directly to elements:

.. code-block:: python

   from pyreact import h

   def StyledButton(props):
       return h('button', {
           'style': {
               'backgroundColor': '#007bff',
               'color': 'white',
               'padding': '10px 20px',
               'border': 'none',
               'borderRadius': '5px',
               'cursor': 'pointer'
           }
       }, 'Click me')

CSS Classes
-----------

Use CSS classes for styling:

.. code-block:: python

   # Component
   def Card(props):
       return h('div', {'class': 'card'},
           h('h2', {'class': 'card-title'}, props['title']),
           h('p', {'class': 'card-body'}, props['children'])
       )

.. code-block:: css
   :caption: styles/main.css

   .card {
       border: 1px solid #ddd;
       border-radius: 8px;
       padding: 20px;
       margin: 10px 0;
   }
   
   .card-title {
       font-size: 24px;
       margin-bottom: 10px;
   }
   
   .card-body {
       color: #666;
   }

CSS Modules
-----------

Enable CSS Modules in ``pyproject.toml``:

.. code-block:: toml

   [tool.pyreact]
   css_modules = true

Use CSS Modules in components:

.. code-block:: python

   from pyreact import h
   from styles import CardStyles  # Import CSS module

   def Card(props):
       return h('div', {'class': CardStyles.card},
           h('h2', {'class': CardStyles.title}, props['title']),
           h('p', {'class': CardStyles.body}, props['children'])
       )

.. code-block:: css
   :caption: styles/CardStyles.module.css

   .card {
       border: 1px solid #ddd;
       border-radius: 8px;
       padding: 20px;
   }
   
   .title {
       font-size: 24px;
       color: #333;
   }

Styled Components
-----------------

Create styled components:

.. code-block:: python

   from pyreact import styled

   # Create styled button
   Button = styled('button', '''
       background-color: #007bff;
       color: white;
       padding: 10px 20px;
       border: none;
       border-radius: 5px;
       cursor: pointer;
       
       &:hover {
           background-color: #0056b3;
       }
       
       &:disabled {
           background-color: #ccc;
           cursor: not-allowed;
       }
   ''')

   # Usage
   h(Button, {'disabled': False}, 'Click me')

Theming
-------

Implement theming:

.. code-block:: python

   from pyreact import h, Component, ThemeProvider

   class App(Component):
       def render(self):
           theme = {
               'primary': '#007bff',
               'secondary': '#6c757d',
               'success': '#28a745',
               'danger': '#dc3545',
               'warning': '#ffc107',
               'info': '#17a2b8',
               'light': '#f8f9fa',
               'dark': '#343a40'
           }
           
           return h(ThemeProvider, {'theme': theme},
               h(ThemedButton, {})
           )

   class ThemedButton(Component):
       def render(self):
           theme = self.use_theme()
           
           return h('button', {
               'style': {
                   'backgroundColor': theme['primary'],
                   'color': 'white'
               }
           }, 'Themed Button')

Responsive Design
-----------------

Create responsive layouts:

.. code-block:: python

   from pyreact import h

   def ResponsiveGrid(props):
       items = props.get('items', [])
       
       return h('div', {
           'style': {
               'display': 'grid',
               'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))',
               'gap': '20px',
               'padding': '20px'
           }
       },
           *[h('div', {
               'style': {
                   'border': '1px solid #ddd',
                   'padding': '20px',
                   'borderRadius': '8px'
               }
           }, item) for item in items]
       )

Best Practices
--------------

1. **Use CSS Modules** - Scoped styles prevent conflicts
2. **Avoid inline styles** - Use classes for better performance
3. **Use a theme** - Centralize colors and spacing
4. **Make it responsive** - Design for all screen sizes

Next Steps
----------

- :doc:`/advanced/ssr` - Server-side rendering
- :doc:`/advanced/testing` - Testing components
- :doc:`/api/element` - Element API reference
