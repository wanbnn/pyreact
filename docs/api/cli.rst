.. _cli:

CLI API
=======

PyReact provides a command-line interface for creating and managing projects.

Installation
------------

The CLI is installed with PyReact:

.. code-block:: bash

   pip install pyreact-framework

Commands
--------

pyreact-framework create
~~~~~~~~~~~~~~~~~~~~~~~~

Create a new PyReact project.

.. code-block:: bash

   pyreact-framework create <project-name> [options]

**Arguments:**

- ``project-name`` - Name of the project (required)

**Options:**

- ``--template`` - Template to use (default: 'default')
- ``--no-git`` - Skip git initialization

**Examples:**

.. code-block:: bash

   # Create basic project
   pyreact-framework create my-app
   
   # Create from template
   pyreact-framework create my-app --template dashboard
   
   # Create without git
   pyreact-framework create my-app --no-git

pyreact-framework dev
~~~~~~~~~~~~~~~~~~~~~

Start the development server.

.. code-block:: bash

   pyreact-framework dev [options]

**Options:**

- ``--port`` - Port number (default: 3000)
- ``--host`` - Host address (default: 'localhost')
- ``--open`` - Open browser automatically

**Examples:**

.. code-block:: bash

   # Start on default port
   pyreact-framework dev
   
   # Start on custom port
   pyreact-framework dev --port 8080
   
   # Start and open browser
   pyreact-framework dev --open

pyreact-framework build
~~~~~~~~~~~~~~~~~~~~~~~

Build the project for production.

.. code-block:: bash

   pyreact-framework build [options]

**Options:**

- ``--output`` - Output directory (default: 'dist')
- ``--mode`` - Build mode ('production' or 'development')

**Examples:**

.. code-block:: bash

   # Build for production
   pyreact-framework build
   
   # Build with custom output
   pyreact-framework build --output build

pyreact-framework serve
~~~~~~~~~~~~~~~~~~~~~~~

Serve the production build.

.. code-block:: bash

   pyreact-framework serve [options]

**Options:**

- ``--port`` - Port number (default: 5000)
- ``--dir`` - Directory to serve (default: 'dist')

**Examples:**

.. code-block:: bash

   # Serve on default port
   pyreact-framework serve
   
   # Serve on custom port
   pyreact-framework serve --port 8080

pyreact-framework test
~~~~~~~~~~~~~~~~~~~~~~

Run tests.

.. code-block:: bash

   pyreact-framework test [options]

**Options:**

- ``--watch`` - Watch for changes
- ``--coverage`` - Generate coverage report
- ``--pattern`` - Test file pattern

**Examples:**

.. code-block:: bash

   # Run all tests
   pyreact-framework test
   
   # Run with coverage
   pyreact-framework test --coverage
   
   # Run specific tests
   pyreact-framework test --pattern "test_components"

pyreact-framework --version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display PyReact version.

.. code-block:: bash

   pyreact-framework --version
   pyreact-framework -v

pyreact-framework --help
~~~~~~~~~~~~~~~~~~~~~~~~

Display help information.

.. code-block:: bash

   pyreact-framework --help
   pyreact-framework -h

Configuration
-------------

Configure your project in ``pyproject.toml``:

.. code-block:: toml

   [tool.pyreact]
   # Entry point
   entry = "src/index.py"
   
   # Output directory
   output = "dist"
   
   # Development server
   dev_port = 3000
   dev_host = "localhost"
   
   # SSR
   ssr = true
   
   # CSS Modules
   css_modules = true
   
   # Source maps
   source_maps = true

Project Structure
-----------------

Standard project structure:

.. code-block:: text

   my-app/
   ├── src/
   │   ├── index.py          # Entry point
   │   ├── components/       # Components
   │   │   ├── Header.py
   │   │   └── Footer.py
   │   ├── styles/           # Styles
   │   │   └── main.css
   │   └── utils/            # Utilities
   ├── tests/                # Tests
   │   ├── test_components.py
   │   └── test_utils.py
   ├── docs/                 # Documentation
   ├── pyproject.toml        # Configuration
   └── README.md

Environment Variables
---------------------

PyReact CLI respects these environment variables:

- ``PYREACT_PORT`` - Default development server port
- ``PYREACT_HOST`` - Default development server host
- ``PYREACT_OUTPUT`` - Default build output directory
- ``NODE_ENV`` - Environment mode ('development' or 'production')

Best Practices
--------------

1. **Use version control** - Initialize git for your project
2. **Configure in pyproject.toml** - Centralize configuration
3. **Use environment variables** - For environment-specific settings
4. **Run tests before build** - Ensure quality before deployment

Next Steps
----------

- :doc:`/getting-started/quickstart` - Quick start guide
- :doc:`/getting-started/tutorial` - Tutorial
- :doc:`/advanced/testing` - Testing guide
