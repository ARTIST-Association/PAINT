import argparse
import pathlib

from paint import PAINT_ROOT
from paint.data.dataset_splits import DatasetSplitter
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
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
        default=f"{PAINT_ROOT}/benchmark_test",
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
        azimuth_splits.head(5)
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
