from pathlib import Path

import cv2
import numpy as np
import pytest

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.target_cropper import (
    crop_image_with_template_matching,
    get_marker_data,
    load_and_preprocess_image,
)


@pytest.mark.parametrize(
    "image_name, target_id, expected_name",
    [
        ("stj_image", mappings.STJ_LOWER, "stj_lower"),
        ("stj_image", mappings.STJ_UPPER, "stj_upper"),
        ("mft_image", mappings.MFT, "mft_crop"),
    ],
)
def test_target_cropper(image_name: str, target_id: str, expected_name: str):
    """
    Test the target cropper by comparing to cropped images for each target.

    Parameters
    ----------
    image_name : str
        Name of the image to be cropped.
    target_id : str
        ID of the target.
    expected_name : str
        Name of the expected file used to verify the crop.
    """
    image_path = Path(PAINT_ROOT) / "tests" / "data" / "test_data" / f"{image_name}.png"
    expected_path = (
        Path(PAINT_ROOT) / "tests" / "data" / "test_data" / f"{expected_name}.png"
    )
    expected_cropped = cv2.imread(str(expected_path))
    cropped_result = crop_image_with_template_matching(
        image_path=image_path, target=target_id
    )
    np.testing.assert_allclose(cropped_result, expected_cropped, atol=1.5, rtol=0.05)

    resized_image = load_and_preprocess_image(image_path, resize=True)
    assert resized_image.shape[0] == mappings.DESTINATION_SIZE[1]
    assert resized_image.shape[1] == mappings.DESTINATION_SIZE[0]


def test_make_marker_data_fail() -> None:
    """Test failure for an incorrect target ID."""
    with pytest.raises(ValueError):
        get_marker_data(target=23)


@pytest.mark.parametrize(
    "image_name, target_id",
    [("stj_image", mappings.MFT)],
)
def test_resize_and_fail(image_name: str, target_id: str):
    """
    Test failure when marker cannot be identified.

    Parameters
    ----------
    image_name : str
        Name of the image to be cropped.
    target_id : str
        ID of the target
    """
    image_path = Path(PAINT_ROOT) / "tests" / "data" / "test_data" / f"{image_name}.png"

    with pytest.raises(RuntimeError):
        crop_image_with_template_matching(image_path=image_path, target=target_id)
