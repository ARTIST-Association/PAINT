import pathlib
from typing import Any
from unittest.mock import MagicMock, patch

import cv2
import deepdiff
import pandas as pd
import pytest
import torch
from torchvision import transforms

from paint import PAINT_ROOT
from paint.data.dataset import PaintCalibrationDataset


@pytest.fixture
def mock_benchmark_data() -> dict[str, Any]:
    """
    Mock data for testing loading the dataset from a benchmark split.

    Returns
    -------
    dict[str, Any]
        Mock data containing information on the dataset splits.
    """
    return {
        "train": [216331, 240796, 137608],
        "test": [152144, 203718, 215701, 194228],
        "validation": [106293, 99927, 213508],
    }


@pytest.mark.parametrize(
    "item_type, expected",
    [
        [
            "calibration_properties",
            {
                "motor_position": {
                    "axis_1_motor_position": 24102,
                    "axis_2_motor_position": 45672,
                },
                "target_name": "solar_tower_juelich_lower",
                "focal_spot": {
                    "HeliOS": [
                        50.91339202853194,
                        6.387827355938812,
                        123.05104719038366,
                    ],
                    "UTIS": [50.91339204305797, 6.38782606406048, 122.96865463256836],
                },
                "sun_elevation": 24.739052879329904,
                "sun_azimuth": -85.60212008930688,
            },
        ],
        ["raw_image", "152144-raw.png"],
        ["cropped_image", "152144-cropped.png"],
        ["flux_image", "152144-flux.png"],
        ["flux_centered_image", "152144-flux-centered.png"],
    ],
)
def test_initialize_dataset(item_type: str, expected: dict[str, Any] | str) -> None:
    """
    Test initialize the dataset.

    Parameters
    ----------
    item_type : str
        Type of item used for dataset creation.
    expected : dict[str, Any] | str
        Expected item to be found at index 0, or name of the image to be found at index 0.
    """
    # Initialize dataset.
    dataset = PaintCalibrationDataset(
        root_dir=pathlib.Path(PAINT_ROOT)
        / "tests"
        / "data"
        / "test_data"
        / "dataset"
        / "test",
        item_ids=[152144, 194228, 203718, 215701],
        item_type=item_type,
    )
    # Assert length is correct.
    assert len(dataset) == 4
    # Assert the correct item is loaded at index 0.
    if item_type == "calibration_properties":
        assert isinstance(expected, dict)
        assert not deepdiff.DeepDiff(
            dataset[0], expected, ignore_numeric_type_changes=True
        )
    else:
        transform = transforms.ToTensor()
        assert isinstance(expected, str)
        expected_path = (
            pathlib.Path(PAINT_ROOT)
            / "tests"
            / "data"
            / "test_data"
            / "dataset"
            / "test"
            / expected
        )
        expected_image = cv2.imread(str(expected_path))
        expected_image = transform(expected_image)
        assert isinstance(expected_image, torch.Tensor)
        torch.testing.assert_close(dataset[0], expected_image)


@pytest.mark.parametrize(
    "item_type",
    [
        "calibration_properties",
        "raw_image",
        "cropped_image",
        "flux_image",
        "flux_centered_image",
    ],
)
def test_initialize_entire_folder(item_type: str) -> None:
    """
    Test initializing the dataset without ``item_ids`` but based on all data in a folder.

    Parameters
    ----------
    item_type : str
        Type of item used for dataset creation.
    """
    dataset = PaintCalibrationDataset(
        root_dir=pathlib.Path(PAINT_ROOT)
        / "tests"
        / "data"
        / "test_data"
        / "dataset"
        / "test",
        item_ids=None,
        item_type=item_type,
    )
    expected_ids = [152144, 194228, 203718, 215701]
    assert sorted(dataset.item_ids) == sorted(expected_ids)


