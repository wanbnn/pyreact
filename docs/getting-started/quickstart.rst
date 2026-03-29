.. _quickstart:

Quick Start
===========

Create your first PyReact application in less than 5 minutes.

Create a New Project
--------------------

Use the CLI to create a new project:

.. code-block:: bash

   pyreact-framework create my-app
   cd my-app

This creates a project structure:

.. code-block:: text

   my-app/
   ├── src/
   │   ├── index.py          # Entry point
   │   ├── components/       # Reusable components
   │   └── styles/           # CSS files
   ├── pyproject.toml        # Project configuration
   └── README.md

Start Development Server
------------------------

Start the development server with hot reload:

.. code-block:: bash

   pyreact-framework dev

The application will be available at ``http://localhost:3000``.

Your First Component
--------------------

Create a simple counter component:

.. code-block:: python
   :caption: src/components/Counter.py

   from pyreact import element, Component

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def increment(self, event):
           self.setState({'count': self.state['count'] + 1})
       
       def decrement(self, event):
           self.setState({'count': self.state['count'] - 1})
       
       def render(self):
           return element('div', {'class': 'counter'},
               element('h2', {}, f'Count: {self.state["count"]}'),
               element('button', {'onClick': self.decrement}, '-'),
               element('button', {'onClick': self.increment}, '+')
           )

Use the Component
-----------------

Import and use your component:

.. code-block:: python
   :caption: src/index.py

   from pyreact import element, render
   from components.Counter import Counter

   def App():
       return element('div', {'class': 'app'},
           element('h1', {}, 'My First PyReact App'),
           element(Counter, {})
       )

   render(App(), root='root')

Build for Production
--------------------

Build your application for production:

.. code-block:: bash

   pyreact-framework build

The build output will be in the ``dist/`` directory.

Next Steps
----------

- :doc:`/getting-started/tutorial` - Learn PyReact in depth
- :doc:`/concepts/components` - Understand components
- :doc:`/api/hooks` - Explore built-in hooks
