"""
PyReact Todo List Example
=========================

A todo list demonstrating:
- Complex state management
- Lists with keys
- Form handling
- Context API
"""

from pyreact import (
    h, render, use_state, use_reducer, use_effect,
    use_context, create_context, use_ref
)


# Context for theme
ThemeContext = create_context('light')


# Reducer for todo list
def todo_reducer(state, action):
    """Reducer for todo list state"""
    action_type = action.get('type')
    
    if action_type == 'ADD':
        new_todo = {
            'id': len(state['todos']) + 1,
            'text': action['text'],
            'completed': False
        }
        return {
            'todos': state['todos'] + [new_todo]
        }
    
    elif action_type == 'TOGGLE':
        todos = [
            {**todo, 'completed': not todo['completed']} if todo['id'] == action['id'] else todo
            for todo in state['todos']
        ]
        return {'todos': todos}
    
    elif action_type == 'REMOVE':
        todos = [todo for todo in state['todos'] if todo['id'] != action['id']]
        return {'todos': todos}
    
    elif action_type == 'CLEAR_COMPLETED':
        todos = [todo for todo in state['todos'] if not todo['completed']]
        return {'todos': todos}
    
    return state


# Components
def TodoItem(props):
    """Single todo item"""
    todo = props['todo']
    on_toggle = props['onToggle']
    on_remove = props['onRemove']
    
    return h('li', {
        'className': f"todo-item {'completed' if todo['completed'] else ''}",
        'key': todo['id']
    },
        h('input', {
            'type': 'checkbox',
            'checked': todo['completed'],
            'onChange': lambda e: on_toggle(todo['id'])
        }),
        h('span', {'className': 'todo-text'}, todo['text']),
        h('button', {
            'onClick': lambda e: on_remove(todo['id']),
            'className': 'btn-remove'
        }, '×')
    )


def TodoList(props):
    """List of todos"""
    todos = props['todos']
    dispatch = props['dispatch']
    
    def handle_toggle(todo_id):
        dispatch({'type': 'TOGGLE', 'id': todo_id})
    
    def handle_remove(todo_id):
        dispatch({'type': 'REMOVE', 'id': todo_id})
    
    if not todos:
        return h('p', {'className': 'empty-message'}, 'No todos yet!')
    
    return h('ul', {'className': 'todo-list'},
        *[h(TodoItem, {
            'key': todo['id'],
            'todo': todo,
            'onToggle': handle_toggle,
            'onRemove': handle_remove
        }) for todo in todos]
    )


def TodoInput(props):
    """Input for adding new todos"""
    dispatch = props['dispatch']
    text, set_text = use_state('')
    input_ref = use_ref(None)
    
    def handle_change(event):
        set_text(event.target.value)
    
    def handle_submit(event):
        event.prevent_default()
        if text.strip():
            dispatch({'type': 'ADD', 'text': text.strip()})
            set_text('')
    
    def handle_key_down(event):
        if event.key == 'Enter':
            handle_submit(event)
    
    return h('form', {'onSubmit': handle_submit, 'className': 'todo-form'},
        h('input', {
            'ref': input_ref,
            'type': 'text',
            'value': text,
            'onChange': handle_change,
            'onKeyDown': handle_key_down,
            'placeholder': 'What needs to be done?',
            'className': 'todo-input'
        }),
        h('button', {'type': 'submit', 'className': 'btn-add'}, 'Add')
    )


def TodoStats(props):
    """Todo statistics"""
    todos = props['todos']
    
    total = len(todos)
    completed = sum(1 for t in todos if t['completed'])
    remaining = total - completed
    
    return h('div', {'className': 'todo-stats'},
        h('span', None, f"{remaining} remaining"),
        h('span', None, f"{completed} completed"),
        h('span', None, f"{total} total")
    )


def TodoApp(props):
    """Main todo application"""
    state, dispatch = use_reducer(todo_reducer, {'todos': []})
    theme = use_context(ThemeContext)
    
    # Save to localStorage
    @use_effect([state])
    def save_todos():
        # In a real app, this would save to localStorage
        print(f"Saving {len(state['todos'])} todos")
        return lambda: None
    
    return h('div', {'className': f"todo-app theme-{theme}"},
        h('h1', None, 'Todo List'),
        h(TodoInput, {'dispatch': dispatch}),
        h(TodoList, {'todos': state['todos'], 'dispatch': dispatch}),
        h(TodoStats, {'todos': state['todos']}),
        state['todos'] and h('button', {
            'onClick': lambda e: dispatch({'type': 'CLEAR_COMPLETED'}),
            'className': 'btn-clear'
        }, 'Clear Completed')
    )


def App(props):
    """Root application"""
    return h(ThemeContext.Provider, {'value': 'light'},
        h(TodoApp, None)
    )


# Render
if __name__ == '__main__':
    from pyreact.dom.dom_operations import document
    
    root = document.create_element('div')
    root.attributes['id'] = 'root'
    document.body.append_child(root)
    
    render(h(App, None), root)
    
    print("Todo app rendered successfully!")
