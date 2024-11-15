import pytest
import torch
from paint.preprocessing.focal_spot_extractor import (
    FocalSpot,
    get_marker_coordinates,
    convert_xy_to_ENU,
    compute_center_of_intensity,
    detect_focal_spot,
)
from unittest.mock import patch


@pytest.mark.parametrize(
    "aim_point_image, target, expected_output",
    [
        ((0.5, 0.5), "mock_target", torch.tensor([0.5, 0, 0.5])),  # Center point
        ((0.25, 0.75), "mock_target", torch.tensor([0.25, 0, 0.75])),  # Skewed point
    ],
)
def test_convert_xy_to_ENU(aim_point_image, target, expected_output):
    """
    Test `convert_xy_to_ENU` with mock marker coordinates.

    Parameters
    ----------
    aim_point_image : tuple
        Relative aim point coordinates.
    target : str
        Target ID.
    expected_output : torch.Tensor
        Expected ENU coordinates.
    """
    # Patch `get_marker_coordinates` to return mock markers
    mock_markers = [
        torch.tensor([0, 0, 0]),  # marker_left_top
        torch.tensor([0, 0, 1]),  # marker_left_bottom
        torch.tensor([1, 0, 0]),  # marker_right_top
        torch.tensor([1, 0, 1]),  # marker_right_bottom
    ]

    with patch("paint.preprocessing.focal_spot_extractor.get_marker_coordinates", return_value=mock_markers):
        result = convert_xy_to_ENU(aim_point_image, target)

    torch.testing.assert_close(result, expected_output, atol=1e-2, rtol=1e-2)

@pytest.mark.parametrize(
    "flux, threshold, expected_center",
    [
        (torch.ones(10, 10), 0.0, (0.5, 0.5)),  # Uniform flux
        (torch.eye(10), 0.1, (0.5, 0.5)),  # Weighted center of diagonal
        (torch.zeros(10, 10), 0.0, (0.5, 0.5)),  # No intensity defaults to center
    ],
)
def test_compute_center_of_intensity(flux, threshold, expected_center):
    """
    Test `compute_center_of_intensity` for various flux distributions.

    Parameters
    ----------
    flux : torch.Tensor
        Flux image to compute center of intensity.
    threshold : float
        Intensity threshold.
    expected_center : tuple
        Expected (x, y) coordinates of the center.
    """
    result = compute_center_of_intensity(flux, threshold)
    assert result == pytest.approx(expected_center, rel=1e-2)

def test_detect_focal_spot():
    """
    Test `detect_focal_spot` end-to-end using a mocked UTIS model and mocked marker coordinates.
    """
    # Mock UTIS model (identity model for testing)
    mock_utis = torch.nn.Identity()

    # Mock input image
    image = torch.ones(16, 16)

    # Mock target
    target = "mock_target"

    # Mock marker coordinates for the target
    mock_markers = [
        torch.tensor([0, 0, 0]),  # marker_left_top
        torch.tensor([0, 0, 1]),  # marker_left_bottom
        torch.tensor([1, 0, 0]),  # marker_right_top
        torch.tensor([1, 0, 1]),  # marker_right_bottom
    ]

    with patch("paint.preprocessing.focal_spot_extractor.get_marker_coordinates", return_value=mock_markers):
        # Run `detect_focal_spot`
        focal_spot = detect_focal_spot(image, target, utis=mock_utis)

    # Assertions
    assert isinstance(focal_spot, FocalSpot)
    assert focal_spot.flux.shape == torch.Size([16, 16])
    assert isinstance(focal_spot.aim_point_image, tuple)
    assert isinstance(focal_spot.aim_point, torch.Tensor)

    # Optional: Add specific checks for the values
    print(f"Flux shape: {focal_spot.flux.shape}")
    print(f"Aimpoint Image: {focal_spot.aim_point_image}")
    print(f"Aimpoint ENU: {focal_spot.aim_point}")