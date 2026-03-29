.. _lifecycle:

Lifecycle Methods
=================

Lifecycle methods allow you to run code at specific times in a component's life.

Mounting
--------

Methods called when a component is being added to the DOM:

``component_did_mount()``
~~~~~~~~~~~~~~~~~~~~~~~~~

Called immediately after the component is mounted. Use this for:

- Fetching data
- Setting up subscriptions
- Adding event listeners

.. code-block:: python

   class DataFetcher(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'data': None, 'loading': True}
       
       def component_did_mount(self):
           # Fetch data when component mounts
           self.fetch_data()
       
       async def fetch_data(self):
           # Simulated data fetch
           import asyncio
           await asyncio.sleep(1)
           self.setState({
               'data': {'message': 'Hello from API'},
               'loading': False
           })
       
       def render(self):
           if self.state['loading']:
               return element('div', {}, 'Loading...')
           
           return element('div', {}, self.state['data']['message'])

Updating
--------

Methods called when a component is being re-rendered:

``component_did_update(prev_props, prev_state)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Called after the component updates. Use this for:

- Responding to prop changes
- Network requests based on new data
- DOM updates

.. code-block:: python

   class UserProfile(Component):
       def component_did_update(self, prev_props, prev_state):
           # Fetch new data when user ID changes
           if prev_props.get('userId') != self.props.get('userId'):
               self.fetch_user_data()
       
       def fetch_user_data(self):
           user_id = self.props['userId']
           print(f'Fetching data for user {user_id}')
       
       def render(self):
           return element('div', {}, f'User: {self.props["userId"]}')

``should_component_update(nextProps, nextState)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Called before rendering. Return ``False`` to skip rendering:

.. code-block:: python

   class ExpensiveComponent(Component):
       def should_component_update(self, next_props, next_state):
           # Only update if data actually changed
           return self.props['data'] != next_props['data']
       
       def render(self):
           # Expensive rendering operation
           return element('div', {}, 'Expensive content')

Unmounting
----------

Methods called when a component is being removed from the DOM:

``component_will_unmount()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Called immediately before the component is unmounted. Use this for:

- Cleaning up subscriptions
- Canceling network requests
- Removing event listeners

.. code-block:: python

   class Timer(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'seconds': 0}
           self.timer_id = None
       
       def component_did_mount(self):
           self.timer_id = self.start_timer()
       
       def component_will_unmount(self):
           # Clean up timer
           if self.timer_id:
               self.stop_timer(self.timer_id)
       
       def start_timer(self):
           import threading
           def tick():
               self.setState({'seconds': self.state['seconds'] + 1})
           
           timer = threading.Timer(1.0, tick)
           timer.start()
           return timer
       
       def stop_timer(self, timer_id):
           timer_id.cancel()
       
       def render(self):
           return element('div', {}, f'Seconds: {self.state["seconds"]}')

Error Handling
--------------

Methods for handling errors during rendering:

``component_did_catch(error, info)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Called when an error is thrown during rendering:

.. code-block:: python

   class ErrorBoundary(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'has_error': False, 'error': None}
       
       def component_did_catch(self, error, info):
           # Log error to service
           print(f'Error: {error}')
           print(f'Info: {info}')
           
           self.setState({
               'has_error': True,
               'error': error
           })
       
       def render(self):
           if self.state['has_error']:
               return element('div', {'class': 'error'},
                   element('h2', {}, 'Something went wrong'),
                   element('p', {}, str(self.state['error']))
               )
           
           return self.props.get('children', [])

Lifecycle Diagram
-----------------

.. code-block:: text

   Mounting:
   constructor → render → component_did_mount
   
   Updating:
   new props/state → should_component_update → render → component_did_update
   
   Unmounting:
   component_will_unmount

Best Practices
--------------

1. **Clean up in will_unmount** - Always clean up subscriptions and timers
2. **Avoid side effects in constructor** - Use ``component_did_mount`` instead
3. **Use should_component_update** - Optimize performance for expensive renders
4. **Handle errors** - Use error boundaries for better error handling

Next Steps
----------

- :doc:`/api/component` - Component API reference
- :doc:`/advanced/testing` - Test lifecycle methods
- :doc:`/concepts/state` - Learn about state management
