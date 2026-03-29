.. _state:

State
=====

State represents data that can change over time. Unlike props, state is managed by the component itself and can be updated.

Initializing State
------------------

Initialize state in the constructor:

.. code-block:: python

   from pyreact import element, Component

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}

Updating State
--------------

Use ``setState()`` to update state:

.. code-block:: python

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def increment(self, event):
           # ✅ Correct: Use setState
           self.setState({'count': self.state['count'] + 1})
       
       def bad_increment(self, event):
           # ❌ Wrong: Never modify state directly
           self.state['count'] += 1  # Don't do this!

State Updates are Merged
------------------------

``setState()`` merges the new state with the existing state:

.. code-block:: python

   class Form(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {
               'name': '',
               'email': '',
               'age': 0
           }
       
       def update_name(self, event):
           # Only updates 'name', preserves 'email' and 'age'
           self.setState({'name': event.target.value})
       
       def update_email(self, event):
           self.setState({'email': event.target.value})

Functional Updates
------------------

When new state depends on previous state, use a function:

.. code-block:: python

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def increment(self, event):
           # Use function for derived state
           self.setState(lambda state: {'count': state['count'] + 1})
       
       def increment_three_times(self, event):
           # Multiple updates
           self.setState(lambda state: {'count': state['count'] + 1})
           self.setState(lambda state: {'count': state['count'] + 1})
           self.setState(lambda state: {'count': state['count'] + 1})

State is Local
--------------

State is local to the component:

.. code-block:: python

   class App(Component):
       def render(self):
           return element('div', {},
               element(Counter, {}),  # Has its own state
               element(Counter, {}),  # Has its own state
               element(Counter, {})   # Has its own state
           )

Lifting State Up
----------------

Share state between components by lifting it to their common ancestor:

.. code-block:: python

   class App(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'temperature': 0}
       
       def handle_change(self, temp):
           self.setState({'temperature': temp})
       
       def render(self):
           return element('div', {},
               element(TemperatureInput, {
                   'temperature': self.state['temperature'],
                   'onChange': self.handle_change
               }),
               element(BoilingVerdict, {
                   'celsius': self.state['temperature']
               })
           )

State vs Props
--------------

.. list-table:: 
   :widths: 50 50
   :header-rows: 1

   * - Props
     - State
   * - Passed from parent
     - Managed by component
   * - Read-only
     - Can be updated
   * - Used for configuration
     - Used for dynamic data
   * - External to component
     - Internal to component

Best Practices
--------------

1. **Minimize state** - Keep state as simple as possible
2. **Lift state up** - Share state by lifting to common ancestor
3. **Don't duplicate state** - Compute derived values instead
4. **Use setState** - Never modify state directly

Next Steps
----------

- :doc:`/concepts/events` - Learn about event handling
- :doc:`/api/hooks` - Explore built-in hooks
- :doc:`/concepts/lifecycle` - Learn about lifecycle methods
