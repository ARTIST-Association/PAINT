import torch

def crop_image(image: torch.Tensor, upper_left: torch.Tensor, lower_right: torch.Tensor) -> torch.Tensor:
    """
    @brief Crops an image to the desired region defined by an upper left and lower right point.
    
    @param image The input image to be cropped.
    @param upper_left The regions upper left point.
    @param lower_right The regions lower right point.

    @return The cropped image.
    """
    x1, y1 = upper_left
    x2, y2 = lower_right
    
    # Perform cropping using tensor slicing
    cropped_image = image[..., y1:y2, x1:x2]
    return cropped_image

def get_parent_coordinate(cropped_coordinate: torch.Tensor, upper_left: torch.Tensor):
    """
    @brief Computes the original image's coordinate from a cropped image's coordinate.

    @param cropped_coordiante Position within the cropped image (height, width).
    @param upper_left Cropped image's upper left position within the parent image.

    @return Position within the parent image.
    """
    x_crop, y_crop = cropped_coordinate
    x1_crop, y1_crop = upper_left
    
    x_parent = x_crop + x1_crop
    y_parent = y_crop + y1_crop
    
    return (x_parent, y_parent)