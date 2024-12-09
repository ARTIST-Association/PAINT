import argparse
import pathlib

from paint import PAINT_ROOT
from paint.data import StacClient
from paint.data.dataset import PaintCalibrationDataset
from paint.data.dataset_splits import DatasetSplitter
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    """
    This script demonstrates the full workflow for loading a ``torch.Dataset`` based on a given benchmark, specifically
    it includes:
    - Downloading the necessary metadata to generate the dataset splits.
    - Generating the dataset splits.
    - Creating a ``torch.Dataset`` based on these splits, if necessary, downloading the appropriate data.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metadata_input",
        type=pathlib.Path,
        help="File containing the metadata required to generate the dataset splits.",
        default=f"{PAINT_ROOT}/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--output_dir",
        type=pathlib.Path,
        help="Root directory to save outputs.",
        default=f"{PAINT_ROOT}/benchmarks",
    )
    parser.add_argument(
        "--split_type",
        type=str,
        help="The split type to apply.",
        default="azimuth",
    )
    parser.add_argument(
        "--train_size",
        type=int,
        help="The size of the training split.",
        default=10,
    )
    parser.add_argument(
        "--val_size",
        type=int,
        help="The size of the validation split.",
        default=30,
    )
    parser.add_argument(
        "--remove_unused_data",
        type=bool,
        help="Whether to remove unused data or not.",
        default=True,
    )
    parser.add_argument(
        "--item_type",
        type=str,
        help="The type of item to be loaded -- i.e. raw image, cropped image, flux image, or flux centered image",
        default="calibration_properties",
    )
    args = parser.parse_args()

    metadata_file = args.metadata_input

    # Check if the metadata file has already been downloaded, if not download it.
    if not metadata_file.exists():
        # Create STAC client to download the metadata.
        output_dir_for_stac = metadata_file.parent
        client = StacClient(output_dir=output_dir_for_stac)
        client.get_heliostat_metadata(heliostats=None)

    # Set the correct folder to save the benchmark splits.
    splits_output_dir = args.output_dir / "splits"
    splitter = DatasetSplitter(
        input_file=args.metadata_input,
        output_dir=splits_output_dir,
        remove_unused_data=args.remove_unused_data,
    )

    # Generate the splits, they will be saved automatically to the defined location.
    _ = splitter.get_dataset_splits(
        split_type=args.split_type,
        training_size=args.train_size,
        validation_size=args.val_size,
    )

    # Determine name to automatically load the splits into the dataset.
    dataset_benchmark_file = (
        splits_output_dir
        / f"benchmark_split-{args.split_type}_train-{args.train_size}_validation-{args.val_size}.csv"
    )

    # Set the correct folder for the dataset.
    dataset_output_dir = (
        args.output_dir
        / "datasets"
        / f"benchmark_split-{args.split_type}_train-{args.train_size}_validation-{args.val_size}"
        / args.item_type
    )

    # Determine whether to download the data or not:
    # The first time this script is executed locally, the data must be downloaded, afterward no longer.
    if dataset_output_dir.exists():
        dataset_download = False
    else:
        dataset_download = True

    # Initialize dataset from benchmark splits.
    train, test, val = PaintCalibrationDataset.from_benchmark(
        benchmark_file=dataset_benchmark_file,
        root_dir=dataset_output_dir,
        item_type=args.item_type,
        download=dataset_download,
    )
