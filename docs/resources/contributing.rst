.. _contributing:

Contributing Guide
==================

Thank you for your interest in contributing to PyReact Framework!

Table of Contents
-----------------

.. contents::
   :local:
   :depth: 2

Code of Conduct
---------------

Please read and follow our `Code of Conduct <https://github.com/wanbnn/pyreact/blob/main/CODE_OF_CONDUCT.md>`_.

How to Contribute
-----------------

Reporting Bugs
~~~~~~~~~~~~~~

1. Check if the bug has already been reported in `Issues <https://github.com/wanbnn/pyreact/issues>`_
2. If not, create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

Suggesting Features
~~~~~~~~~~~~~~~~~~~

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear title
   - Use case description
   - Proposed solution (optional)

Pull Requests
-------------

Development Setup
~~~~~~~~~~~~~~~~~

1. Fork the repository
2. Clone your fork:

   .. code-block:: bash

      git clone https://github.com/wanbnn/pyreact.git
      cd pyreact

3. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # Linux/Mac
      venv\Scripts\activate     # Windows

4. Install dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

5. Create a branch:

   .. code-block:: bash

      git checkout -b feature/my-feature

Coding Standards
~~~~~~~~~~~~~~~~

Follow these guidelines:

**Python Style**

- Follow `PEP 8 <https://pep8.org/>`_
- Use type hints
- Write docstrings

**Code Example:**

.. code-block:: python

   def calculate_total(items: list[dict]) -> float:
       """
       Calculate the total price of items.
       
       Args:
           items: List of item dictionaries with 'price' key
       
       Returns:
           Total price as float
       
       Raises:
           ValueError: If items list is empty
       """
       if not items:
           raise ValueError("Items list cannot be empty")
       
       return sum(item['price'] for item in items)

Testing
~~~~~~~

Write tests for your code:

.. code-block:: python
   :caption: tests/test_utils.py

   import pytest
   from pyreact.utils import calculate_total

   def test_calculate_total():
       items = [{'price': 10}, {'price': 20}]
       assert calculate_total(items) == 30
   
   def test_calculate_total_empty():
       with pytest.raises(ValueError):
           calculate_total([])

Run tests:

.. code-block:: bash

   pytest tests/

Documentation
~~~~~~~~~~~~~

Update documentation:

1. Update docstrings
2. Update API reference if needed
3. Add examples
4. Update changelog

Commit Messages
~~~~~~~~~~~~~~~

Follow conventional commits:

.. code-block:: text

   type(scope): subject

   body (optional)

   footer (optional)

**Types:**

- ``feat`` - New feature
- ``fix`` - Bug fix
- ``docs`` - Documentation
- ``style`` - Formatting
- ``refactor`` - Code refactoring
- ``test`` - Adding tests
- ``chore`` - Maintenance

**Examples:**

.. code-block:: text

   feat(hooks): add useTransition hook
   
   Implement useTransition hook for managing transition state.
   
   Closes #123

.. code-block:: text

   fix(router): handle nested routes correctly
   
   Fix issue where nested routes were not rendering properly.

Submitting PRs
~~~~~~~~~~~~~~

1. Push your branch:

   .. code-block:: bash

      git push origin feature/my-feature

2. Create a Pull Request on GitHub
3. Fill in the PR template
4. Wait for review

Review Process
--------------

All PRs require:

1. At least one approval
2. All tests passing
3. No merge conflicts
4. Documentation updated

Reviewers will check:

- Code quality
- Test coverage
- Documentation
- Performance impact
- Breaking changes

Release Process
---------------

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md``
3. Create a release PR
4. Merge to main
5. Tag the release:

   .. code-block:: bash

      git tag v1.0.0
      git push origin v1.0.0

6. GitHub Actions will publish to PyPI

Getting Help
------------

- **GitHub Discussions**: https://github.com/wanbnn/pyreact/discussions
- **Discord**: https://discord.gg/pyreact
- **Email**: wanbnn@users.noreply.github.com

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank You!
----------

Your contributions make PyReact better for everyone. Thank you for your time and effort!

Next Steps
----------

- :doc:`/getting-started/installation` - Install PyReact
- :doc:`/getting-started/tutorial` - Build a Todo app
- :doc:`/api/hooks` - Explore hooks
