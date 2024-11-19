from typing import Union

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

    def __init__(
        self,
        flux: torch.Tensor,
        aim_point_image: tuple[float, float],
        aim_point: torch.Tensor,
    ) -> None:
        """
        Initialize the focal spot data class.

        Parameters
        ----------
        flux : torch.Tensor
            Intensity image of the detected focal spot.
        aim_point_image : tuple[float, float]
            Detected center of intensity in image coordinates (height, width).
        aim_point : torch.Tensor
            Detected center of intensity in global coordinates (E, N, U).
        """
        self.flux = flux
        self.aim_point_image = aim_point_image
        self.aim_point = aim_point


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
    if flux.dim() != 2:
        raise ValueError(f"Expected a 2D tensor, got {flux.dim()} dimensions.")

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
    flux = utis_model(image.unsqueeze(0).unsqueeze(0))[0, 0]

    # Compute the center of intensity in image coordinates.
    aim_point_image = compute_center_of_intensity(flux)

    # Convert the center of intensity to global ENU coordinates using marker data.
    aimpoint_global = convert_xy_to_enu(aim_point_image, target)

    # Return a FocalSpot object containing the flux, image coordinates, and global aimpoint.
    return FocalSpot(
        flux=flux,
        aim_point_image=aim_point_image,
        aim_point=aimpoint_global,
    )
