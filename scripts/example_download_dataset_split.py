import argparse
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data import StacClient
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dataset_splits",
        type=str,
        help="File containing the information on the dataset splits.",
        default=f"{PAINT_ROOT}/benchmark_test/Benchmark_split-azimuth_train-10_validation-30.csv",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the extracted dataset splits.",
        default=f"{PAINT_ROOT}/Benchmark_Datasets",
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=["calibration_properties"],
    )
    args = parser.parse_args()

    # Determine the name of the benchmark split being determined.
    benchmark_name = Path(args.input_dataset_splits).name.split(".")[0]
    base_output_dir = Path(args.output_dir)
    full_output_dir = base_output_dir / benchmark_name

    # Create STAC client.
    client = StacClient(output_dir=full_output_dir)

    # Read in dataset splits file.
    splits = pd.read_csv(args.input_dataset_splits)

    for _, split_data in splits.groupby(mappings.SPLIT_KEY):
        for __, item in split_data.iterrows():
            client.get_single_calibration_item_by_id(
                heliostat_id=item[mappings.HELIOSTAT_ID],
                item_id=item[mappings.ID_INDEX],
                filtered_calibration_keys=args.filtered_calibration,
                benchmark_split=item[mappings.SPLIT_KEY],
            )
