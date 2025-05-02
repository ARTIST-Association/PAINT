.. _stac-client:

StacClient Tutorial
===================

.. note::

    You can find the corresponding ``Python`` script for this tutorial here:
    https://github.com/ARTIST-Association/PAINT/blob/main/scripts/example_stac_client.py


This tutorial demonstrates how to use the ``StacClient`` to browse and download data from the `PAINT database <https://paint-database.org>`_ within a Python program. This client builds on the `pystac` library with specific functionality for the PAINT database.

Basic Usage
-----------

The ``StacClient`` provides convenient methods to access various datasets. An example script demonstrating its use can be found at: ``scripts/example_stac_client.py``.

First, initialize the client with a path where downloaded data will be stored:

.. code-block:: python

    client = StacClient(output_dir=args.output_dir)

Downloading Tower Measurements
------------------------------

You can easily download tower measurements for the power plant with the global ID ``WRI1030197`` in Jülich:

.. code-block:: python

    client.get_tower_measurements()

Downloading Weather Data
------------------------

You can also fetch weather data from sources like Jülich or DWD over a specified time period:

.. code-block:: python

    client.get_weather_data(
        data_sources=args.weather_data_sources,
        start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
        end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
    )

Downloading Heliostat Data
--------------------------

The ``StacClient`` can download data from one or more heliostats:

.. code-block:: python

    client.get_heliostat_data(
        heliostats=args.heliostats,
        collections=args.collections,
        filtered_calibration_keys=args.filtered_calibration,
    )

The parameters are defined as follows:

- **heliostats**: A list of heliostat IDs or ``None``. If ``None``, data for all heliostats is downloaded.
- **collections**: A list of STAC collections to download from. Options include calibration data, deflectometry measurements, and heliostat properties. If ``None``, all collections are used.
- **filtered_calibration_keys**: A list of calibration item types to download, such as raw images, cropped images, flux images, or calibration properties. If ``None``, all items are downloaded.

Downloading Heliostat Metadata
------------------------------

If you only need the metadata (e.g., for analysis or plotting), use:

.. code-block:: python

    client.get_heliostat_metadata(heliostats=None)

.. warning::
    Using ``heliostats=None`` will download metadata for *all* heliostats and can take a very long time.
