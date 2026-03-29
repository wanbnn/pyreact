.. _testing:

Testing
=======

PyReact provides utilities for testing your components.

Unit Testing
------------

Test components with pytest:

.. code-block:: python
   :caption: tests/test_button.py

   import pytest
   from pyreact import element
   from pyreact.testing import render, fireEvent
   from my_app.components import Button

   def test_button_renders():
       """Test that button renders with correct text"""
       result = render(element(Button, {'text': 'Click me'}))
       assert result.text == 'Click me'
   
   def test_button_click():
       """Test that button handles click events"""
       clicked = []
       
       def handle_click(event):
           clicked.append(True)
       
       result = render(element(Button, {
           'text': 'Click me',
           'onClick': handle_click
       }))
       
       fireEvent.click(result)
       assert len(clicked) == 1

Testing State
-------------

Test component state changes:

.. code-block:: python
   :caption: tests/test_counter.py

   from pyreact import element
   from pyreact.testing import render, fireEvent
   from my_app.components import Counter

   def test_counter_initial_state():
       """Test counter initial state"""
       result = render(element(Counter, {}))
       assert result.text == 'Count: 0'
   
   def test_counter_increment():
       """Test counter increment"""
       result = render(element(Counter, {}))
       
       # Click increment button
       increment_btn = result.find('button', text='+')
       fireEvent.click(increment_btn)
       
       assert result.text == 'Count: 1'
   
   def test_counter_decrement():
       """Test counter decrement"""
       result = render(element(Counter, {}))
       
       # Click decrement button
       decrement_btn = result.find('button', text='-')
       fireEvent.click(decrement_btn)
       
       assert result.text == 'Count: -1'

Testing Props
-------------

Test component props:

.. code-block:: python
   :caption: tests/test_greeting.py

   from pyreact import element
   from pyreact.testing import render
   from my_app.components import Greeting

   def test_greeting_with_name():
       """Test greeting with name prop"""
       result = render(element(Greeting, {'name': 'PyReact'}))
       assert 'PyReact' in result.text
   
   def test_greeting_default():
       """Test greeting with default prop"""
       result = render(element(Greeting, {}))
       assert 'World' in result.text

Testing Events
--------------

Test event handlers:

.. code-block:: python
   :caption: tests/test_form.py

   from pyreact import element
   from pyreact.testing import render, fireEvent
   from my_app.components import ContactForm

   def test_form_submission():
       """Test form submission"""
       submitted = []
       
       def handle_submit(event):
           event.preventDefault()
           submitted.append(event.data)
       
       result = render(element(ContactForm, {
           'onSubmit': handle_submit
       }))
       
       # Fill form
       name_input = result.find('input', {'name': 'name'})
       fireEvent.change(name_input, {'value': 'John Doe'})
       
       email_input = result.find('input', {'name': 'email'})
       fireEvent.change(email_input, {'value': 'john@example.com'})
       
       # Submit form
       form = result.find('form')
       fireEvent.submit(form)
       
       assert len(submitted) == 1
       assert submitted[0]['name'] == 'John Doe'
       assert submitted[0]['email'] == 'john@example.com'

Testing Async Components
------------------------

Test async operations:

.. code-block:: python
   :caption: tests/test_data_fetcher.py

   import pytest
   from pyreact import element
   from pyreact.testing import render, waitFor
   from my_app.components import DataFetcher

   @pytest.mark.asyncio
   async def test_data_fetcher():
       """Test async data fetching"""
       result = render(element(DataFetcher, {}))
       
       # Initially shows loading
       assert 'Loading' in result.text
       
       # Wait for data to load
       await waitFor(lambda: 'Data loaded' in result.text)
       
       # Check final state
       assert 'Data loaded' in result.text

Integration Testing
-------------------

Test component integration:

.. code-block:: python
   :caption: tests/test_app_integration.py

   from pyreact import element
   from pyreact.testing import render, fireEvent
   from my_app import App

   def test_app_integration():
       """Test full app integration"""
       result = render(element(App, {}))
       
       # Navigate to about page
       about_link = result.find('a', {'href': '/about'})
       fireEvent.click(about_link)
       
       # Check about page loaded
       assert 'About Us' in result.text
       
       # Navigate back home
       home_link = result.find('a', {'href': '/'})
       fireEvent.click(home_link)
       
       # Check home page loaded
       assert 'Welcome' in result.text

Test Configuration
------------------

Configure pytest for PyReact:

.. code-block:: python
   :caption: tests/conftest.py

   import pytest
   from pyreact.testing import TestRenderer

   @pytest.fixture
   def renderer():
       """Provide test renderer"""
       renderer = TestRenderer()
       yield renderer
       renderer.cleanup()

Best Practices
--------------

1. **Test behavior, not implementation** - Focus on what the component does
2. **Use descriptive test names** - ``test_button_displays_error_when_disabled``
3. **Test edge cases** - Empty states, errors, loading states
4. **Keep tests isolated** - Each test should be independent
5. **Use fixtures** - Reuse common test setup

Next Steps
----------

- :doc:`/api/component` - Component API reference
- :doc:`/advanced/ssr` - Server-side rendering
- :doc:`/resources/faq` - Frequently asked questions
