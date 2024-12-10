import argparse
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data import StacClient
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    """
    This is an example script demonstrating how the STAC client can be used to download all the data contained within
    a dataset split file.

    NOTE: This functionality is also included within the `torch.Dataset` and is therefore only required if the data is
    required without generating a dataset.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dataset_splits",
        type=pathlib.Path,
        help="File containing the information on the dataset splits.",
        default=f"{PAINT_ROOT}/benchmark_test/Benchmark_split-azimuth_train-10_validation-30.csv",
    )
    parser.add_argument(
        "--output_dir",
        type=pathlib.Path,
        help="Path to save the extracted dataset splits.",
        default=f"{PAINT_ROOT}/benchmark_datasets",
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        choices=[
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
        ],
        default=["calibration_properties"],
    )
    args = parser.parse_args()

    # Determine the name of the benchmark split being determined.
    benchmark_name = args.input_dataset_splits.name.split(".")[0]
    base_output_dir = args.output_dir
    full_output_dir = base_output_dir / benchmark_name

    # Create STAC client.
    client = StacClient(output_dir=full_output_dir)

    # Read in dataset splits file.
    splits = pd.read_csv(args.input_dataset_splits)

    for split_name, split_data in splits.groupby(mappings.SPLIT_KEY):
        number_items = len(split_data)
        with tqdm(
            total=number_items,
            desc=f"Downloading benchmark data for the {split_name} split",
            unit="Item",
        ) as pbar:
            with ThreadPoolExecutor() as executor:
                # Create a list of future objects.
                futures = [
                    executor.submit(
                        client.get_single_calibration_item_by_id,
                        heliostat_id=item[mappings.HELIOSTAT_ID],
                        item_id=item[mappings.ID_INDEX],
                        filtered_calibration_keys=args.filtered_calibration,
                        benchmark_split=item[mappings.SPLIT_KEY],
                        verbose=False,
                        pbar=pbar,
                    )
                    for _, item in split_data.iterrows()
                ]
                # Wait for all tasks to complete.
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        # Handle exceptions from individual tasks.
                        print(f"Error in thread execution: {e}")
