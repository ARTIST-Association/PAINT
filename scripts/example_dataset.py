import argparse
import pathlib

from paint import PAINT_ROOT
from paint.data.dataset import PaintCalibrationDataset
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root_dir",
        type=pathlib.Path,
        help="Root directory containing data.",
        default=f"{PAINT_ROOT}/benchmark_datasets/Benchmark_testy_test/test",
    )
    parser.add_argument(
        "--item_ids",
        type=int,
        help="List of calibration item IDs to load.",
        nargs="+",
        default=[60445, 60935, 61864, 62302],
    )
    parser.add_argument(
        "--item_type",
        type=str,
        help="The type of item to be loaded -- i.e. raw image, cropped image, flux image, or flux centered image",
        default="calibration_properties",
    )
    args = parser.parse_args()

    dataset = PaintCalibrationDataset(
        root_dir=args.root_dir, item_ids=args.item_ids, item_type=args.item_type
    )
