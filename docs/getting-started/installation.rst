.. _installation:

Installation
============

PyReact Framework requires Python 3.10 or higher.

Stable Release
--------------

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install pyreact-framework

Development Version
-------------------

Install the latest development version from GitHub:

.. code-block:: bash

   pip install git+https://github.com/wanbnn/pyreact.git

Requirements
------------

PyReact Framework automatically installs the following dependencies:

- ``watchdog>=3.0.0`` - File system monitoring for hot reload
- ``jinja2>=3.1.0`` - Template rendering
- ``pyyaml>=6.0`` - YAML configuration parsing
- ``click>=8.1.0`` - CLI framework (alternative to argparse)

Verification
------------

Verify your installation:

.. code-block:: bash

   pyreact-framework --version

You should see output similar to:

.. code-block:: text

   PyReact Framework v1.0.1

Next Steps
----------

- :doc:`/getting-started/quickstart` - Create your first PyReact app
- :doc:`/getting-started/tutorial` - Follow the step-by-step tutorial
