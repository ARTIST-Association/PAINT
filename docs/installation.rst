.. _installation:

Installation Guide
==================
PAINT is a Python package that provides tools for accessing, processing, and analyzing operational data from concentrating solar power (CSP) tower plants. We recommend using a dedicated Python 3.9+ virtual environment.

Quick Installation
------------------

You can install the latest stable version of PAINT directly from PyPI using:

.. code-block:: console

    $ pip install paint

Alternatively, you can install the latest development version directly from the official GitHub repository:

.. code-block:: console

    $ pip install git+https://github.com/ARTIST-Association/PAINT

After installation, verify that PAINT is installed correctly by running:

.. code-block:: python

    >>> import paint
    >>> print(paint.__version__)

Installing from Source
----------------------

If you want to contribute to the development of PAINT or need more control over the installation, you can install it locally from source:

1. Clone the repository:

   .. code-block:: console

       $ git clone https://github.com/ARTIST-Association/PAINT.git
       $ cd PAINT

2. Install the package:

   - For a standard installation:

     .. code-block:: console

         $ pip install .

   - For development (editable install with developer dependencies):

     .. code-block:: console

         $ pip install -e ".[dev]"

Virtual Environment (Recommended)
---------------------------------

We strongly recommend using a virtual environment (e.g., `venv` or `conda`) to manage your dependencies:

.. code-block:: console

    $ python -m venv venv
    $ source venv/bin/activate   # On Windows: venv\Scripts\activate
    (venv) $ pip install paint

Troubleshooting
---------------

- Make sure you are using **Python 3.9 or higher**
- If you encounter any issues with dependencies, try upgrading `pip` first:

  .. code-block:: console

      $ pip install --upgrade pip

- For GPU acceleration or large-scale data processing, consider installing additional dependencies manually.

Further Help
------------
For issues, please open a GitHub issue at: https://github.com/ARTIST-Association/PAINT/issues
