from pathlib import Path

import cv2
import pytest
import torch

from paint.preprocessing.focal_spot_extractor import (
    FocalSpot,
    compute_center_of_intensity,
    detect_focal_spot,
    get_marker_coordinates,
)
from paint.util.paint_mappings import MFT, STJ_LOWER, STJ_UPPER


def test_get_marker_coordinates_invalid_target():
    """Test `get_marker_coordinates` raises ValueError for invalid targets."""
    invalid_target = "INVALID_TARGET"
    with pytest.raises(ValueError, match=f"Unsupported target value: {invalid_target}"):
        get_marker_coordinates(invalid_target)


@pytest.mark.parametrize(
    "flux, threshold, expected_center",
    [
        (torch.zeros(10, 10), 0.0, (0.5, 0.5)),  # No intensity defaults to center
        (
            torch.tensor([[float("nan"), 0], [0, float("nan")]]),
            0.0,
            (0.5, 0.5),
        ),
    ],
)
def test_compute_center_of_intensity(
    flux: torch.Tensor, threshold: float, expected_center: tuple[float, float]
):
    """
    Test `compute_center_of_intensity` for various flux distributions.

    Parameters
    ----------
    flux : torch.Tensor
        Flux imput image.
    threshold : float
        Threshold used to determine center of intensity.
    expected_center : tuple[float, float]
        Expected center of intensity.
    """
    result = compute_center_of_intensity(flux, threshold)
    assert result == pytest.approx(expected_center, rel=1e-2)


def test_detect_focal_spot_invalid_inputs():
    """Test `detect_focal_spot` handles invalid inputs."""
    mock_utis = torch.nn.Identity()
    invalid_image = torch.rand(3, 3, 3)  # Invalid dimensions
    target = 1

    with pytest.raises(ValueError, match="Expected a 2D tensor, got 3 dimensions."):
        detect_focal_spot(invalid_image, target, utis_model=mock_utis)


@pytest.fixture(scope="module")
def utis_model():
    """Fixture to load the UTIS model once for all test cases."""
    utis_model_path = Path("tests/preprocessing/test_data/utis_model_scripted.pt")
    return torch.jit.load(str(utis_model_path), map_location="cpu")
    # loaded_model = load_model_from_url(UTIS_MODEL_CHECKPOINT)
    # return loaded_model


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
    """
    Test `detect_focal_spot` end-to-end using a loaded UTIS model and test images.

    Parameters
    ----------
    image_path : Path
        Path to the input image.
    target : Union[int, str]
        Calibration target used.
    expected_aimpoint : torch.Tensor
        Expected aimpoint in ENU coordinates.
    utis_model : torch.jit.ScriptModule
        The preloaded UTIS model.
    """
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

    # Output the calculated aimpoint for debugging
    print(f"Calculated Aimpoint: {focal_spot.aim_point.tolist()}")

    # Check if the detected aimpoint matches the expected aimpoint
    torch.testing.assert_close(
        focal_spot.aim_point, expected_aimpoint, atol=1e-3, rtol=1e-3
    )
