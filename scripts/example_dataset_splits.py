import argparse

from paint import PAINT_ROOT
from paint.data.dataset_splits import DatasetSplitter

if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file",
        type=str,
        help="File containing the metadata required to generate the dataset splits.",
        default=f"{PAINT_ROOT}/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the extracted dataset splits.",
        default=f"{PAINT_ROOT}/benchmark_test",
    )
    args = parser.parse_args()

    splitter = DatasetSplitter(input_file=args.input_file, output_dir=args.output_dir)
    print("YUP WE ARE HERE")
