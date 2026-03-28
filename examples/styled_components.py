"""
PyReact Styled Components Example
=================================

Demonstrates:
- CSS-in-Python styling
- Styled components
- Global styles
- Keyframe animations
"""

from pyreact import h, render, use_state, styled, css_module, keyframes, create_global_style


# Global Styles
GlobalStyle = create_global_style('''
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background-color: #f5f5f5;
        color: #333;
        line-height: 1.6;
    }
    
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
''')


# Keyframe Animation
fadeIn = keyframes('''
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
''')

pulse = keyframes('''
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
''')


# Styled Components
Button = styled('button', '''
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
    }
    
    &:active {
        transform: translateY(0);
    }
    
    &:disabled {
        background-color: #ccc;
        cursor: not-allowed;
        transform: none;
    }
''')

PrimaryButton = styled('button', '''
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 12px 30px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
    
    &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
''')

Card = styled('div', '''
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease;
    
    &:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
''')

Input = styled('input', '''
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.2s ease;
    
    &:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
    }
    
    &::placeholder {
        color: #999;
    }
''')

Alert = styled('div', '''
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
    animation: fadeIn 0.3s ease;
    
    &.success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    &.error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    &.warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
''')


# Components using styled components
def StyledButton(props):
    """Button with loading state"""
    loading, set_loading = use_state(False)
    
    def handle_click(event):
        if not loading:
            set_loading(True)
            # Simulate async operation
            import time
            time.sleep(1)
            set_loading(False)
    
    return h(Button, {
        'onClick': handle_click,
        'disabled': loading
    }, 'Loading...' if loading else props.get('children', 'Click Me'))


def StyledCard(props):
    """Card with title and content"""
    return h(Card, None,
        h('h3', {'style': {'marginBottom': '12px'}}, props.get('title', 'Card Title')),
        props.get('children', h('p', None, 'Card content goes here'))
    )


def StyledForm(props):
    """Styled form example"""
    name, set_name = use_state('')
    email, set_email = use_state('')
    submitted, set_submitted = use_state(False)
    
    def handle_submit(event):
        event.prevent_default()
        if name and email:
            set_submitted(True)
    
    if submitted:
        return h(Alert, {'className': 'success'},
            h('strong', None, 'Success!'),
            h('p', None, f"Thank you, {name}! We'll contact you at {email}.")
        )
    
    return h('form', {'onSubmit': handle_submit},
        h(StyledCard, {'title': 'Contact Form'},
            h('div', {'style': {'marginBottom': '16px'}},
                h('label', {'style': {'display': 'block', 'marginBottom': '8px'}}, 'Name'),
                h(Input, {
                    'type': 'text',
                    'value': name,
                    'onChange': lambda e: set_name(e.target.value),
                    'placeholder': 'Enter your name'
                })
            ),
            h('div', {'style': {'marginBottom': '16px'}},
                h('label', {'style': {'display': 'block', 'marginBottom': '8px'}}, 'Email'),
                h(Input, {
                    'type': 'email',
                    'value': email,
                    'onChange': lambda e: set_email(e.target.value),
                    'placeholder': 'Enter your email'
                })
            ),
            h(PrimaryButton, {'type': 'submit'}, 'Submit')
        )
    )


def App(props):
    """Main application"""
    return h('div', {'className': 'container'},
        h(GlobalStyle, None),
        h('h1', {'style': {'textAlign': 'center', 'marginBottom': '32px'}},
            'Styled Components Demo'
        ),
        h(StyledCard, {'title': 'Buttons'},
            h('div', {'style': {'display': 'flex', 'gap': '12px'}},
                h(Button, None, 'Default Button'),
                h(PrimaryButton, None, 'Primary Button'),
                h(StyledButton, None, 'Loading Button')
            )
        ),
        h(StyledCard, {'title': 'Alerts'},
            h(Alert, {'className': 'success'}, 'Success message!'),
            h(Alert, {'className': 'warning'}, 'Warning message!'),
            h(Alert, {'className': 'error'}, 'Error message!')
        ),
        h(StyledForm, None)
    )


# Render
if __name__ == '__main__':
    from pyreact.dom.dom_operations import document
    
    root = document.create_element('div')
    root.attributes['id'] = 'root'
    document.body.append_child(root)
    
    render(h(App, None), root)
    
    print("Styled components demo rendered!")
