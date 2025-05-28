import argparse
import pathlib

from paint import PAINT_ROOT
from paint.data.dataset_splits import DatasetSplitter
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    """
    This script demonstrates how dataset splits can be created.

    The ``DatasetSplitter`` class is used to create the dataset splits. This class must be initialized with an
    ``input_file`` that contains the metadata required to generate the splits, and an ``output_dir`` as the directory
    where information on the generated splits will be saved. The ``DatasetSplitter`` always saves the split information
    as a CSV file and returns the split information as a ``pandas.Dataframe``. If additional metadata is required in the
    returned ``pandas.Dataframe``, then the ``remove_unused_data`` boolean can be set to false. This will cause all
    available metadata to be returned.

    The ``DatasetSplitter`` currently supports the following splits:
    - Azimuth split, used by setting `split_type` to "azimuth".
    - Solstice split, used by setting `split_type` to "solstice".
    - Balanced split, used by setting `split_type` to "balanced".
    - High Variance split, used by setting `split_type` to "high_variance".
    More information on the splits is found in the documentation for the ``DatasetSplitter`` class.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=pathlib.Path,
        help="File containing the metadata required to generate the dataset splits.",
        default=f"{PAINT_ROOT}/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--output_dir",
        type=pathlib.Path,
        help="Path to save the extracted dataset splits.",
        default=f"{PAINT_ROOT}/blabababa/benchmark_test",
    )
    args = parser.parse_args()

    splitter = DatasetSplitter(
        input_file=args.input_file, output_dir=args.output_dir, remove_unused_data=False
    )
    # Example for azimuth splits
    azimuth_splits = splitter.get_dataset_splits(
        split_type="azimuth", training_size=10, validation_size=30
    )
    print(
        "The returned azimuth split data frame contains additional metadata which may be useful for plots."
    )
    print(
        "This data frame has the following structure (first five rows):\n",
        azimuth_splits.head(5),
    )
    # Example for solstice splits
    solstice_splits = splitter.get_dataset_splits(
        split_type="solstice", training_size=10, validation_size=30
    )
    print(
        "The returned solstice split data frame contains additional metadata which may be useful for plots.\n"
        "This data frame has the following structure (first five rows):\n",
        solstice_splits.head(5),
    )
    # Example for balanced splits
    balanced_splits = splitter.get_dataset_splits(
        split_type="balanced", training_size=10, validation_size=30
    )
    print(
        "The returned balanced split data frame contains additional metadata which may be useful for plots.\n"
        "This data frame has the following structure (first five rows):\n",
        solstice_splits.head(5),
    )
    # Example for balanced splits
    high_variance_splits = splitter.get_dataset_splits(
        split_type="high_variance", training_size=10, validation_size=30
    )
    print(
        "The returned high-variance split data frame contains additional metadata which may be useful for plots.\n"
        "This data frame has the following structure (first five rows):\n",
        solstice_splits.head(5),
    )
