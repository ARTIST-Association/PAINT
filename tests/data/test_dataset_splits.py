import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pandas import Timestamp

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.dataset_splits import DatasetSplitter


@pytest.mark.parametrize(
    "remove_unused_data, split_type, training_size, validation_size, expected_splits",
    [
        (
            True,
            "azimuth",
            3,
            3,
            {
                "HeliostatId": {
                    77399: "AA23",
                    203321: "AA23",
                    62302: "AA23",
                    199617: "AA23",
                    253429: "AA23",
                    254084: "AA23",
                    222963: "AA23",
                    246253: "AA23",
                    212358: "AA23",
                    225295: "AA23",
                },
                "Split": {
                    77399: "train",
                    203321: "train",
                    62302: "train",
                    199617: "test",
                    253429: "test",
                    254084: "test",
                    222963: "test",
                    246253: "validation",
                    212358: "validation",
                    225295: "validation",
                },
            },
        ),
        (
            True,
            "solstice",
            3,
            3,
            {
                "HeliostatId": {
                    222963: "AA23",
                    225295: "AA23",
                    212358: "AA23",
                    203321: "AA23",
                    199617: "AA23",
                    246253: "AA23",
                    253429: "AA23",
                    254084: "AA23",
                    77399: "AA23",
                    62302: "AA23",
                },
                "Split": {
                    222963: "validation",
                    225295: "validation",
                    212358: "validation",
                    203321: "test",
                    199617: "test",
                    246253: "test",
                    253429: "test",
                    254084: "train",
                    77399: "train",
                    62302: "train",
                },
            },
        ),
        (
            False,
            "solstice",
            3,
            3,
            {
                "HeliostatId": {
                    222963: "AA23",
                    225295: "AA23",
                    212358: "AA23",
                    203321: "AA23",
                    199617: "AA23",
                    246253: "AA23",
                    253429: "AA23",
                    254084: "AA23",
                    77399: "AA23",
                    62302: "AA23",
                },
                "Azimuth": {
                    222963: -6.400352313789926,
                    225295: 81.83915757811221,
                    212358: 66.41160685040921,
                    203321: -56.13534862708945,
                    199617: -24.27562868172698,
                    246253: 0.6579483837589489,
                    253429: -15.977388041420308,
                    254084: -10.322274676749569,
                    77399: -58.76801724645433,
                    62302: -42.01706826036833,
                },
                "Elevation": {
                    222963: 62.3279159365105,
                    225295: 37.04787945593409,
                    212358: 45.213616680026576,
                    203321: 46.12541005936384,
                    199617: 48.83409042343407,
                    246253: 45.16393436924701,
                    253429: 36.73122895223354,
                    254084: 33.49675640446808,
                    77399: 15.887782919284154,
                    62302: 8.527271132686408,
                },
                "DateTime": {
                    222963: Timestamp("2023-06-16 09:48:04"),
                    225295: Timestamp("2023-06-27 05:39:56"),
                    212358: Timestamp("2023-05-31 06:35:41"),
                    203321: Timestamp("2023-05-13 12:00:13"),
                    199617: Timestamp("2023-04-21 10:37:26"),
                    246253: Timestamp("2023-09-07 09:30:42"),
                    253429: Timestamp("2023-09-26 10:16:52"),
                    254084: Timestamp("2023-10-06 09:57:10"),
                    77399: Timestamp("2022-03-05 14:29:04"),
                    62302: Timestamp("2022-01-18 13:44:45"),
                },
                "Split": {
                    222963: "validation",
                    225295: "validation",
                    212358: "validation",
                    203321: "test",
                    199617: "test",
                    246253: "test",
                    253429: "test",
                    254084: "train",
                    77399: "train",
                    62302: "train",
                },
            },
        ),
    ],
)
def test_dataset_splits(
    remove_unused_data: bool,
    split_type: str,
    training_size: int,
    validation_size: int,
    expected_splits: dict[str, Any],
) -> None:
    """
    Test the dataset splitter with a small test dataset.

    Parameters
    ----------
    remove_unused_data : bool
        Indicating whether unused metadata should be removed.
    split_type : str
        Type of split to be performed.
    training_size : int
        Size of the training set.
    validation_size : int
        Size of the validation set.
    expected_splits : dict[str, Any]
        Dictionary of expected splits.
    """
    test_data_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "test_metadata.csv"
    )
    expected_splits_df = pd.DataFrame(expected_splits)
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = temp_dir
        splitter = DatasetSplitter(
            input_file=test_data_path,
            output_dir=output_dir,
            remove_unused_data=remove_unused_data,
        )
        split = splitter.get_dataset_splits(
            split_type=split_type,
            training_size=training_size,
            validation_size=validation_size,
        )

        assert split.equals(expected_splits_df)


