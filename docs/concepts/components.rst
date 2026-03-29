.. _components:

Components
==========

Components are the building blocks of PyReact applications. They are reusable pieces of UI that can manage their own state and props.

Component Types
---------------

PyReact supports two types of components:

1. **Function Components** - Simple components defined as functions
2. **Class Components** - Complex components with state and lifecycle methods

Function Components
-------------------

Function components are simple and concise:

.. code-block:: python

   from pyreact import element

   def Greeting(props):
       name = props.get('name', 'World')
       return element('h1', {}, f'Hello, {name}!')

   # Usage
   element(Greeting, {'name': 'PyReact'})

Class Components
----------------

Class components offer more features:

.. code-block:: python

   from pyreact import element, Component

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def increment(self, event):
           self.setState({'count': self.state['count'] + 1})
       
       def render(self):
           return element('div', {},
               element('p', {}, f'Count: {self.state["count"]}'),
               element('button', {'onClick': self.increment}, 'Increment')
           )

Component Lifecycle
-------------------

Class components have lifecycle methods:

.. code-block:: python

   class MyComponent(Component):
       def component_did_mount(self):
           """Called after the component is mounted"""
           print('Component mounted')
       
       def component_did_update(self, prev_props, prev_state):
           """Called after the component updates"""
           print('Component updated')
       
       def component_will_unmount(self):
           """Called before the component is unmounted"""
           print('Component will unmount')
       
       def render(self):
           return element('div', {}, 'My Component')

Component Composition
---------------------

Components can be composed together:

.. code-block:: python

   def Header(props):
       return element('header', {},
           element('h1', {}, props['title'])
       )
   
   def Footer(props):
       return element('footer', {},
           element('p', {}, props['text'])
       )
   
   def App(props):
       return element('div', {},
           element(Header, {'title': 'My App'}),
           element('main', {}, 'Content goes here'),
           element(Footer, {'text': '© 2026'})
       )

Best Practices
--------------

1. **Keep components small** - Each component should do one thing well
2. **Use meaningful names** - Component names should be descriptive
3. **Reuse components** - Create reusable components for common patterns
4. **Lift state up** - Share state between components by lifting it to their common ancestor

Next Steps
----------

- :doc:`/concepts/props` - Learn about props
- :doc:`/concepts/state` - Learn about state management
- :doc:`/api/component` - Component API reference
