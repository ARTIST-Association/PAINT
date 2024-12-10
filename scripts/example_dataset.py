import argparse

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.dataset import PaintCalibrationDataset
from paint.util import set_logger_config

set_logger_config()


if __name__ == "__main__":
    """
    This is an example script demonstrating how the ``PaintCalibrationDataset`` can be used. This script shows the three
    ways of creating a ``PaintCalibrationDataset``:
    1.) Directly, when the data is already downloaded and a ``root_dir`` containing the data is available.
    2.) From a benchmark file, containing information on variaous calibration IDs and what split they belong to. In this
     case, both a ``benchmark_file`` and a ``root_dir`` for saving the data are required.
    3.) From a single heliostats or list of heliostats. In this case, all calibration items for the provided heliostats
    will be used to create a dataset. Here, a list of heliostats is required.
    """
    # Read in arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--item_type",
        type=str,
        help="The type of item to be loaded -- i.e. raw image, cropped image, flux image, or flux centered image",
        choices=[
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
        ],
        default="calibration_properties",
    )
    args = parser.parse_args()

    # Direct Creation:
    # The root dir needs to be set to the directory containing the data.
    direct_root_dir = f"{PAINT_ROOT}/benchmark_datasets/Benchmark_testy_test/test"
    dataset = PaintCalibrationDataset(
        root_dir=direct_root_dir,
        item_ids=None,
        item_type=args.item_type,
    )

    # From Benchmark:
    # The benchmark file needs to be set to the path of the benchmark file and the root dir to the location the data
    # should be saved.
    benchmark_file = f"{PAINT_ROOT}/benchmark_test/benchmark_testy_test.csv"
    benchmark_root_dir = f"{PAINT_ROOT}/dataset_benchmark_test"
    train, test, val = PaintCalibrationDataset.from_benchmark(
        benchmark_file=benchmark_file,
        root_dir=benchmark_root_dir,
        item_type=args.item_type,
        download=True,
    )

    # From Heliostat:
    # The list of heliostats must be provided (if ``None`` data for all heliostats will be downloaded) and the root dir
    # must be selected to the location, the data should be saved.
    heliostats = ["AA39", "AA23"]
    heliostat_root_dir = f"{PAINT_ROOT}/dataset_heliostat_test"
    heliostat_dataset = PaintCalibrationDataset.from_heliostats(
        heliostats=heliostats,
        root_dir=heliostat_root_dir,
        item_type=args.item_type,
        download=True,
    )
