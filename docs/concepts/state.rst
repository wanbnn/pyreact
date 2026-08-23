.. _state:

State
=====

State represents data that can change over time. Unlike props, state is managed by the component itself and can be updated.

Initializing State
------------------

Initialize state in the constructor:

.. code-block:: python

   from pyreact import h, Component

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}

Updating State
--------------

Use ``set_state()`` to update state:

.. code-block:: python

   class Counter(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def increment(self, event):
           # ✅ Correct: Use set_state
           self.set_state({'count': self.state['count'] + 1})
       
       def bad_increment(self, event):
           # ❌ Wrong: Never modify state directly
           self.state['count'] += 1  # Don't do this!

State Updates are Merged
------------------------

``set_state()`` merges the new state with the existing state:

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
           self.set_state({'name': event.target.value})
       
       def update_email(self, event):
           self.set_state({'email': event.target.value})

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
           self.set_state(lambda state: {'count': state['count'] + 1})
       
       def increment_three_times(self, event):
           # Multiple updates
           self.set_state(lambda state: {'count': state['count'] + 1})
           self.set_state(lambda state: {'count': state['count'] + 1})
           self.set_state(lambda state: {'count': state['count'] + 1})

State is Local
--------------

State is local to the component:

.. code-block:: python

   class App(Component):
       def render(self):
           return h('div', {},
               h(Counter, {}),  # Has its own state
               h(Counter, {}),  # Has its own state
               h(Counter, {})   # Has its own state
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
           self.set_state({'temperature': temp})
       
       def render(self):
           return h('div', {},
               h(TemperatureInput, {
                   'temperature': self.state['temperature'],
                   'onChange': self.handle_change
               }),
               h(BoilingVerdict, {
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
4. **Use set_state** - Never modify state directly

Next Steps
----------

- :doc:`/concepts/events` - Learn about event handling
- :doc:`/api/hooks` - Explore built-in hooks
- :doc:`/concepts/lifecycle` - Learn about lifecycle methods
