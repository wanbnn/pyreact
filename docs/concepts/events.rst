.. _events:

Events
======

PyReact uses synthetic events to handle user interactions. Events are similar to DOM events but work consistently across all browsers.

Event Handling
--------------

Handle events by passing functions to element props:

.. code-block:: python

   from pyreact import element, Component

   class Button(Component):
       def handle_click(self, event):
           print('Button clicked!')
       
       def render(self):
           return element('button', {
               'onClick': self.handle_click
           }, 'Click me')

Event Types
-----------

PyReact supports all standard DOM events:

Mouse Events
~~~~~~~~~~~~

.. code-block:: python

   element('div', {
       'onClick': lambda e: print('Clicked'),
       'onDoubleClick': lambda e: print('Double clicked'),
       'onMouseEnter': lambda e: print('Mouse entered'),
       'onMouseLeave': lambda e: print('Mouse left'),
       'onMouseMove': lambda e: print(f'Position: {e.clientX}, {e.clientY}')
   })

Keyboard Events
~~~~~~~~~~~~~~~

.. code-block:: python

   element('input', {
       'onKeyDown': lambda e: print(f'Key down: {e.key}'),
       'onKeyUp': lambda e: print(f'Key up: {e.key}'),
       'onKeyPress': lambda e: print(f'Key pressed: {e.key}')
   })

Form Events
~~~~~~~~~~~

.. code-block:: python

   element('form', {
       'onSubmit': lambda e: e.preventDefault()
   },
       element('input', {
           'onChange': lambda e: print(f'Value: {e.target.value}')
       }),
       element('button', {'type': 'submit'}, 'Submit')
   )

Focus Events
~~~~~~~~~~~~

.. code-block:: python

   element('input', {
       'onFocus': lambda e: print('Focused'),
       'onBlur': lambda e: print('Blurred')
   })

Event Object
------------

The event object contains useful properties:

.. code-block:: python

   def handle_click(self, event):
       # Prevent default behavior
       event.preventDefault()
       
       # Stop event propagation
       event.stopPropagation()
       
       # Access event properties
       print(f'Target: {event.target}')
       print(f'Current target: {event.currentTarget}')
       print(f'Type: {event.type}')
       print(f'TimeStamp: {event.timeStamp}')

Passing Arguments
-----------------

Pass arguments to event handlers:

.. code-block:: python

   class TodoList(Component):
       def delete_todo(self, todo_id, event):
           event.preventDefault()
           print(f'Deleting todo: {todo_id}')
       
       def render(self):
           todos = self.props['todos']
           return element('ul', {},
               *[element('li', {'key': todo['id']},
                   element('span', {}, todo['text']),
                   element('button', {
                       'onClick': lambda e, id=todo['id']: self.delete_todo(id, e)
                   }, 'Delete')
               ) for todo in todos]
           )

Conditional Event Handlers
--------------------------

Conditionally attach event handlers:

.. code-block:: python

   class Button(Component):
       def render(self):
           disabled = self.props.get('disabled', False)
           
           return element('button', {
               'disabled': disabled,
               'onClick': None if disabled else self.handle_click
           }, 'Click me')

Event Pooling
-------------

PyReact uses event pooling for performance. Access event properties asynchronously:

.. code-block:: python

   def handle_click(self, event):
       # Persist the event to use it asynchronously
       event.persist()
       
       # Now you can use it in async code
       import asyncio
       asyncio.create_task(self.async_operation(event))
   
   async def async_operation(self, event):
       await asyncio.sleep(1)
       print(f'Event type: {event.type}')

Best Practices
--------------

1. **Use descriptive names** - ``handle_submit`` instead of ``submit``
2. **Prevent default when needed** - Use ``event.preventDefault()`` for forms
3. **Clean up event listeners** - Remove listeners in ``component_will_unmount``
4. **Avoid inline functions** - Define methods instead of lambdas for complex logic

Next Steps
----------

- :doc:`/concepts/lifecycle` - Learn about lifecycle methods
- :doc:`/api/element` - Element API reference
- :doc:`/advanced/routing` - Add routing to your app