@pytest.mark.parametrize(
    "split_type, training_size, validation_size",
    [
        ("azimuth", 3, 10),
        ("solstice", 10, 1),
        ("this_does_not_exist", 1, 1),
    ],
)
def test_make_dataset_splitter_fail(
    split_type: str, training_size: int, validation_size: int
) -> None:
    """
    Make the dataset splitter fail.

    This test either provides training and validation sizes resulting in an empty list of heliostats or a split type
    that is not valid. All of these combinations lead to failure.

    Parameters
    ----------
    split_type : str
        Type of split to be performed.
    training_size
        Size of the training set.
    validation_size
        Size of the validation set.
    """
    test_data_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "test_metadata.csv"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = temp_dir
        splitter = DatasetSplitter(
            input_file=test_data_path,
            output_dir=output_dir,
        )
        with pytest.raises(ValueError):
            splitter.get_dataset_splits(
                split_type=split_type,
                training_size=training_size,
                validation_size=validation_size,
            )


def test_make_solstice_distance_fail() -> None:
    """Make the solstice distance calculation fail."""
    with pytest.raises(ValueError):
        DatasetSplitter._get_nearest_solstice_distance(
            timestamp=Timestamp("2023-06-16 09:48:04"),
            season="bob_marley_is_not_a_season",
        )


@pytest.mark.parametrize("split_type", ["kmeans", "knn"])
def test_dataset_splits_kmeans_and_knn(split_type: str) -> None:
    """Test the new splits (kmeans and knn)."""
    test_data_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "test_metadata.csv"
    )
    training_size = 3
    validation_size = (
        3  # This number will be used both for the validation and for test samples.
    )
    expected_total = training_size + 2 * validation_size  # 3 + 2*3 = 9 rows

    with tempfile.TemporaryDirectory() as temp_dir:
        splitter = DatasetSplitter(
            input_file=test_data_path,
            output_dir=temp_dir,
            remove_unused_data=True,
        )
        split = splitter.get_dataset_splits(
            split_type=split_type,
            training_size=training_size,
            validation_size=validation_size,
        )

        # Check that the total number of rows is as expected.
        assert len(split) == expected_total, (
            f"For {split_type} split, expected {expected_total} rows, got {len(split)}."
        )

        # Check that the split labels are distributed correctly.
        counts = split[mappings.SPLIT_KEY].value_counts().to_dict()
        assert counts.get(mappings.TRAIN_INDEX, 0) == training_size, (
            f"For {split_type} split, expected {training_size} training rows, got {counts.get(mappings.TRAIN_INDEX, 0)}."
        )
        assert counts.get(mappings.TEST_INDEX, 0) == validation_size, (
            f"For {split_type} split, expected {validation_size} test rows, got {counts.get(mappings.TEST_INDEX, 0)}."
        )
        assert counts.get(mappings.VALIDATION_INDEX, 0) == validation_size, (
            f"For {split_type} split, expected {validation_size} validation rows, got {counts.get(mappings.VALIDATION_INDEX, 0)}."
        )


def test_invalid_split_type() -> None:
    """Test failure when an invalid split type is provided."""
    test_data_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "test_metadata.csv"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        splitter = DatasetSplitter(
            input_file=test_data_path, output_dir=temp_dir, remove_unused_data=True
        )

        with pytest.raises(ValueError, match=r"The split type must be one of *"):
            splitter.get_dataset_splits(
                split_type="invalid_split", training_size=3, validation_size=3
            )


@pytest.mark.parametrize("split_type", ["kmeans"])
def test_not_small_clusters(split_type: str) -> None:
    """Test small cluster (kmeans and knn)."""
    test_data_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "test_metadata.csv"
    )
    training_size = 2
    validation_size = (
        4  # This number will be used both for the validation and for test samples.
    )
    expected_total = training_size + 2 * validation_size

    with tempfile.TemporaryDirectory() as temp_dir:
        splitter = DatasetSplitter(
            input_file=test_data_path,
            output_dir=temp_dir,
            remove_unused_data=True,
        )
        split = splitter.get_dataset_splits(
            split_type=split_type,
            training_size=training_size,
            validation_size=validation_size,
        )

        # Check that the total number of rows is as expected.
        assert len(split) == expected_total, (
            f"For {split_type} split, expected {expected_total} rows, got {len(split)}."
        )

        # Check that the split labels are distributed correctly.
        counts = split[mappings.SPLIT_KEY].value_counts().to_dict()
        assert counts.get(mappings.TRAIN_INDEX, 0) == training_size, (
            f"For {split_type} split, expected {training_size} training rows, got {counts.get(mappings.TRAIN_INDEX, 0)}."
        )
        assert counts.get(mappings.TEST_INDEX, 0) == validation_size, (
            f"For {split_type} split, expected {validation_size} test rows, got {counts.get(mappings.TEST_INDEX, 0)}."
        )
        assert counts.get(mappings.VALIDATION_INDEX, 0) == validation_size, (
            f"For {split_type} split, expected {validation_size} validation rows, got {counts.get(mappings.VALIDATION_INDEX, 0)}."
        )
