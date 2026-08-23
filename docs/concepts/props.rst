.. _props:

Props
=====

Props (short for "properties") are how data flows from parent to child components. They are read-only and help make components reusable.

Basic Usage
-----------

Pass props to a component:

.. code-block:: python

   from pyreact import h

   def Greeting(props):
       name = props.get('name', 'World')
       return h('h1', {}, f'Hello, {name}!')

   # Pass props
   h(Greeting, {'name': 'PyReact'})

Props are Read-Only
-------------------

Components must never modify their own props:

.. code-block:: python
   :caption: ❌ Wrong

   def Greeting(props):
       props['name'] = 'Modified'  # Never do this!
       return h('h1', {}, f'Hello, {props["name"]}')

.. code-block:: python
   :caption: ✅ Correct

   def Greeting(props):
       name = props.get('name', 'World')
       return h('h1', {}, f'Hello, {name}')

Default Props
-------------

Provide default values for props:

.. code-block:: python

   def Button(props):
       text = props.get('text', 'Click me')
       variant = props.get('variant', 'primary')
       disabled = props.get('disabled', False)
       
       return h('button', {
           'class': f'btn btn-{variant}',
           'disabled': disabled
       }, text)

   # Usage
   h(Button, {})  # Uses defaults
   h(Button, {'text': 'Submit', 'variant': 'success'})

Children Prop
-------------

Pass children to components:

.. code-block:: python

   def Card(props):
       title = props.get('title', '')
       children = props.get('children', [])
       
       return h('div', {'class': 'card'},
           h('h2', {'class': 'card-title'}, title),
           h('div', {'class': 'card-body'}, *children)
       )

   # Usage
   h(Card, {'title': 'Welcome'},
       h('p', {}, 'This is the card content'),
       h('button', {}, 'Click me')
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
       
       return h('div', {'class': 'user-card'},
           h('h3', {}, user['name']),
           h('p', {}, f"Active: {is_active}"),
           h('div', {},
               *[h('span', {'class': 'tag'}, tag) for tag in tags]
           ),
           h('button', {'onClick': on_click}, 'View Profile')
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
           self.set_state({'count': self.state['count'] + amount})
       
       def render(self):
           return h('div', {},
               h('p', {}, f'Count: {self.state["count"]}'),
               h(ChildButton, {
                   'onClick': lambda e: self.handle_increment(1),
                   'label': 'Add 1'
               }),
               h(ChildButton, {
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
