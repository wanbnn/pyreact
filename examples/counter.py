"""
PyReact Counter Example
=======================

A simple counter component demonstrating:
- useState hook
- Event handling
- Component composition
"""

from pyreact import h, render, use_state, Component


# Functional Component with Hooks
def Counter(props):
    """
    Counter component using hooks
    
    Demonstrates:
    - use_state for state management
    - Event handlers
    - Conditional rendering
    """
    count, set_count = use_state(0)
    
    def increment(event):
        set_count(lambda c: c + 1)
    
    def decrement(event):
        set_count(lambda c: c - 1)
    
    def reset(event):
        set_count(0)
    
    return h('div', {'className': 'counter'},
        h('h2', None, 'Counter Example'),
        h('div', {'className': 'count-display'},
            h('span', {'className': 'count'}, str(count))
        ),
        h('div', {'className': 'buttons'},
            h('button', {'onClick': decrement, 'className': 'btn-dec'}, '-'),
            h('button', {'onClick': reset, 'className': 'btn-reset'}, 'Reset'),
            h('button', {'onClick': increment, 'className': 'btn-inc'}, '+')
        ),
        count > 0 and h('p', {'className': 'positive'}, 'Positive!'),
        count < 0 and h('p', {'className': 'negative'}, 'Negative!')
    )


# Class Component Alternative
class CounterClass(Component):
    """
    Counter component using class
    
    Demonstrates:
    - Component state
    - set_state method
    - Lifecycle methods
    """
    
    def __init__(self, props):
        super().__init__(props)
        self.state = {'count': 0}
    
    def increment(self, event):
        self.set_state({'count': self.state['count'] + 1})
    
    def decrement(self, event):
        self.set_state({'count': self.state['count'] - 1})
    
    def reset(self, event):
        self.set_state({'count': 0})
    
    def render(self):
        count = self.state['count']
        
        return h('div', {'className': 'counter'},
            h('h2', None, 'Counter (Class)'),
            h('div', {'className': 'count-display'},
                h('span', {'className': 'count'}, str(count))
            ),
            h('div', {'className': 'buttons'},
                h('button', {'onClick': self.decrement}, '-'),
                h('button', {'onClick': self.reset}, 'Reset'),
                h('button', {'onClick': self.increment}, '+')
            )
        )


# App Component
def App(props):
    """Main application component"""
    return h('div', {'className': 'app'},
        h('h1', None, 'PyReact Counter Examples'),
        h('hr', None),
        h(Counter, None),
        h('hr', None),
        h(CounterClass, None)
    )


# Render
if __name__ == '__main__':
    from pyreact.dom.dom_operations import document
    
    # Create root element
    root = document.create_element('div')
    root.attributes['id'] = 'root'
    document.body.append_child(root)
    
    # Render app
    render(h(App, None), root)
    
    print("Counter app rendered successfully!")
    print("Use the buttons to increment/decrement the counter.")
