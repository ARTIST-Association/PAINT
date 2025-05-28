Welcome to ``PAINT``
====================
**PAINT** is the first FAIR (Findable, Accessible, Interoperable, Reusable) open-access database for operational data from concentrating solar power (CSP) tower plants. Developed to accelerate research and innovation in renewable energy, PAINT provides over 849 GB of high-resolution, real-world data collected over multiple years from the Jülich solar tower plant in Germany (GPPD ID: WRI1030197).

What is PAINT?
--------------

PAINT aims to break down the barriers to innovation in CSP technologies by offering standardized, high-quality data that supports reproducibility and fair comparisons. The dataset includes:

- Heliostat calibration and deflectometry measurements
- Heliostat kinematic and alignment data
- Fine-grained local weather data
- Extensive metadata following the SpatioTemporal Asset Catalog (STAC) specification

By democratizing access to detailed operational data, PAINT enables the development of:

- Digital twins of heliostat fields
- AI-based calibration and control algorithms
- Predictive maintenance techniques (e.g., soiling or fault detection)
- Improved solar flux-density prediction models

How Does The ``PAINT`` Software Package Help?
---------------------------------------------

This ``PAINT`` package provides the tools to **interact with and analyze** data from the PAINT database. Found in the ``paint.data`` subpackage, this includes:

- A custom ``StacClient`` for browsing and downloading PAINT assets
- Utilities to generate benchmark splits for algorithm testing
- A PyTorch-compatible dataset class for efficient machine learning workflows

Why PAINT Matters
-----------------

Despite the high potential of CSP technology, its progress is hindered by limited access to real operational data. PAINT addresses this gap, offering:

- The first CSP dataset of this scale following FAIR principles
- Support for scalable and reproducible research
- Benchmarks for comparing heliostat calibration and optimization algorithms
- Tools that integrate easily with simulation frameworks, ML libraries, and research pipelines

By fostering openness and lowering the barrier for entry, PAINT invites the global research community to contribute to the future of clean, solar-based energy.

Get Started
-----------

Explore the documentation to learn how to download the data, preprocess it, and build your own benchmarks and datasets. Example scripts and usage guides are included to help you quickly dive into real-world CSP research.

- To find out more about how to use ``PAINT`` check out :ref:`usage`.
- |:sunny:| Visit the official database at: https://paint-database.org |:rocket:|

Quick Install
=============
To install ``PAINT``, run the following in your terminal:

.. code-block:: console

    $ pip install paint

You can check whether your installation was successful by importing ``PAINT`` in ``Python``:

.. code-block:: python

   import paint

You can find more detailed installation instructions in :ref:`installation`.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation
   usage

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
