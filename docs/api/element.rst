.. _element:

Element API
===========

The ``h()`` function is the core building block of PyReact. It creates virtual DOM elements.

Function Signature
------------------

.. py:function:: h(type, props=None, *children)

   Creates a virtual DOM node (``VNode``).

   :param type: The node type. It can be:
      - A string (HTML tag name like 'div', 'span', 'h1')
      - A component class or function
   :type type: str | Component | callable

   :param props: Properties/attributes for the node
   :type props: dict, optional

   :param children: Child elements
   :type children: VNode | str | int | float | list | tuple

   :returns: A virtual DOM node
   :rtype: VNode

Basic Usage
-----------

Create HTML elements:

.. code-block:: python

   from pyreact import h

   # Simple element
   h('div')
   
   # Element with props
   h('div', {'class': 'container', 'id': 'main'})
   
   # Element with children
   h('div', {},
       h('h1', {}, 'Title'),
       h('p', {}, 'Paragraph')
   )

HTML Elements
-------------

Create standard HTML elements:

.. code-block:: python

   # Text content
   h('h1', {}, 'Hello World')
   h('p', {}, 'This is a paragraph')
   
   # Attributes
   h('input', {'type': 'text', 'placeholder': 'Enter name'})
   h('a', {'href': 'https://example.com', 'target': '_blank'}, 'Link')
   
   # Styles
   h('div', {
       'style': {
           'backgroundColor': 'red',
           'padding': '10px'
       }
   })

Component Elements
------------------

Create component instances:

.. code-block:: python

   from pyreact import h
   from my_components import Button, Card

   # Function component
   h(Button, {'text': 'Click me', 'onClick': handle_click})
   
   # Class component
   h(Card, {'title': 'My Card'},
       h('p', {}, 'Card content')
   )

Children
--------

Pass children in different ways:

.. code-block:: python

   # As positional arguments
   h('div', {},
       h('p', {}, 'First'),
       h('p', {}, 'Second')
   )
   
   # As a list
   children = [
       h('p', {}, 'First'),
       h('p', {}, 'Second')
   ]
   h('div', {}, *children)
   
   # Mixed
   h('ul', {'class': 'list'},
       *[h('li', {}, f'Item {i}') for i in range(5)]
   )

Special Props
-------------

Key
~~~

Unique identifier for list items:

.. code-block:: python

   h('ul', {},
       *[h('li', {'key': item['id']}, item['text'])
         for item in items]
   )

Ref
~~~

Reference to a DOM element:

.. code-block:: python

   from pyreact import create_ref

   class MyComponent(Component):
       def __init__(self, props):
           super().__init__(props)
           self.input_ref = create_ref()
       
       def focus_input(self):
           self.input_ref.current.focus()
       
       def render(self):
           return h('input', {'ref': self.input_ref})

Style
~~~~~

Inline styles:

.. code-block:: python

   h('div', {
       'style': {
           'color': 'red',
           'fontSize': '16px',  # camelCase
           'marginTop': '10px'
       }
   })

className
~~~~~~~~~

CSS class names:

.. code-block:: python

   h('div', {'class': 'container active'})
   
   # Multiple classes
   h('div', {'class': 'btn btn-primary btn-large'})

dangerouslySetInnerHTML
~~~~~~~~~~~~~~~~~~~~~~~

Insert raw HTML (use with caution):

.. code-block:: python

   h('div', {
       'dangerouslySetInnerHTML': {'__html': '<strong>Bold</strong>'}
   })

Event Handlers
--------------

Attach event handlers:

.. code-block:: python

   h('button', {
       'onClick': lambda e: print('Clicked'),
       'onMouseEnter': lambda e: print('Mouse entered'),
       'onFocus': lambda e: print('Focused')
   })

Boolean Attributes
------------------

Boolean attributes:

.. code-block:: python

   h('input', {
       'type': 'checkbox',
       'checked': True,  # checked
       'disabled': False  # not disabled
   })

Data Attributes
---------------

Custom data attributes:

.. code-block:: python

   h('div', {
       'data-id': '123',
       'data-type': 'user',
       'data-active': 'true'
   })

Best Practices
--------------

1. **Always use keys for lists** - Helps PyReact identify which items changed
2. **Use fragments for grouped content** - Avoid unnecessary wrapper divs
3. **Extract repeated elements** - Create components for repeated patterns
4. **Keep props simple** - Don't pass complex logic in props

Next Steps
----------

- :doc:`/api/component` - Component API reference
- :doc:`/concepts/props` - Learn about props
- :doc:`/concepts/events` - Learn about events
