import json
from pathlib import Path
from typing import Union

import cv2
import torch

import paint.util.paint_mappings as mappings


class FocalSpot:
    """
    Data class for storing focal spot information.

    Attributes
    ----------
    flux : torch.Tensor
        Intensity image of the detected focal spot.
    aim_point_image : tuple[float, float]
        Detected center of intensity in image coordinates (height, width).
    aim_point : torch.Tensor
        Detected center of intensity in global coordinates (E, N, U).
    """

    def __init__(self) -> None:
        """
        Private initializer to ensure objects are only created using ``from_flux()`` or ``load()``.

        Initializes attributes with default placeholder values.
        """
        self.flux: torch.Tensor = torch.empty(0)  # Default to an empty tensor
        self.aim_point_image: tuple[float, float] = (0.0, 0.0)  # Default to (0.0, 0.0)
        self.aim_point: torch.Tensor = torch.empty(3)  # Default to an empty tensor of required shape

    @classmethod
    def from_flux(
        cls,
        flux: torch.Tensor,
        aim_point_image: tuple[float, float],
        aim_point: torch.Tensor,
    ) -> "FocalSpot":
        """
        Create a ``FocalSpot`` object from provided data.

        Parameters
        ----------
        flux : torch.Tensor
            Intensity image of the detected focal spot.
        aim_point_image : tuple[float, float]
            Detected center of intensity in image coordinates (height, width).
        aim_point : torch.Tensor
            Detected center of intensity in global coordinates (E, N, U).

        Returns
        -------
        FocalSpot
            Initialized ``FocalSpot`` object.
        """
        instance = cls()
        instance.flux = flux
        instance.aim_point_image = aim_point_image
        instance.aim_point = aim_point
        return instance

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "FocalSpot":
        """
        Load a FocalSpot object from disk.

        Parameters
        ----------
        file_path : Union[str, Path]
            Base path for the focal spot files (without extensions).

        Returns
        -------
        FocalSpot
            Loaded FocalSpot object.
        """
        base_path = Path(file_path)
        flux_path = base_path.with_name(f"{base_path.name}_flux.png")
        metadata_path = base_path.with_name(f"{base_path.name}_metadata.json")

        if not flux_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"Missing required files: {flux_path}, {metadata_path}"
            )

        # Load flux as a grayscale image and convert to tensor
        flux_image = cv2.imread(str(flux_path), cv2.IMREAD_GRAYSCALE)
        if flux_image is None:
            raise ValueError("Flux PNG file is missing or corrupted.")
        flux = torch.tensor(flux_image, dtype=torch.float32) / 255.0

        # Load metadata
        with open(metadata_path, "r") as json_file:
            metadata = json.load(json_file)

        aim_point_image = tuple(metadata["aim_point_image"])
        aim_point = torch.tensor(metadata["aim_point"])

        # Create the FocalSpot instance
        return cls.from_flux(flux, aim_point_image, aim_point)

    def save(self, save_path: Path) -> None:
        """
        Save the focal spot object to disk.

        Parameters
        ----------
        save_path : Path
            Base path (without extension) to save the focal spot data.
        """
        # Ensure all fields are initialized
        if self.flux is None or self.aim_point_image is None or self.aim_point is None:
            raise ValueError("FocalSpot object is not fully initialized.")

        # Normalize flux to the range [0, 255] for saving as PNG
        normalized_flux = (self.flux / self.flux.max() * 255).clamp(0, 255).byte()
        flux_image = normalized_flux.numpy()

        # Save flux as a single-channel grayscale PNG
        cv2.imwrite(f"{save_path}_flux.png", flux_image)

        # Save metadata to JSON
        metadata = {
            "aim_point_image": self.aim_point_image,
            "aim_point": self.aim_point.tolist(),
        }
        with open(f"{save_path}_metadata.json", "w") as json_file:
            json.dump(metadata, json_file, indent=4)


def get_marker_coordinates(target: Union[str, int]) -> tuple[torch.Tensor, ...]:
    """
    Get the specific marker coordinates based on the target.

    Parameters
    ----------
    target : Union[str, int]
        Target ID used to determine which marker coordinates should be used.

    Returns
    -------
    tuple[torch.Tensor, ...]
        Coordinates for the markers from the considered target.
    """
    # Select markers based on the target identifier.
    # These markers are predefined in `paint.util.paint_mappings`.
    if target in {1, 7, mappings.STJ_LOWER}:
        markers = mappings.STJ_LOWER_ENU
    elif target in {4, 5, 6, mappings.STJ_UPPER}:
        markers = mappings.STJ_UPPER_ENU
    elif target in {3, mappings.MFT}:
        markers = mappings.MFT_ENU
    else:
        # Raise an error if the target is not recognized.
        raise ValueError(f"Unsupported target value: {target}")

    # Convert marker coordinates to PyTorch tensors for further computation.
    return tuple(torch.tensor(marker) for marker in markers)


