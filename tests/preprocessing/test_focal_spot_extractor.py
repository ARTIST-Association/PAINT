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


@pytest.fixture(scope="module")
def sample_focal_spot() -> FocalSpot:
    """
    Create a sample ``FocalSpot`` object for testing purposes.

    Returns
    -------
    FocalSpot
        Sample ``FocalSpot`` object.
    """
    flux = torch.ones(256, 256)
    aim_point_image = (0.5, 0.5)
    aim_point = torch.tensor([1.0, 1.0, 1.0])
    return FocalSpot.from_flux(flux, aim_point_image, aim_point)


@pytest.fixture(scope="module")
def temp_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Create a temporary directory for testing file I/O.

    Returns
    -------
    Path
        Temporary directory for testing purposes.
    """
    return tmp_path_factory.mktemp("temp_dir")


@pytest.fixture(scope="module")
def utis_model() -> torch.jit.ScriptModule:
    """
    Load the UTIS model once for all test cases.

    Returns
    -------
    torch.jit.ScriptModule
        The loaded UTIS model.
    -------
    """
    return torch.jit.load(
        "tests/preprocessing/test_data/utis_model_scripted.pt", map_location="cpu"
    )


def test_focal_spot_save_and_load(sample_focal_spot: FocalSpot, temp_dir: Path) -> None:
    """
    Test saving and loading the ``FocalSpot`` object.

    Parameters
    ----------
    sample_focal_spot : FocalSpot
        Sample ``FocalSpot`` object.
    temp_dir : Path
        Temporary directory for testing purposes.
    """
    save_path = temp_dir / "test_focal_spot"

    # Save the focal spot.
    sample_focal_spot.save(save_path)

    # Check if files exist.
    assert (save_path.with_name(f"{save_path.name}_flux.png")).exists()
    assert (save_path.with_name(f"{save_path.name}_metadata.json")).exists()

    # Load the focal spot.
    loaded_focal_spot = FocalSpot.load(save_path)

    # Validate loaded data.
    torch.testing.assert_close(loaded_focal_spot.flux, sample_focal_spot.flux)
    assert loaded_focal_spot.aim_point_image == sample_focal_spot.aim_point_image
    torch.testing.assert_close(loaded_focal_spot.aim_point, sample_focal_spot.aim_point)


@pytest.mark.parametrize(
    "flux, threshold, expected_center",
    [
        (torch.zeros(10, 10), 0.0, (0.5, 0.5)),  # No intensity defaults to center
    ],
)
def test_compute_center_of_intensity(
    flux: torch.Tensor, threshold: float, expected_center: tuple[float, float]
) -> None:
    """
    Test ``compute_center_of_intensity`` for various flux distributions.

    Parameters
    ----------
    flux : torch.Tensor
        A 2D tensor representing the flux/intensity image.
    threshold : float, optional
        Minimum intensity value for pixels to be included in the calculation (Default: `0.0`).
    expected_center : tuple[float, float]
        Expected center of intensity.
    """
    assert compute_center_of_intensity(flux, threshold) == pytest.approx(
        expected_center, rel=1e-2
    )


def test_get_marker_coordinates_invalid_target() -> None:
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
def test_detect_focal_spot(
    image_path: Path,
    target: str,
    expected_aimpoint: torch.Tensor,
    utis_model: torch.jit.ScriptModule,
) -> None:
    """
    Test ``detect_focal_spot`` end-to-end using a loaded UTIS model and test images.

    Parameters
    ----------
    image_path : Path
        Path to test image to load.
    target : str
        Target to consider.
    expected_aimpoint : torch.Tensor
        Expected aimpoint.
    utis_model : torch.jit.ScriptModule
        Loaded UTIS model.
    """
    # Load the image.
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Image not found at {image_path}"
    image_tensor = torch.tensor(image, dtype=torch.float32) / 255.0

    # Perform focal spot detection.
    focal_spot = detect_focal_spot(image_tensor, target, utis_model=utis_model)

    # Validate the focal spot.
    assert isinstance(focal_spot, FocalSpot)
    assert focal_spot.flux.shape == image_tensor.shape
    assert isinstance(focal_spot.aim_point_image, tuple)
    assert isinstance(focal_spot.aim_point, torch.Tensor)

    # Check if the detected aimpoint matches the expected aimpoint.
    torch.testing.assert_close(
        focal_spot.aim_point, expected_aimpoint, atol=1e-3, rtol=1e-3
    )
