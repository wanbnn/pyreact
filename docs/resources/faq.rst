.. _faq:

Frequently Asked Questions
===========================

General
-------

**What is PyReact Framework?**

PyReact Framework is a declarative web framework for Python, inspired by React. It allows you to build web applications using Python instead of JavaScript.

**Why use Python for frontend?**

- Python is easier to learn and read
- Large ecosystem of libraries
- Same language for frontend and backend
- Great for data science and ML integration

**Is PyReact production-ready?**

Yes! PyReact is stable and used in production applications. However, it's still evolving, so check the changelog for updates.

Getting Started
---------------

**How do I install PyReact?**

.. code-block:: bash

   pip install pyreact-framework

**What Python version do I need?**

Python 3.10 or higher is required.

**How do I create a new project?**

.. code-block:: bash

   pyreact-framework create my-app
   cd my-app
   pyreact-framework dev

Components
----------

**What's the difference between function and class components?**

Function components are simpler and recommended for most cases. Class components are useful when you need state or lifecycle methods.

**How do I pass data to components?**

Use props:

.. code-block:: python

   element(MyComponent, {'name': 'John', 'age': 30})

**How do I handle events?**

Pass event handlers as props:

.. code-block:: python

   element('button', {'onClick': lambda e: print('Clicked')}, 'Click me')

State Management
----------------

**How do I update state?**

Use ``setState()`` in class components:

.. code-block:: python

   self.setState({'count': self.state['count'] + 1})

Or ``useState`` hook in function components:

.. code-block:: python

   count, set_count = useState(0)
   set_count(count + 1)

**Why isn't my state updating?**

Make sure you're using ``setState()`` or the setter function, not modifying state directly:

.. code-block:: python
   :caption: ❌ Wrong

   self.state['count'] += 1  # Don't do this!

.. code-block:: python
   :caption: ✅ Correct

   self.setState({'count': self.state['count'] + 1})

**How do I share state between components?**

Lift state up to the common ancestor component and pass it down as props.

Styling
-------

**How do I add CSS?**

Import CSS files in your components:

.. code-block:: python

   from styles import main_css

Or use inline styles:

.. code-block:: python

   element('div', {'style': {'color': 'red'}})

**Does PyReact support CSS Modules?**

Yes! Enable in ``pyproject.toml``:

.. code-block:: toml

   [tool.pyreact]
   css_modules = true

Routing
-------

**How do I add routing?**

Use the built-in router:

.. code-block:: python

   from pyreact.router import Router, Route
   
   element(Router, {},
       element(Route, {'path': '/', 'component': Home}),
       element(Route, {'path': '/about', 'component': About})
   )

**How do I get route parameters?**

Use ``useParams``:

.. code-block:: python

   from pyreact.router import useParams
   
   params = useParams()
   user_id = params['id']

Testing
-------

**How do I test components?**

Use pytest with PyReact's testing utilities:

.. code-block:: python

   from pyreact.testing import render, fireEvent
   
   result = render(element(Button, {}))
   assert result.text == 'Click me'

**How do I test async code?**

Use ``asyncio`` and ``waitFor``:

.. code-block:: python

   from pyreact.testing import waitFor
   
   await waitFor(lambda: 'Loaded' in result.text)

Deployment
----------

**How do I build for production?**

.. code-block:: bash

   pyreact-framework build

**Where do I deploy PyReact apps?**

PyReact apps can be deployed to:

- Vercel
- Netlify
- AWS
- Google Cloud
- Any static hosting
- Python web servers (with SSR)

**How do I enable SSR?**

Enable in ``pyproject.toml``:

.. code-block:: toml

   [tool.pyreact]
   ssr = true

Troubleshooting
---------------

**My component isn't rendering**

Check:
1. Is the component exported correctly?
2. Are there any errors in the console?
3. Is the parent component rendering?

**Hot reload isn't working**

Make sure:
1. Development server is running
2. Files are being saved
3. No syntax errors exist

**Build is failing**

Check:
1. All imports are correct
2. No circular dependencies
3. All dependencies are installed

Getting Help
------------

- **Documentation**: https://pyreact-framework.readthedocs.io/
- **GitHub Issues**: https://github.com/wanbnn/pyreact/issues
- **Discussions**: https://github.com/wanbnn/pyreact/discussions

Next Steps
----------

- :doc:`/getting-started/tutorial` - Follow the tutorial
- :doc:`/api/hooks` - Explore hooks
- :doc:`/resources/changelog` - See what's new
