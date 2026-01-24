.. _splitter:

DatasetSplitter Tutorial
========================

.. note::

    You can find the corresponding ``Python`` script for this tutorial here:
    https://github.com/ARTIST-Association/PAINT/blob/main/scripts/example_dataset_splits.py

The ``DatasetSplitter`` class is used to create benchmark dataset splits. When working with calibration data and developing alignment algorithms to optimize performance, it is important that the train, test, and validation data are diverse. Currently, there is no standard to benchmark different algorithms, and part of the ``PAINT`` project is to provide this standard.

Therefore, we include methods for generating benchmark splits that can be used for a standardized evaluation process. The following split strategies are currently supported:

Supported Splits
----------------

- **Azimuth Split:**
  This splits the data based on the azimuth of the sun for each considered calibration sample. For a single heliostat:

  - The ``training_size`` indices with the smallest azimuth values are selected for the training split.
  - The ``validation_size`` indices with the largest azimuth values are selected for the validation split.
  - Remaining indices are assigned to the test split.

  This ensures that train and validation splits contain very different samples, resulting in a high level of difficulty and promoting robust calibration methods.

- **Solstice Split:**
  This split is based on the time of year — specifically, how close the measurement date is to the winter or summer solstice. For a single heliostat:

  - The ``training_size`` indices closest to the winter solstice are selected for the training split.
  - The ``validation_size`` indices closest to the summer solstice are selected for the validation split.
  - Remaining indices are assigned to the test split.

  Again, the goal is to create diverse and challenging training and validation datasets.

- **Balanced Split:**
  This method uses k-means clustering on azimuth and elevation features to ensure a stratified selection. The process includes:

  - Clustering the data into ``validation_size`` clusters.
  - Selecting one data point per cluster for the validation split.
  - Selecting another (distinct) point from the same cluster for the test split, if possible.
  - Filling any missing test samples from the overall pool to maintain balance.
  - Assigning the remaining data points to the training split.

  This technique promotes diversity across all splits and ensures that each split represents a balanced coverage of the feature space. It is especially useful for avoiding sampling bias and increasing generalizability.

- **High-Variance Split:**
  This method is based on a k-nearest neighbors (KNN) quality metric using azimuth and elevation as features. For each data point:

  - The average distance to its nearest neighbors (excluding itself) is computed.
  - Data points are sorted in descending order of this average distance.
  - The top ``validation_size`` points (most distinct) go to the validation split.
  - The next ``validation_size`` go to the test split.
  - The bottom ``training_size`` points (most typical) go to the training split.

  This strategy ensures that validation and test samples cover the high-variance regions of the dataset, while the training set focuses on more consistent, representative samples. It’s ideal for stress-testing model performance on edge cases.

Usage Example
-------------

To generate splits, first initialize the class with an ``input_file`` (containing the metadata required to generate the splits) and an ``output_dir`` (where the split information will be saved):

.. code-block:: python

    splitter = DatasetSplitter(
        input_file=args.input_file, output_dir=args.output_dir, remove_unused_data=False
    )

The ``remove_unused_data`` argument indicates whether extra metadata not required for the split calculation should be removed from the returned ``pandas.DataFrame``. This additional metadata may be useful for plotting or detailed analysis of the splits.

To generate the splits, simply call the ``get_dataset_splits()`` function:

.. code-block:: python

    # Example for azimuth splits
    azimuth_splits = splitter.get_dataset_splits(
        split_type="azimuth", training_size=10, validation_size=30
    )

This returns a ``pd.Dataframe`` containing information on the splits, i.e. which samples belong to which split, and also saves this information as a CSV file.
