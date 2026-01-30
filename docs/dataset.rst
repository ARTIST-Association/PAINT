.. _dataset:

PaintCalibrationDataset Tutorial
================================

.. note::

    You can find the corresponding ``Python`` script for this tutorial here:
    https://github.com/ARTIST-Association/PAINT/blob/main/scripts/example_dataset.py

Since multiple calibration items may be required for training an alignment optimization or similar, we have created a
custom ``torch.Dataset`` that loads calibration items from the ``PAINT`` database.

There are three ways of creating a ``PaintCalibrationDataset``:

1. **Direct instantiation from local data**

   This approach is based on calibration data that has already been downloaded and saved in a ``root_dir``:

   .. code-block:: python

      dataset = PaintCalibrationDataset(
           root_dir=direct_root_dir,
           item_ids=None,
           item_type=args.item_type,
       )

   - The ``item_ids`` can be a list indicating which of the items contained in the ``root_dir`` should be used, or
     if ``None``, all items will be used.
   - The ``item_type`` specifies what type of calibration item should be loaded (e.g., raw image, cropped image,
     flux image, flux-centered image, or calibration properties file).

2. **From a benchmark file**

   You can also create the dataset from a benchmark file (see the :information on dataset splits:`splitter` for details). In this case, the ``benchmark_file`` containing information on the train, validation, and test split must be provided:

   .. code-block:: python

      train, test, val = PaintCalibrationDataset.from_benchmark(
           benchmark_file=benchmark_file,
           root_dir=benchmark_root_dir,
           item_type=args.item_type,
           download=True,
      )

   This class method returns three ``torch.Dataset`` instances, one for each split: train, test, and validation.

3. **From heliostat identifiers**

   Finally, the dataset can be created from a single heliostat or a list of heliostats. All calibration items for the
   provided heliostats will be used to construct the dataset:

   .. code-block:: python

      heliostat_dataset = PaintCalibrationDataset.from_heliostats(
           heliostats=heliostats,
           root_dir=heliostat_root_dir,
           item_type=args.item_type,
           download=True,
       )
