.. _props:

Props
=====

Props (short for "properties") are how data flows from parent to child components. They are read-only and help make components reusable.

Basic Usage
-----------

Pass props to a component:

.. code-block:: python

   from pyreact import element

   def Greeting(props):
       name = props.get('name', 'World')
       return element('h1', {}, f'Hello, {name}!')

   # Pass props
   element(Greeting, {'name': 'PyReact'})

Props are Read-Only
-------------------

Components must never modify their own props:

.. code-block:: python
   :caption: ❌ Wrong

   def Greeting(props):
       props['name'] = 'Modified'  # Never do this!
       return element('h1', {}, f'Hello, {props["name"]}')

.. code-block:: python
   :caption: ✅ Correct

   def Greeting(props):
       name = props.get('name', 'World')
       return element('h1', {}, f'Hello, {name}')

Default Props
-------------

Provide default values for props:

.. code-block:: python

   def Button(props):
       text = props.get('text', 'Click me')
       variant = props.get('variant', 'primary')
       disabled = props.get('disabled', False)
       
       return element('button', {
           'class': f'btn btn-{variant}',
           'disabled': disabled
       }, text)

   # Usage
   element(Button, {})  # Uses defaults
   element(Button, {'text': 'Submit', 'variant': 'success'})

Children Prop
-------------

Pass children to components:

.. code-block:: python

   def Card(props):
       title = props.get('title', '')
       children = props.get('children', [])
       
       return element('div', {'class': 'card'},
           element('h2', {'class': 'card-title'}, title),
           element('div', {'class': 'card-body'}, *children)
       )

   # Usage
   element(Card, {'title': 'Welcome'},
       element('p', {}, 'This is the card content'),
       element('button', {}, 'Click me')
   )

Prop Types
----------

Props can be any Python type:

.. code-block:: python

   def UserCard(props):
       user = props['user']  # dict
       on_click = props['onClick']  # function
       is_active = props.get('active', False)  # bool
       tags = props.get('tags', [])  # list
       
       return element('div', {'class': 'user-card'},
           element('h3', {}, user['name']),
           element('p', {}, f"Active: {is_active}"),
           element('div', {},
               *[element('span', {'class': 'tag'}, tag) for tag in tags]
           ),
           element('button', {'onClick': on_click}, 'View Profile')
       )

Passing Functions as Props
--------------------------

Pass callback functions to child components:

.. code-block:: python

   class Parent(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {'count': 0}
       
       def handle_increment(self, amount):
           self.setState({'count': self.state['count'] + amount})
       
       def render(self):
           return element('div', {},
               element('p', {}, f'Count: {self.state["count"]}'),
               element(ChildButton, {
                   'onClick': lambda e: self.handle_increment(1),
                   'label': 'Add 1'
               }),
               element(ChildButton, {
                   'onClick': lambda e: self.handle_increment(10),
                   'label': 'Add 10'
               })
           )

Best Practices
--------------

1. **Use descriptive prop names** - ``is_active`` instead of ``active``
2. **Provide defaults** - Use ``props.get()`` with default values
3. **Document props** - Add docstrings explaining expected props
4. **Validate props** - Check required props exist

Next Steps
----------

- :doc:`/concepts/state` - Learn about state
- :doc:`/concepts/events` - Learn about event handling
- :doc:`/api/component` - Component API reference
