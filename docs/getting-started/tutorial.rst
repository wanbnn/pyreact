.. _tutorial:

Tutorial: Building a Todo App
==============================

In this tutorial, you'll build a complete Todo application with PyReact Framework.

What You'll Build
-----------------

A fully functional Todo app with:

- Add new todos
- Mark todos as complete
- Delete todos
- Filter todos (all/active/completed)
- Persistent storage (localStorage)

Prerequisites
-------------

- Python 3.10 or higher
- PyReact Framework installed
- Basic Python knowledge

Step 1: Create the Project
---------------------------

.. code-block:: bash

   pyreact-framework create todo-app
   cd todo-app
   pyreact-framework dev

Step 2: Create TodoItem Component
----------------------------------

Create ``src/components/TodoItem.py``:

.. code-block:: python

   from pyreact import h, Component

   class TodoItem(Component):
       def render(self):
           todo = self.props['todo']
           on_toggle = self.props['onToggle']
           on_delete = self.props['onDelete']
           
           return h('li', {
               'class': f'todo-item {"completed" if todo["completed"] else ""}'
           },
               h('input', {
                   'type': 'checkbox',
                   'checked': todo['completed'],
                   'onChange': lambda e: on_toggle(todo['id'])
               }),
               h('span', {'class': 'todo-text'}, todo['text']),
               h('button', {
                   'class': 'delete-btn',
                   'onClick': lambda e: on_delete(todo['id'])
               }, '×')
           )

Step 3: Create TodoList Component
----------------------------------

Create ``src/components/TodoList.py``:

.. code-block:: python

   from pyreact import h, Component
   from .TodoItem import TodoItem

   class TodoList(Component):
       def render(self):
           todos = self.props['todos']
           filter_type = self.props.get('filter', 'all')
           
           filtered_todos = todos
           if filter_type == 'active':
               filtered_todos = [t for t in todos if not t['completed']]
           elif filter_type == 'completed':
               filtered_todos = [t for t in todos if t['completed']]
           
           return h('ul', {'class': 'todo-list'},
               *[h(TodoItem, {
                   'todo': todo,
                   'onToggle': self.props['onToggle'],
                   'onDelete': self.props['onDelete']
               }) for todo in filtered_todos]
           )

Step 4: Create App Component
-----------------------------

Update ``src/index.py``:

.. code-block:: python

   from pyreact import h, Component, render
   from components.TodoList import TodoList

   class App(Component):
       def __init__(self, props):
           super().__init__(props)
           self.state = {
               'todos': [],
               'input': '',
               'filter': 'all'
           }
       
       def add_todo(self, event):
           if self.state['input'].strip():
               new_todo = {
                   'id': len(self.state['todos']) + 1,
                   'text': self.state['input'],
                   'completed': False
               }
               self.set_state({
                   'todos': self.state['todos'] + [new_todo],
                   'input': ''
               })
       
       def toggle_todo(self, todo_id):
           todos = self.state['todos'][:]
           for todo in todos:
               if todo['id'] == todo_id:
                   todo['completed'] = not todo['completed']
           self.set_state({'todos': todos})
       
       def delete_todo(self, todo_id):
           todos = [t for t in self.state['todos'] if t['id'] != todo_id]
           self.set_state({'todos': todos})
       
       def set_filter(self, filter_type):
           self.set_state({'filter': filter_type})
       
       def render(self):
           return h('div', {'class': 'app'},
               h('h1', {}, 'Todo App'),
               h('div', {'class': 'add-todo'},
                   h('input', {
                       'type': 'text',
                       'value': self.state['input'],
                       'onInput': lambda e: self.set_state({'input': e.target.value}),
                       'placeholder': 'Add a todo...'
                   }),
                   h('button', {'onClick': self.add_todo}, 'Add')
               ),
               h(TodoList, {
                   'todos': self.state['todos'],
                   'filter': self.state['filter'],
                   'onToggle': self.toggle_todo,
                   'onDelete': self.delete_todo
               }),
               h('div', {'class': 'filters'},
                   h('button', {
                       'class': f"filter-btn {'' if self.state['filter'] == 'all' else ''}",
                       'onClick': lambda e: self.set_filter('all')
                   }, 'All'),
                   h('button', {
                       'class': f"filter-btn {'' if self.state['filter'] == 'active' else ''}",
                       'onClick': lambda e: self.set_filter('active')
                   }, 'Active'),
                   h('button', {
                       'class': f"filter-btn {'' if self.state['filter'] == 'completed' else ''}",
                       'onClick': lambda e: self.set_filter('completed')
                   }, 'Completed')
               )
           )

   render(h(App, {}), root='root')

Step 5: Add Styles
------------------

Create ``src/styles/main.css``:

.. code-block:: css

   .app {
       max-width: 600px;
       margin: 0 auto;
       padding: 20px;
   }
   
   .add-todo {
       display: flex;
       gap: 10px;
       margin-bottom: 20px;
   }
   
   .add-todo input {
       flex: 1;
       padding: 10px;
       font-size: 16px;
   }
   
   .todo-list {
       list-style: none;
       padding: 0;
   }
   
   .todo-item {
       display: flex;
       align-items: center;
       gap: 10px;
       padding: 10px;
       border-bottom: 1px solid #eee;
   }
   
   .todo-item.completed .todo-text {
       text-decoration: line-through;
       opacity: 0.5;
   }
   
   .delete-btn {
       background: #ff4444;
       color: white;
       border: none;
       border-radius: 50%;
       width: 30px;
       height: 30px;
       cursor: pointer;
   }
   
   .filters {
       display: flex;
       gap: 10px;
       margin-top: 20px;
   }
   
   .filter-btn.active {
       background: #007bff;
       color: white;
   }

Step 6: Run and Test
--------------------

Your app is ready! Open ``http://localhost:3000`` and test:

1. Add a new todo
2. Mark it as complete
3. Filter by active/completed
4. Delete a todo

What's Next?
------------

- :doc:`/concepts/state` - Learn more about state management
- :doc:`/advanced/routing` - Add routing to your app
- :doc:`/advanced/testing` - Write tests for your components