@pytest.mark.parametrize(
    "item_type, download",
    [
        ["calibration_properties", True],
        ["raw_image", True],
        ["cropped_image", True],
        ["flux_image", True],
        ["flux_centered_image", True],
        ["calibration_properties", False],
        ["raw_image", False],
        ["cropped_image", False],
        ["flux_image", False],
        ["flux_centered_image", False],
    ],
)
@patch("paint.data.dataset.PaintCalibrationDataset._download_benchmark_splits")
def test_from_benchmark(
    mock_request: MagicMock,
    mock_benchmark_data: dict[str, Any],
    item_type: str,
    download: bool,
) -> None:
    """
    Test initializing the dataset form a benchmark split file.

    Parameters
    ----------
    mock_request : MagicMock
        Mock request.
    mock_benchmark_data
        Mock benchmark data containing the splits to be used instead of downloading data.
    item_type : str
        Type of item used for dataset creation.
    download : bool
        Whether to download the data (use mock) or not.
    """
    # Set the return value for the mocked ``_get_raw_data`` function to our test data.
    mock_request.return_value = mock_benchmark_data
    train, test, val = PaintCalibrationDataset.from_benchmark(
        benchmark_file=pathlib.Path(PAINT_ROOT)
        / "tests"
        / "data"
        / "test_data"
        / "test_benchmark.csv",
        root_dir=pathlib.Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "dataset",
        item_type=item_type,
        download=download,
    )
    assert len(train) == 3
    assert len(test) == 4
    assert len(val) == 3

    # Test with Pandas data frame as input instead of file.
    benchmark_df = pd.read_csv(
        pathlib.Path(PAINT_ROOT)
        / "tests"
        / "data"
        / "test_data"
        / "test_benchmark.csv",
        index_col=0,
    )
    train, test, val = PaintCalibrationDataset.from_benchmark(
        benchmark_file=benchmark_df,
        root_dir=pathlib.Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "dataset",
        item_type=item_type,
        download=download,
    )
    assert len(train) == 3
    assert len(test) == 4
    assert len(val) == 3


@pytest.mark.parametrize(
    "item_type, heliostats",
    [
        ["calibration_properties", None],
        ["raw_image", None],
        ["cropped_image", None],
        ["flux_image", None],
        ["flux_centered_image", None],
        ["calibration_properties", ["AA23"]],
        ["raw_image", ["AA23"]],
        ["cropped_image", ["AA23"]],
        ["flux_image", ["AA23"]],
        ["flux_centered_image", ["AA23"]],
    ],
)
def test_from_heliostats(item_type: str, heliostats: list[str] | None) -> None:
    """
    Test initializing the dataset form a list of heliostats.

    Note: This test doesn't actually test this functionality properly, since this can only occur when we download
    the data. To avoid download in a test, this function only ensures that the logic of the method works and the
    actual data referenced in the ``root_dir`` is not from the heliostats provided.

    Parameters
    ----------
    item_type : str
        Type of item used for dataset creation.
    heliostats : list[str] | None
        Heliostats used to create the dataset. If no heliostats are provided, data from all heliostats is used
        (Default: ``None``).
    """
    dataset = PaintCalibrationDataset.from_heliostats(
        root_dir=pathlib.Path(PAINT_ROOT)
        / "tests"
        / "data"
        / "test_data"
        / "dataset"
        / "test",
        heliostats=heliostats,
        item_type=item_type,
        download=False,
    )
    expected_ids = [152144, 194228, 203718, 215701]
    assert sorted(dataset.item_ids) == sorted(expected_ids)


def test_dataset_with_wrong_item_type() -> None:
    """Test the dataset with and ``item_type`` that is invalid, causing the class to raise an error."""
    with pytest.raises(ValueError):
        _ = PaintCalibrationDataset(
            root_dir=pathlib.Path(PAINT_ROOT)
            / "tests"
            / "data"
            / "test_data"
            / "dataset"
            / "test",
            item_ids=None,
            item_type="an_invalid_type",
        )


def test_dataset_with_invalid_root() -> None:
    """Test the dataset by initializing with a ``root_dir`` that is invalid, causing the class to raise an error."""
    with pytest.raises(FileNotFoundError):
        _ = PaintCalibrationDataset(
            root_dir=pathlib.Path(PAINT_ROOT)
            / "tests"
            / "data"
            / "test_data"
            / "A_non_existent_dir",
            item_ids=None,
            item_type="calibration_properties",
        )


def test_str_method() -> None:
    """Test the string representation of the dataset."""
    root_dir = (
        pathlib.Path(PAINT_ROOT) / "tests" / "data" / "test_data" / "dataset" / "test"
    )
    dataset = PaintCalibrationDataset(
        root_dir=root_dir,
        item_ids=None,
        item_type="calibration_properties",
    )
    expected = (
        "This is a dataset containing calibration items from the PAINT database:\n"
        f"-The root directory is {root_dir}\n"
        "-The file identifier is -calibration-properties.json\n"
        "-The dataset contains 4 items\n"
    )
    assert str(dataset) == expected


def test_from_benchmark_fails_with_incorrect_dataframe(
    tmp_path: pathlib.Path,
) -> None:
    """
    Verifies that from_benchmark raises ValueError when the input DataFrame has incorrect columns.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Fixture to the temporary folder.
    """
    # Create invalid data frame.
    invalid_df = pd.DataFrame(columns=["Id", "HeliostatId", "WrongCol"])

    # Expect a ValueError.
    with pytest.raises(ValueError, match="incorrect schema"):
        PaintCalibrationDataset.from_benchmark(
            benchmark_file=invalid_df, root_dir=tmp_path, item_type="raw_image"
        )
