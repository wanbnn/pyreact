.. _hooks:

Hooks API
=========

Hooks let you use state and other features in function components.

useState
--------

.. py:function:: useState(initial_value)

   Adds state to a function component.

   :param initial_value: Initial state value
   :type initial_value: any
   :returns: Tuple of (current_value, setter_function)
   :rtype: tuple

   Example:

   .. code-block:: python

      from pyreact import element, useState

      def Counter(props):
          count, set_count = useState(0)
          
          def increment():
              set_count(count + 1)
          
          return element('div', {},
              element('p', {}, f'Count: {count}'),
              element('button', {'onClick': increment}, 'Increment')
          )

   Functional updates:

   .. code-block:: python

      def Counter(props):
          count, set_count = useState(0)
          
          def increment():
              # Use function for derived state
              set_count(lambda prev: prev + 1)
          
          return element('button', {'onClick': increment}, f'Count: {count}')

useEffect
---------

.. py:function:: useEffect(effect, dependencies=None)

   Performs side effects in function components.

   :param effect: Function to run (can return cleanup function)
   :type effect: callable
   :param dependencies: Array of values that trigger the effect
   :type dependencies: list, optional

   Example:

   .. code-block:: python

      from pyreact import element, useState, useEffect

      def DataFetcher(props):
          data, set_data = useState(None)
          loading, set_loading = useState(True)
          
          def fetch_data():
              # Fetch data
              set_data(fetch_from_api())
              set_loading(False)
          
          # Run once on mount
          useEffect(fetch_data, [])
          
          if loading:
              return element('div', {}, 'Loading...')
          
          return element('div', {}, f'Data: {data}')

   With cleanup:

   .. code-block:: python

      def Timer(props):
          seconds, set_seconds = useState(0)
          
          def setup_timer():
              timer_id = setInterval(lambda: set_seconds(s => s + 1), 1000)
              
              # Cleanup function
              return lambda: clearInterval(timer_id)
          
          useEffect(setup_timer, [])
          
          return element('div', {}, f'Seconds: {seconds}')

   With dependencies:

   .. code-block:: python

      def UserProfile(props):
          user_id = props['userId']
          user, set_user = useState(None)
          
          def fetch_user():
              set_user(fetch_user_by_id(user_id))
          
          # Re-run when userId changes
          useEffect(fetch_user, [user_id])
          
          return element('div', {}, f'User: {user}')

useContext
----------

.. py:function:: useContext(context)

   Accesses context value.

   :param context: Context object created by createContext
   :type context: Context
   :returns: Current context value
   :rtype: any

   Example:

   .. code-block:: python

      from pyreact import element, createContext, useContext

      ThemeContext = createContext('light')
      
      def ThemedButton(props):
          theme = useContext(ThemeContext)
          
          return element('button', {
              'style': {'backgroundColor': theme['primary']}
          }, 'Click me')

useRef
------

.. py:function:: useRef(initial_value=None)

   Creates a mutable reference that persists across renders.

   :param initial_value: Initial ref value
   :type initial_value: any, optional
   :returns: Ref object with current property
   :rtype: Ref

   Example:

   .. code-block:: python

      from pyreact import element, useRef

      def TextInput(props):
          input_ref = useRef()
          
          def focus():
              input_ref.current.focus()
          
          return element('div', {},
              element('input', {'ref': input_ref}),
              element('button', {'onClick': focus}, 'Focus')
          )

useMemo
-------

.. py:function:: useMemo(factory, dependencies)

   Memoizes expensive computations.

   :param factory: Function that computes the value
   :type factory: callable
   :param dependencies: Values that trigger recomputation
   :type dependencies: list
   :returns: Memoized value
   :rtype: any

   Example:

   .. code-block:: python

      from pyreact import element, useMemo

      def ExpensiveList(props):
          items = props['items']
          filter_text = props['filter']
          
          # Only recompute when items or filter changes
          filtered_items = useMemo(
              lambda: [i for i in items if filter_text in i['name']],
              [items, filter_text]
          )
          
          return element('ul', {},
              *[element('li', {'key': i['id']}, i['name']) 
                for i in filtered_items]
          )

useCallback
-----------

.. py:function:: useCallback(callback, dependencies)

   Returns a memoized callback.

   :param callback: Function to memoize
   :type callback: callable
   :param dependencies: Values that trigger recreation
   :type dependencies: list
   :returns: Memoized callback
   :rtype: callable

   Example:

   .. code-block:: python

      from pyreact import element, useCallback

      def Parent(props):
          def handle_click(item_id):
              print(f'Clicked: {item_id}')
          
          # Memoize callback
          memoized_click = useCallback(handle_click, [])
          
          return element('div', {},
              *[element(ChildButton, {
                  'key': item['id'],
                  'id': item['id'],
                  'onClick': memoized_click
              }) for item in props['items']]
          )

useReducer
----------

.. py:function:: useReducer(reducer, initial_state, init=None)

   Alternative to useState for complex state logic.

   :param reducer: Function (state, action) => new_state
   :type reducer: callable
   :param initial_state: Initial state value
   :type initial_state: any
   :param init: Lazy initialization function
   :type init: callable, optional
   :returns: Tuple of (state, dispatch)
   :rtype: tuple

   Example:

   .. code-block:: python

      from pyreact import element, useReducer

      def reducer(state, action):
          if action['type'] == 'increment':
              return {'count': state['count'] + 1}
          elif action['type'] == 'decrement':
              return {'count': state['count'] - 1}
          elif action['type'] == 'reset':
              return {'count': action['payload']}
          return state
      
      def Counter(props):
          state, dispatch = useReducer(reducer, {'count': 0})
          
          return element('div', {},
              element('p', {}, f'Count: {state["count"]}'),
              element('button', {
                  'onClick': lambda: dispatch({'type': 'increment'})
              }, '+'),
              element('button', {
                  'onClick': lambda: dispatch({'type': 'decrement'})
              }, '-'),
              element('button', {
                  'onClick': lambda: dispatch({'type': 'reset', 'payload': 0})
              }, 'Reset')
          )

Custom Hooks
------------

Create custom hooks:

.. code-block:: python

   from pyreact import useState, useEffect

   def useLocalStorage(key, initial_value):
       """Custom hook for localStorage"""
       stored = localStorage.getItem(key)
       value, set_value = useState(stored or initial_value)
       
       def save_to_storage():
           localStorage.setItem(key, value)
       
       useEffect(save_to_storage, [value])
       
       return value, set_value
   
   # Usage
   def App(props):
       name, set_name = useLocalStorage('name', 'Guest')
       
       return element('input', {
           'value': name,
           'onChange': lambda e: set_name(e.target.value)
       })

Best Practices
--------------

1. **Only call hooks at the top level** - Not inside loops or conditions
2. **Only call hooks from function components** - Not from regular functions
3. **Use the dependency array** - Specify all dependencies
4. **Name custom hooks with "use"** - Convention for custom hooks

Next Steps
----------

- :doc:`/api/component` - Component API reference
- :doc:`/concepts/state` - Learn about state
- :doc:`/advanced/testing` - Testing hooks
