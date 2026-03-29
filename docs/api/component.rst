.. _component:

Component API
=============

Components are the building blocks of PyReact applications.

Component Class
---------------

.. py:class:: Component(props)

   Base class for all PyReact components.

   :param props: Properties passed to the component
   :type props: dict

   Example:

   .. code-block:: python

      from pyreact import element, Component

      class MyComponent(Component):
          def __init__(self, props):
              super().__init__(props)
              self.state = {'count': 0}
          
          def render(self):
              return element('div', {}, f'Count: {self.state["count"]}')

State Management
----------------

.. py:method:: setState(state, callback=None)

   Updates the component's state and triggers a re-render.

   :param state: New state or function that returns new state
   :type state: dict | callable
   :param callback: Function to call after state is updated
   :type callback: callable, optional

   Example:

   .. code-block:: python

      class Counter(Component):
          def __init__(self, props):
              super().__init__(props)
              self.state = {'count': 0}
          
          def increment(self):
              # Update state
              self.setState({'count': self.state['count'] + 1})
          
          def increment_async(self):
              # Functional update
              self.setState(lambda state: {'count': state['count'] + 1})
          
          def increment_with_callback(self):
              # With callback
              self.setState(
                  {'count': self.state['count'] + 1},
                  lambda: print(f'Count is now {self.state["count"]}')
              )

.. py:attribute:: state

   The component's state object.

   :type: dict

   Example:

   .. code-block:: python

      def render(self):
          return element('div', {}, f'Count: {self.state["count"]}')

.. py:attribute:: props

   The component's props object (read-only).

   :type: dict

   Example:

   .. code-block:: python

      def render(self):
          return element('h1', {}, f'Hello, {self.props["name"]}')

Lifecycle Methods
-----------------

.. py:method:: component_did_mount()

   Called immediately after the component is mounted.

   Use for:
   - Fetching data
   - Setting up subscriptions
   - Adding event listeners

   Example:

   .. code-block:: python

      class DataFetcher(Component):
          def component_did_mount(self):
              self.fetch_data()
          
          async def fetch_data(self):
              # Fetch data from API
              pass

.. py:method:: component_did_update(prev_props, prev_state)

   Called after the component updates.

   :param prev_props: Previous props
   :type prev_props: dict
   :param prev_state: Previous state
   :type prev_state: dict

   Example:

   .. code-block:: python

      class UserViewer(Component):
          def component_did_update(self, prev_props, prev_state):
              if prev_props['userId'] != self.props['userId']:
                  self.fetch_user_data()

.. py:method:: component_will_unmount()

   Called immediately before the component is unmounted.

   Use for:
   - Cleaning up subscriptions
   - Canceling timers
   - Removing event listeners

   Example:

   .. code-block:: python

      class Timer(Component):
          def component_did_mount(self):
              self.timer_id = self.start_timer()
          
          def component_will_unmount(self):
              self.stop_timer(self.timer_id)

.. py:method:: should_component_update(next_props, next_state)

   Called before rendering. Return False to prevent re-render.

   :param next_props: Next props
   :type next_props: dict
   :param next_state: Next state
   :type next_state: dict
   :returns: Whether the component should update
   :rtype: bool

   Example:

   .. code-block:: python

      class OptimizedComponent(Component):
          def should_component_update(self, next_props, next_state):
              # Only update if data changed
              return self.props['data'] != next_props['data']

.. py:method:: component_did_catch(error, info)

   Called when an error is thrown during rendering.

   :param error: The error that was thrown
   :type error: Exception
   :param info: Information about the error
   :type info: dict

   Example:

   .. code-block:: python

      class ErrorBoundary(Component):
          def __init__(self, props):
              super().__init__(props)
              self.state = {'has_error': False}
          
          def component_did_catch(self, error, info):
              self.setState({'has_error': True})
              log_error(error, info)

Render Method
-------------

.. py:method:: render()

   Must be implemented by the component. Returns the element tree.

   :returns: The element tree to render
   :rtype: Element

   Example:

   .. code-block:: python

      class MyComponent(Component):
          def render(self):
              return element('div', {},
                  element('h1', {}, 'Title'),
                  element('p', {}, 'Content')
              )

Force Update
------------

.. py:method:: force_update(callback=None)

   Forces a re-render of the component.

   :param callback: Function to call after update
   :type callback: callable, optional

   Example:

   .. code-block:: python

      class MyComponent(Component):
          def some_method(self):
              # Force re-render without changing state
              self.force_update()

Function Components
-------------------

Function components are simpler:

.. py:function:: FunctionComponent(props)

   A function that takes props and returns an element.

   :param props: Properties passed to the component
   :type props: dict
   :returns: An element tree
   :rtype: Element

   Example:

   .. code-block:: python

      def Greeting(props):
          name = props.get('name', 'World')
          return element('h1', {}, f'Hello, {name}!')

Best Practices
--------------

1. **Keep components small** - Each component should do one thing
2. **Lift state up** - Share state by lifting to common ancestor
3. **Use should_component_update** - Optimize performance
4. **Clean up in will_unmount** - Always clean up subscriptions

Next Steps
----------

- :doc:`/api/hooks` - Hooks API reference
- :doc:`/concepts/state` - Learn about state
- :doc:`/concepts/lifecycle` - Learn about lifecycle
