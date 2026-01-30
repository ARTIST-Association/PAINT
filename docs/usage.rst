.. _usage:

How To Use
==========

To get started with ``PAINT`` we have included a interactive notebook, which is available here: https://github.com/ARTIST-Association/PAINT/blob/main/tutorials/paint_data_tutorial.ipynb.

This tutorial provides an interactive introduction to the PAINT database, demonstrating how to:
- Initialize the STAC client.
- Download and inspect metadata.
- Generate calibration data splits.
- Load calibration data using a dataloader.
- Download and inspect other types of PAINT data.

To run the tutorial make sure you install the tutorial dependencies, i.e.:

.. code-block:: console

    $ pip install "paint-csp[tutorial]"

Most of the concepts covered in the interactive tutorial are also covered in the documentation and associated scripts listed below:

.. toctree::
   :maxdepth: 1

   stac-client
   splitter
   dataset
   workflow
