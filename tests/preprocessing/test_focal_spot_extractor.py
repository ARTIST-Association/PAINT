import json
from pathlib import Path

import cv2
import h5py
import pytest
import torch

from paint.preprocessing.focal_spot_extractor import (
    FocalSpot,
    compute_center_of_intensity,
    detect_focal_spot,
    get_marker_coordinates,
)
from paint.util.paint_mappings import MFT, STJ_LOWER, STJ_UPPER


@pytest.fixture(scope="module")
def sample_focal_spot():
    """Create a sample FocalSpot object for testing."""
    flux = torch.ones(256, 256)
    aim_point_image = (0.5, 0.5)
    aim_point = torch.tensor([1.0, 1.0, 1.0])
    return FocalSpot(flux, aim_point_image, aim_point)


@pytest.fixture(scope="module")
def temp_dir(tmp_path_factory):
    """Create a temporary directory for testing file I/O."""
    return tmp_path_factory.mktemp("temp_dir")


@pytest.fixture(scope="module")
def utis_model():
    """Load the UTIS model once for all test cases."""
    utis_model_path = Path("tests/preprocessing/test_data/utis_model_scripted.pt")
    return torch.jit.load(str(utis_model_path), map_location="cpu")


def test_focal_spot_save_and_load(sample_focal_spot, temp_dir):
    """Test saving and loading the FocalSpot object."""
    save_path = temp_dir / "test_focal_spot"

    # Save the focal spot
    sample_focal_spot.save(save_path)

    # Check if files exist
    assert (save_path.with_name(f"{save_path.name}_flux.h5")).exists()
    assert (save_path.with_name(f"{save_path.name}_metadata.json")).exists()

    # Load the focal spot
    loaded_focal_spot = FocalSpot.load(save_path)

    # Validate loaded data
    torch.testing.assert_close(loaded_focal_spot.flux, sample_focal_spot.flux)
    assert loaded_focal_spot.aim_point_image == sample_focal_spot.aim_point_image
    torch.testing.assert_close(loaded_focal_spot.aim_point, sample_focal_spot.aim_point)


def test_focal_spot_load_invalid_flux(temp_dir):
    """Test that loading fails with invalid flux data."""
    save_path = temp_dir / "test_invalid_flux"

    # Create invalid flux HDF5 file
    with h5py.File(f"{save_path}_flux.h5", "w") as h5_file:
        h5_file.create_dataset("flux", data=[])

    # Create valid metadata file
    metadata = {"aim_point_image": [0.5, 0.5], "aim_point": [1.0, 1.0, 1.0]}
    with open(f"{save_path}_metadata.json", "w") as json_file:
        json.dump(metadata, json_file)

    # Attempt to load
    with pytest.raises(ValueError, match="Flux data is empty."):
        FocalSpot.load(save_path)


@pytest.mark.parametrize(
    "flux, threshold, expected_center",
    [
        (torch.zeros(10, 10), 0.0, (0.5, 0.5)),  # No intensity defaults to center
    ],
)
def test_compute_center_of_intensity(flux, threshold, expected_center):
    """Test compute_center_of_intensity for various flux distributions."""
    result = compute_center_of_intensity(flux, threshold)
    assert result == pytest.approx(expected_center, rel=1e-2)


def test_get_marker_coordinates_invalid_target():
    """Test get_marker_coordinates raises ValueError for invalid targets."""
    with pytest.raises(ValueError, match="Unsupported target value: INVALID_TARGET"):
        get_marker_coordinates("INVALID_TARGET")


@pytest.mark.parametrize(
    "image_path, target, expected_aimpoint",
    [
        (
            Path("tests/preprocessing/test_data/stj_lower.png"),
            STJ_LOWER,
            torch.tensor([0.9369, -3.2300, 36.4410]),
        ),
        (
            Path("tests/preprocessing/test_data/stj_upper.png"),
            STJ_UPPER,
            torch.tensor([0.0996, -3.2300, 43.0595]),
        ),
        (
            Path("tests/preprocessing/test_data/mft_crop.png"),
            MFT,
            torch.tensor([-17.5122, -2.8299, 52.0571]),
        ),
    ],
)
def test_detect_focal_spot(image_path, target, expected_aimpoint, utis_model):
    """Test detect_focal_spot end-to-end using a loaded UTIS model and test images."""
    # Load the image
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Image not found at {image_path}"
    image_tensor = torch.tensor(image, dtype=torch.float32) / 255.0

    # Perform focal spot detection
    focal_spot = detect_focal_spot(image_tensor, target, utis_model=utis_model)

    # Validate the focal spot
    assert isinstance(focal_spot, FocalSpot)
    assert focal_spot.flux.shape == image_tensor.shape
    assert isinstance(focal_spot.aim_point_image, tuple)
    assert isinstance(focal_spot.aim_point, torch.Tensor)

    # Check if the detected aimpoint matches the expected aimpoint
    torch.testing.assert_close(
        focal_spot.aim_point, expected_aimpoint, atol=1e-3, rtol=1e-3
    )