def convert_xy_to_enu(
    aim_point_image: tuple[float, float], target: Union[str, int]
) -> torch.Tensor:
    """
    Convert (x, y) coordinates to an aimpoint in the target image based on marker positions.

    Parameters
    ----------
    aim_point_image : tuple[float, float]
        Relative aim point coordinates (x, y).
    target : Union[str, int]
        The target object containing marker information.

    Returns
    -------
    torch.Tensor
        Aimpoint coordinates in the target image.
    """
    # Retrieve the marker positions for the given target.
    (
        marker_left_top,
        marker_left_bottom,
        marker_right_top,
        marker_right_bottom,
    ) = get_marker_coordinates(target)

    # Compute the horizontal directional vector (dx).
    # This vector spans the distance between the left and right markers.
    dx = 0.5 * (marker_right_top - marker_left_top) + 0.5 * (
        marker_right_bottom - marker_left_bottom
    )

    # Compute the vertical directional vector (dy).
    # This vector spans the distance between the top and bottom markers.
    dy = 0.5 * (marker_left_bottom - marker_left_top) + 0.5 * (
        marker_right_bottom - marker_right_top
    )

    # Calculate the aimpoint in global coordinates.
    # The aimpoint is a combination of the top-left marker position and a weighted
    # sum of dx and dy based on the relative aim_point_image coordinates.
    return marker_left_top + aim_point_image[0] * dx + aim_point_image[1] * dy


def compute_center_of_intensity(
    flux: torch.Tensor, threshold: float = 0.0
) -> tuple[float, float]:
    """
    Calculate the center of intensity (x, y) coordinates in a 2D flux image.

    Parameters
    ----------
    flux : torch.Tensor
        A 2D tensor representing the flux/intensity image.
    threshold : float, optional
        Minimum intensity value for pixels to be included in the calculation (Default: `0.0`).

    Returns
    -------
    float
        x coordinate of the center of intensity.
    float
        y coordinate of the center of intensity.
    """
    height, width = flux.shape

    # Threshold the flux values. Any values below the threshold are set to zero.
    flux_thresholded = torch.where(flux >= threshold, flux, torch.zeros_like(flux))
    total_intensity = flux_thresholded.sum()

    # If all values are below the threshold, default to the center of the image.
    if total_intensity == 0:
        return 0.5, 0.5

    # Generate normalized x and y coordinates adjusted for pixel centers.
    # The "+ 0.5" adjustment ensures coordinates are centered within each pixel.
    x_coords = (torch.arange(width, dtype=torch.float32) + 0.5) / width
    y_coords = (torch.arange(height, dtype=torch.float32) + 0.5) / height

    # Compute the center of intensity using weighted sums of the coordinates.
    x_center = (flux_thresholded.sum(dim=0) * x_coords).sum() / total_intensity
    y_center = (flux_thresholded.sum(dim=1) * y_coords).sum() / total_intensity

    return x_center.item(), y_center.item()


def detect_focal_spot(
    image: torch.Tensor,
    target: Union[str, int],
    utis_model: torch.nn.Module,
) -> FocalSpot:
    """
    Detect a focal spot within an image using UTIS focal spot segmentation.

    Parameters
    ----------
    image : torch.Tensor
        Cropped image containing the focal spot to be detected, with the shape (height, width).
    target : Union[str, int]
        Target center and dimensions used for aimpoint calculation.
    utis_model : torch.nn.Module
        UTIS model checkpoint used to compute the flux.

    Returns
    -------
    FocalSpot
        Detected focal spot with flux, image coordinates, and global aimpoint.
    """
    if image.dim() != 2:
        raise ValueError(f"Expected a 2D tensor, got {image.dim()} dimensions.")

    # Pass the input image through the UTIS model to generate a flux image.
    # The input image is unsqueezed to add batch and channel dimensions.
    # The output flux is extracted from the first channel of the result.
    flux = utis_model(image.unsqueeze(0).unsqueeze(0))[0, 0].detach()

    # Compute the center of intensity in image coordinates.
    aim_point_image = compute_center_of_intensity(flux)

    # Convert the center of intensity to global ENU coordinates using marker data.
    aimpoint_global = convert_xy_to_enu(aim_point_image, target)

    # Return a FocalSpot object containing the flux, image coordinates, and global aimpoint.
    return FocalSpot.from_flux(
        flux=flux,
        aim_point_image=aim_point_image,
        aim_point=aimpoint_global,
    )
