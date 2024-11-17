from unittest.mock import patch

import pytest
import torch

from paint.preprocessing.focal_spot_extractor import (
    FocalSpot,
    compute_center_of_intensity,
    convert_xy_to_enu,
    detect_focal_spot,
    get_marker_coordinates,
)
from paint.util.paint_mappings import MFT, STJ_LOWER, STJ_UPPER


def test_get_marker_coordinates_valid_targets():
    """Test `get_marker_coordinates` with valid targets."""
    valid_targets = [1, 7, STJ_LOWER, 4, 5, 6, STJ_UPPER, 3, MFT]

    # Define mock marker data for each valid target
    marker_data = {
        STJ_LOWER: [(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 0, 1)],
        STJ_UPPER: [(1, 1, 1), (1, 1, 2), (2, 1, 1), (2, 1, 2)],
        MFT: [(2, 2, 2), (2, 2, 3), (3, 2, 2), (3, 2, 3)],
    }

    # Patch the implementation to return the mock data for the corresponding targets
    with patch(
        "paint.preprocessing.focal_spot_extractor.mappings", autospec=True
    ) as mock_mappings:
        mock_mappings.STJ_LOWER_ENU = marker_data[STJ_LOWER]
        mock_mappings.STJ_UPPER_ENU = marker_data[STJ_UPPER]
        mock_mappings.MFT_ENU = marker_data[MFT]
        mock_mappings.STJ_LOWER = STJ_LOWER
        mock_mappings.STJ_UPPER = STJ_UPPER
        mock_mappings.MFT = MFT

        for target in valid_targets:
            result = get_marker_coordinates(target)
            assert len(result) == 4
            assert all(isinstance(marker, torch.Tensor) for marker in result)


def test_get_marker_coordinates_invalid_target():
    """Test `get_marker_coordinates` raises ValueError for invalid targets."""
    invalid_target = "INVALID_TARGET"
    with pytest.raises(ValueError, match=f"Unsupported target value: {invalid_target}"):
        get_marker_coordinates(invalid_target)


@pytest.mark.parametrize(
    "aim_point_image, target, expected_output",
    [
        ((0.5, 0.5), 1, torch.tensor([0.5, 0.0, 0.5])),  # Center point
        ((0.25, 0.75), 3, torch.tensor([0.25, 0.0, 0.75])),  # Skewed point
    ],
)
def test_convert_xy_to_enu(aim_point_image, target, expected_output):
    """Test `convert_xy_to_enu` with mocked marker coordinates."""
    mock_markers = [
        torch.tensor([0, 0, 0]),  # marker_left_top
        torch.tensor([0, 0, 1]),  # marker_left_bottom
        torch.tensor([1, 0, 0]),  # marker_right_top
        torch.tensor([1, 0, 1]),  # marker_right_bottom
    ]

    with patch(
        "paint.preprocessing.focal_spot_extractor.get_marker_coordinates",
        return_value=mock_markers,
    ):
        result = convert_xy_to_enu(aim_point_image, target)

    torch.testing.assert_close(result, expected_output, atol=1e-2, rtol=1e-2)


@pytest.mark.parametrize(
    "flux, threshold, expected_center",
    [
        (torch.ones(10, 10), 0.0, (0.5, 0.5)),  # Uniform flux
        (torch.eye(10), 0.1, (0.5, 0.5)),  # Weighted center of diagonal
        (torch.zeros(10, 10), 0.0, (0.5, 0.5)),  # No intensity defaults to center
        (
            torch.tensor([[float("nan"), 0], [0, float("nan")]]),
            0.0,
            (0.5, 0.5),
        ),  # NaN values
    ],
)
def test_compute_center_of_intensity(flux, threshold, expected_center):
    """Test `compute_center_of_intensity` for various flux distributions."""
    result = compute_center_of_intensity(flux, threshold)
    assert result == pytest.approx(expected_center, rel=1e-2)


def test_compute_center_of_intensity_invalid_flux():
    """Test `compute_center_of_intensity` raises ValueError for invalid flux tensors."""
    invalid_flux = torch.rand(3, 3, 3)  # 3D tensor
    with pytest.raises(ValueError, match="Expected a 2D tensor, got 3 dimensions."):
        compute_center_of_intensity(invalid_flux)


def test_detect_focal_spot():
    """Test `detect_focal_spot` end-to-end using a mocked UTIS model and mocked marker coordinates."""
    mock_utis = torch.nn.Identity()
    image = torch.ones(16, 16)
    target = 1

    mock_markers = [
        torch.tensor([0, 0, 0]),  # marker_left_top
        torch.tensor([0, 0, 1]),  # marker_left_bottom
        torch.tensor([1, 0, 0]),  # marker_right_top
        torch.tensor([1, 0, 1]),  # marker_right_bottom
    ]

    with patch(
        "paint.preprocessing.focal_spot_extractor.get_marker_coordinates",
        return_value=mock_markers,
    ):
        focal_spot = detect_focal_spot(image, target, utis=mock_utis)

    assert isinstance(focal_spot, FocalSpot)
    assert focal_spot.flux.shape == torch.Size([16, 16])
    assert isinstance(focal_spot.aim_point_image, tuple)
    assert isinstance(focal_spot.aim_point, torch.Tensor)


def test_detect_focal_spot_invalid_inputs():
    """Test `detect_focal_spot` handles invalid inputs."""
    mock_utis = torch.nn.Identity()
    invalid_image = torch.rand(3, 3, 3)  # Invalid dimensions
    target = 1

    with pytest.raises(ValueError, match="Expected a 2D tensor, got 3 dimensions."):
        detect_focal_spot(invalid_image, target, utis=mock_utis)

    with pytest.raises(ValueError, match="UTIS model must be provided."):
        detect_focal_spot(torch.ones(16, 16), target, utis=None)
