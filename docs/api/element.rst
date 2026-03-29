.. _element:

Element API
===========

The ``element()`` function is the core building block of PyReact. It creates virtual DOM elements.

Function Signature
------------------

.. py:function:: element(type, props={}, *children)

   Creates a virtual DOM element.

   :param type: The type of element. Can be:
      - A string (HTML tag name like 'div', 'span', 'h1')
      - A component class or function
      - A fragment (``Fragment``)
   :type type: str | Component | Fragment

   :param props: Properties/attributes for the element
   :type props: dict, optional

   :param children: Child elements
   :type children: element | str | list

   :returns: A virtual DOM element
   :rtype: Element

Basic Usage
-----------

Create HTML elements:

.. code-block:: python

   from pyreact import element

   # Simple element
   element('div')
   
   # Element with props
   element('div', {'class': 'container', 'id': 'main'})
   
   # Element with children
   element('div', {},
       element('h1', {}, 'Title'),
       element('p', {}, 'Paragraph')
   )

HTML Elements
-------------

Create standard HTML elements:

.. code-block:: python

   # Text content
   element('h1', {}, 'Hello World')
   element('p', {}, 'This is a paragraph')
   
   # Attributes
   element('input', {'type': 'text', 'placeholder': 'Enter name'})
   element('a', {'href': 'https://example.com', 'target': '_blank'}, 'Link')
   
   # Styles
   element('div', {
       'style': {
           'backgroundColor': 'red',
           'padding': '10px'
       }
   })

Component Elements
------------------

Create component instances:

.. code-block:: python

   from pyreact import element
   from my_components import Button, Card

   # Function component
   element(Button, {'text': 'Click me', 'onClick': handle_click})
   
   # Class component
   element(Card, {'title': 'My Card'},
       element('p', {}, 'Card content')
   )

Fragments
---------

Group elements without adding extra DOM nodes:

.. code-block:: python

   from pyreact import element, Fragment

   def ListItem(props):
       return element(Fragment, {},
           element('dt', {}, props['term']),
           element('dd', {}, props['definition'])
       )

Children
--------

Pass children in different ways:

.. code-block:: python

   # As positional arguments
   element('div', {},
       element('p', {}, 'First'),
       element('p', {}, 'Second')
   )
   
   # As a list
   children = [
       element('p', {}, 'First'),
       element('p', {}, 'Second')
   ]
   element('div', {}, *children)
   
   # Mixed
   element('ul', {'class': 'list'},
       *[element('li', {}, f'Item {i}') for i in range(5)]
   )

Special Props
-------------

Key
~~~

Unique identifier for list items:

.. code-block:: python

   element('ul', {},
       *[element('li', {'key': item['id']}, item['text']) 
         for item in items]
   )

Ref
~~~

Reference to DOM element:

.. code-block:: python

   from pyreact import create_ref

   class MyComponent(Component):
       def __init__(self, props):
           super().__init__(props)
           self.input_ref = create_ref()
       
       def focus_input(self):
           self.input_ref.current.focus()
       
       def render(self):
           return element('input', {'ref': self.input_ref})

Style
~~~~

Inline styles:

.. code-block:: python

   element('div', {
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

   element('div', {'class': 'container active'})
   
   # Multiple classes
   element('div', {'class': 'btn btn-primary btn-large'})

dangerouslySetInnerHTML
~~~~~~~~~~~~~~~~~~~~~~~

Insert raw HTML (use with caution):

.. code-block:: python

   element('div', {
       'dangerouslySetInnerHTML': {'__html': '<strong>Bold</strong>'}
   })

Event Handlers
--------------

Attach event handlers:

.. code-block:: python

   element('button', {
       'onClick': lambda e: print('Clicked'),
       'onMouseEnter': lambda e: print('Mouse entered'),
       'onFocus': lambda e: print('Focused')
   })

Boolean Attributes
------------------

Boolean attributes:

.. code-block:: python

   element('input', {
       'type': 'checkbox',
       'checked': True,  # checked
       'disabled': False  # not disabled
   })

Data Attributes
---------------

Custom data attributes:

.. code-block:: python

   element('div', {
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
