.. _workflow:

Full Calibration Benchmark Workflow Example
===========================================

.. note::

    You can find the corresponding ``Python`` script for this tutorial here:
    https://github.com/ARTIST-Association/PAINT/blob/main/scripts/example_benchmark_dataset_full_workflow.py

We provide an executable example of how ``PAINT`` calibration data can be used directly in further applications. When executed, the script performs the following steps:

- Downloads the necessary metadata to generate benchmark splits (if not already downloaded).
- Generates the dataset benchmark splits.
- Initializes a ``torch.Dataset`` based on these splits (downloading data if necessary).

This is the one script you can use if you want to get your hands on ``PAINT`` data as quickly as possible without coding at all yourself!

Script Arguments
~~~~~~~~~~~~~~~~

The script accepts the following command-line arguments:

- ``metadata_input``
  Path to the file containing the metadata required to generate the dataset splits.

- ``output_dir``
  Root directory where all outputs and data will be saved.

- ``split_type``
  The benchmark dataset split type to apply.

- ``train_size``
  The number of training samples required per heliostat. The total training size depends on the number of heliostats.

- ``val_size``
  The number of validation samples required per heliostat. The total validation size also depends on the number of heliostats.

- ``remove_unused_data``
  Whether to remove metadata not required to load benchmark splits. This data may still be useful for plots or inspection.

- ``item_type``
  The type of calibration item to load, e.g., raw image, cropped image, flux image, flux-centered image, or calibration properties.

Have fun experimenting with the workflow! 🚀
