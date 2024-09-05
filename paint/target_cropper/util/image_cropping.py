import torch


def crop_image(
    image: torch.Tensor, upper_left: torch.Tensor, lower_right: torch.Tensor
) -> torch.Tensor:
    """
    Crop an image to the desired region defined by an upper left and lower right point.

    Parameters
    ----------
    image : torch.Tensor
        Input image to be cropped.
    upper_left : torch.Tensor
        Regions upper left point.
    lower_right : torch.Tensor
        Regions lower right point.

    Returns
    -------
    torch.Tensor
        The cropped image.
    """
    x1, y1 = upper_left
    x2, y2 = lower_right

    # Perform cropping using tensor slicing
    cropped_image = image[..., y1:y2, x1:x2]
    return cropped_image


def get_parent_coordinate(
    cropped_coordinate: torch.Tensor, upper_left: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Compute the original image's coordinates from a cropped image's coordinates.

    Parameters
    ----------
    cropped_coordinate : torch.Tensor
        Position within the cropped image (height, width).
    upper_left : torch.Tensor
        Cropped image's upper left position within the parent image.

    Returns
    -------
    torch.Tensor
        x coordinate of the original image.
    torch.Tensor
        y coordinates of the original image.
    """
    x_crop, y_crop = cropped_coordinate
    x1_crop, y1_crop = upper_left

    x_parent = x_crop + x1_crop
    y_parent = y_crop + y1_crop

    return x_parent, y_parent
