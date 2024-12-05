import argparse

from paint import PAINT_ROOT
from paint.data.dataset import PaintCalibrationDataset
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--item_type",
        type=str,
        help="The type of item to be loaded -- i.e. raw image, cropped image, flux image, or flux centered image",
        default="calibration_properties",
    )
    args = parser.parse_args()

    dataset = PaintCalibrationDataset(
        root_dir=f"{PAINT_ROOT}/benchmark_datasets/Benchmark_testy_test/test",
        item_ids=None,
        item_type=args.item_type,
    )

    train, test, val = PaintCalibrationDataset.from_benchmark(
        benchmark_file=f"{PAINT_ROOT}/benchmark_test/benchmark_testy_test.csv",
        root_dir=f"{PAINT_ROOT}/AAA_test",
        item_type=args.item_type,
        download=True,
    )
