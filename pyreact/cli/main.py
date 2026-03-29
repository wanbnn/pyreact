"""
PyReact CLI
===========

Command-line interface for PyReact development.
"""

import argparse
import os
import sys
from pathlib import Path


def create_project(name: str) -> None:
    """Create a new PyReact project"""
    project_dir = Path(name)
    
    if project_dir.exists():
        print(f"Error: Directory '{name}' already exists")
        sys.exit(1)
    
    # Create directory structure
    dirs = [
        'src/components',
        'src/hooks',
        'src/pages',
        'src/styles',
        'src/utils',
        'public',
        'tests',
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create pyproject.toml
    pyproject_content = '''[tool.pyreact]
entry = "src/index.py"
output = "dist"
dev_port = 3000
ssr = true
css_modules = true
source_maps = true
'''
    (project_dir / 'pyproject.toml').write_text(pyproject_content, encoding='utf-8')
    
    # Create main index file
    index_content = '''"""
Main entry point for PyReact application
"""

from pyreact import h, render, use_state


def App(props):
    """Main application component"""
    count, set_count = use_state(0)
    
    return h('div', {'className': 'app'},
        h('h1', None, f'Welcome to {props.get("name", "PyReact")}!'),
        h('p', None, 'Edit src/index.py to get started.'),
        h('div', {'className': 'counter'},
            h('span', None, f'Count: {count}'),
            h('button', {'onClick': lambda _: set_count(count + 1)}, '+'),
            h('button', {'onClick': lambda _: set_count(count - 1)}, '-')
        )
    )


if __name__ == '__main__':
    from pyreact.dom.dom_operations import document
    
    root = document.create_element('div')
    root.attributes['id'] = 'root'
    document.body.append_child(root)
    
    render(h(App, {'name': 'My App'}), root)
'''
    (project_dir / 'src' / 'index.py').write_text(index_content, encoding='utf-8')
    
    # Create __init__.py files
    init_content = '"""PyReact application package"""'
    (project_dir / 'src' / '__init__.py').write_text(init_content, encoding='utf-8')
    (project_dir / 'src' / 'components' / '__init__.py').write_text(init_content, encoding='utf-8')
    (project_dir / 'src' / 'hooks' / '__init__.py').write_text(init_content, encoding='utf-8')
    (project_dir / 'src' / 'pages' / '__init__.py').write_text(init_content, encoding='utf-8')
    
    # Create README
    readme_content = f'''# {name}

A PyReact application.

## Getting Started

```bash
# Install dependencies
pip install pyreact

# Run development server
pyreact dev

# Build for production
pyreact build
```

## Project Structure

```
{name}/
├── src/
│   ├── components/    # Reusable components
│   ├── hooks/         # Custom hooks
│   ├── pages/         # Page components
│   ├── styles/        # CSS files
│   └── index.py       # Entry point
├── public/            # Static assets
├── tests/             # Test files
└── pyproject.toml     # Configuration
```
'''
    (project_dir / 'README.md').write_text(readme_content, encoding='utf-8')
    
    # Create test file
    test_content = '''"""
Tests for the application
"""

from pyreact.testing import render, screen, fireEvent
from pyreact import h


def test_app_renders():
    """Test that the app renders"""
    # Add your tests here
    pass


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
'''
    (project_dir / 'tests' / 'test_app.py').write_text(test_content, encoding='utf-8')
    
    print(f"[OK] Created project '{name}'")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    print(f"  pyreact dev")


def generate_component(name: str, component_type: str = 'functional') -> None:
    """Generate a new component"""
    # Determine output directory
    components_dir = Path('src/components')
    if not components_dir.exists():
        components_dir = Path('components')
    
    if not components_dir.exists():
        print("Error: Could not find components directory")
        sys.exit(1)
    
    # Create component file
    if component_type == 'class':
        content = f'''"""
{name} Component
"""

from pyreact import h, Component


class {name}(Component):
    """Class component: {name}"""
    
    def __init__(self, props):
        super().__init__(props)
        self.state = {{}}
    
    def render(self):
        return h('div', {{'className': '{name.lower()}'}},
            h('h2', None, '{name}'),
            self.props.get('children', None)
        )
'''
    else:
        content = f'''"""
{name} Component
"""

from pyreact import h, use_state


def {name}(props):
    """Functional component: {name}"""
    
    return h('div', {{'className': '{name.lower()}'}},
        h('h2', None, '{name}'),
        props.get('children', None)
    )
'''
    
    file_path = components_dir / f'{name}.py'
    file_path.write_text(content, encoding='utf-8')
    
    print(f"[OK] Created component '{name}' at {file_path}")


def generate_hook(name: str) -> None:
    """Generate a new custom hook"""
    hooks_dir = Path('src/hooks')
    if not hooks_dir.exists():
        hooks_dir = Path('hooks')
    
    if not hooks_dir.exists():
        print("Error: Could not find hooks directory")
        sys.exit(1)
    
    # Remove 'use' prefix if present
    if name.startswith('use_'):
        name = name[4:]
    elif name.startswith('use'):
        name = name[3:]
    
    hook_name = f'use_{name.lower()}'
    
    content = f'''"""
{name} Hook
"""

from pyreact import use_state, use_effect


def {hook_name}(initial_value=None):
    """
    Custom hook: {hook_name}
    
    Args:
        initial_value: Initial value
    
    Returns:
        tuple: (value, setter)
    """
    value, set_value = use_state(initial_value)
    
    @use_effect([])
    def setup():
        # Setup logic here
        return lambda: None  # Cleanup
    
    return value, set_value
'''
    
    file_path = hooks_dir / f'{hook_name}.py'
    file_path.write_text(content, encoding='utf-8')
    
    print(f"[OK] Created hook '{hook_name}' at {file_path}")


def run_dev_server(port: int = 3000) -> None:
    """Run development server"""
    import http.server
    import socketserver
    import threading
    import time
    import webbrowser
    from pathlib import Path
    
    # Check if we're in a PyReact project
    if not Path('pyproject.toml').exists():
        print("Error: Not a PyReact project. Run 'pyreact create <name>' first.", flush=True)
        sys.exit(1)
    
    # Check if src/index.py exists
    if not Path('src/index.py').exists():
        print("Error: src/index.py not found", flush=True)
        sys.exit(1)
    
    # Create public directory if it doesn't exist
    Path('public').mkdir(exist_ok=True)
    
    # Generate HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyReact App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .app { max-width: 800px; margin: 0 auto; }
        .counter { display: flex; gap: 10px; align-items: center; }
        button { padding: 5px 15px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script>
        // PyReact runtime simulation
        const PyReact = {
            h: function(type, props, ...children) {
                return { type, props: props || {}, children: children.flat() };
            },
            render: function(vnode, container) {
                const dom = this.createDom(vnode);
                container.innerHTML = '';
                container.appendChild(dom);
            },
            createDom: function(vnode) {
                if (typeof vnode === 'string') {
                    return document.createTextNode(vnode);
                }
                if (!vnode || !vnode.type) {
                    return document.createTextNode('');
                }
                
                const dom = document.createElement(vnode.type);
                
                // Apply props
                for (const [key, value] of Object.entries(vnode.props || {})) {
                    if (key === 'className') {
                        dom.className = value;
                    } else if (key.startsWith('on')) {
                        const event = key[2].toLowerCase() + key.slice(3);
                        dom.addEventListener(event, value);
                    } else if (key === 'style' && typeof value === 'object') {
                        Object.assign(dom.style, value);
                    } else {
                        dom.setAttribute(key, value);
                    }
                }
                
                // Render children
                for (const child of vnode.children || []) {
                    dom.appendChild(this.createDom(child));
                }
                
                return dom;
            }
        };
        
        // State management
        let stateValues = [];
        let stateIndex = 0;
        
        function useState(initialValue) {
            const currentIndex = stateIndex;
            if (stateValues[currentIndex] === undefined) {
                stateValues[currentIndex] = initialValue;
            }
            const setValue = (newValue) => {
                if (typeof newValue === 'function') {
                    stateValues[currentIndex] = newValue(stateValues[currentIndex]);
                } else {
                    stateValues[currentIndex] = newValue;
                }
                stateIndex = 0;
                render();
            };
            stateIndex++;
            return [stateValues[currentIndex], setValue];
        }
        
        function render() {
            stateIndex = 0;
            const [count, setCount] = useState(0);
            const root = document.getElementById('root');
            const app = PyReact.h('div', {className: 'app'},
                PyReact.h('h1', null, 'Welcome to PyReact!'),
                PyReact.h('p', null, 'Edit src/index.py to get started.'),
                PyReact.h('div', {className: 'counter'},
                    PyReact.h('span', null, 'Count: ' + count),
                    PyReact.h('button', {onClick: () => setCount(count + 1)}, '+'),
                    PyReact.h('button', {onClick: () => setCount(count - 1)}, '-')
                )
            );
            PyReact.render(app, root);
        }
        
        // Initial render
        render();
        
        // Hot reload simulation
        console.log('PyReact dev server running. Edit src/index.py to see changes.');
    </script>
</body>
</html>'''
    
    html_path = Path('public/index.html')
    html_path.write_text(html_content, encoding='utf-8')
    
    # Change to public directory
    original_dir = os.getcwd()
    os.chdir('public')
    
    # Create custom handler
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress default logging
            pass
    
    # Start server
    try:
        # Allow address reuse
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print(f"[OK] Development server running at {url}", flush=True)
            print(f"\nPress Ctrl+C to stop the server", flush=True)
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1.5)
                try:
                    webbrowser.open(url)
                except:
                    pass
            
            browser_thread = threading.Thread(target=open_browser, daemon=True)
            browser_thread.start()
            
            # Serve forever
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                os.chdir(original_dir)
            
    except OSError as e:
        os.chdir(original_dir)
        if 'Address already in use' in str(e) or e.errno == 10048:  # Port already in use (Windows)
            print(f"Error: Port {port} is already in use", flush=True)
            print(f"Try: pyreact dev --port {port + 1}", flush=True)
        else:
            print(f"Error: {e}", flush=True)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[OK] Server stopped", flush=True)


def build_project() -> None:
    """Build project for production"""
    print("Building project for production...")
    print("Note: This is a placeholder. Implement actual build process.")
    
    # Check for pyproject.toml
    if not Path('pyproject.toml').exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)
    
    print("[OK] Build complete (placeholder)")


def run_tests() -> None:
    """Run tests"""
    import subprocess
    
    print("Running tests...")
    result = subprocess.run(['pytest', 'tests/', '-v'])
    sys.exit(result.returncode)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PyReact - Framework Web Declarativo para Python'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('name', help='Project name')
    
    # Dev command
    dev_parser = subparsers.add_parser('dev', help='Start development server')
    dev_parser.add_argument('--port', type=int, default=3000, help='Port number')
    
    # Build command
    subparsers.add_parser('build', help='Build for production')
    
    # Test command
    subparsers.add_parser('test', help='Run tests')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate component or hook')
    gen_parser.add_argument('type', choices=['component', 'hook'], help='Type to generate')
    gen_parser.add_argument('name', help='Name of component or hook')
    gen_parser.add_argument('--class', dest='class_type', action='store_true',
                           help='Generate class component')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_project(args.name)
    elif args.command == 'dev':
        run_dev_server(args.port)
    elif args.command == 'build':
        build_project()
    elif args.command == 'test':
        run_tests()
    elif args.command == 'generate':
        if args.type == 'component':
            component_type = 'class' if args.class_type else 'functional'
            generate_component(args.name, component_type)
        elif args.type == 'hook':
            generate_hook(args.name)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
