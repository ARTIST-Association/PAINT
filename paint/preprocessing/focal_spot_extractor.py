from typing import Union
import torch
import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT


class FocalSpot:
    """
    Data class for storing focal spot information.

    Attributes
    ----------
    flux : torch.Tensor
        Intensity image of the detected focal spot.
    aim_point_image : torch.Tensor
        The detected center of intensity in image coordinates (height, width).
    aim_point : torch.Tensor
        The detected center of intensity in global coordinates (E, N, U).
    """

    def __init__(
        self, flux: torch.Tensor, aim_point_image: torch.Tensor, aim_point: torch.Tensor
    ):
        self.flux = flux
        self.aim_point_image = aim_point_image
        self.aim_point = aim_point


def get_marker_coordinates(target: Union[str, int]) -> tuple:
    """
    Get the specific marker coordinates based on the target.

    Parameters
    ----------
    target : Union[str, int]
        Target ID used to determine which marker coordinates should be used.

    Returns
    -------
    tuple
        A tuple containing the marker coordinates as torch.Tensors:
        (marker_left_top, marker_left_bottom, marker_right_top, marker_right_bottom)
    """
    if target in {1, 7, mappings.STJ_LOWER}:
        markers = mappings.STJ_LOWER_ENU
    elif target in {4, 5, 6, mappings.STJ_UPPER}:
        markers = mappings.STJ_UPPER_ENU
    elif target in {3, mappings.MFT}:
        markers = mappings.MFT_ENU
    else:
        raise ValueError(f"Unsupported target value: {target}")

    return tuple(torch.tensor(marker) for marker in markers)


def convert_xy_to_ENU(aim_point_image: tuple, target: Union[str, int]) -> torch.Tensor:
    """
    Convert x, y coordinates to an aimpoint in the target image based on marker positions.

    Parameters
    ----------
    aim_point_image : tuple
        Relative aim point coordinates (x, y).
    target : Union[str, int]
        The target object containing marker information.

    Returns
    -------
    torch.Tensor
        Aimpoint coordinates in the target image.
    """
    marker_left_top, marker_left_bottom, marker_right_top, marker_right_bottom = get_marker_coordinates(
        target
    )

    dx = 0.5 * (marker_right_top - marker_left_top) + 0.5 * (
        marker_right_bottom - marker_left_bottom
    )
    dy = 0.5 * (marker_left_bottom - marker_left_top) + 0.5 * (
        marker_right_bottom - marker_right_top
    )

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
        Minimum intensity value for pixels to be included in the calculation, by default 0.0.

    Returns
    -------
    tuple[float, float]
        (x, y) coordinates of the center of intensity.
    """
    if flux.dim() != 2:
        raise ValueError(f"Expected a 2D tensor, got {flux.dim()} dimensions.")

    height, width = flux.shape

    flux_thresholded = torch.where(flux >= threshold, flux, torch.zeros_like(flux))
    total_intensity = flux_thresholded.sum()
    if total_intensity == 0:
        return width / 2, height / 2

    y_coords = torch.arange(height, dtype=torch.float32) / height
    x_coords = torch.arange(width, dtype=torch.float32) / width

    x_center = (flux_thresholded.sum(dim=0) * x_coords).sum() / total_intensity
    y_center = (flux_thresholded.sum(dim=1) * y_coords).sum() / total_intensity

    return x_center.item(), y_center.item()


def detect_focal_spot(
    image: torch.Tensor, target: Union[str, int], utis: torch.nn.Module = None
) -> FocalSpot:
    """
    Detect a focal spot within an image using UTIS focal spot segmentation.

    Parameters
    ----------
    image : torch.Tensor
        Cropped image containing the focal spot to be detected, with the shape (height, width).
    target : Union[str, int]
        Target center and dimensions used for aimpoint calculation.
    utis : torch.nn.Module, optional
        UTIS model checkpoint used to compute the flux, by default None.

    Returns
    -------
    FocalSpot
        Detected focal spot with flux, image coordinates, and global aimpoint.
    """
    if image.dim() != 2:
        raise ValueError(f"Expected a 2D tensor, got {image.dim()} dimensions.")

    if utis is None:
        raise ValueError("UTIS model must be provided.")

    flux = utis(image.unsqueeze(0).unsqueeze(0))[0, 0]
    aim_point_image = compute_center_of_intensity(flux)
    aimpoint_global = convert_xy_to_ENU(aim_point_image, target)

    return FocalSpot(
        flux=flux,
        aim_point_image=aim_point_image,
        aim_point=aimpoint_global,
    )
