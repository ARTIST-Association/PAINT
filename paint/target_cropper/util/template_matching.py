import cv2
import torch


def find_template_position(
    image: torch.Tensor,
    template: torch.Tensor,
) -> torch.Tensor:
    """
    Find a template within an image by computing the image likeliness matrix via convolution using OpenCV.

    Parameters
    ----------
    image : torch.Tensor
        Image where the template is to be found in, with the shape (height, width).
    template : torch.Tensor
        Template to be found with the shape (height, width).

    Returns
    -------
    torch.Tensor
        Identified template position.
    """
    if len(image.shape) != 2:
        raise ValueError("Image must have the shape (height, width).")
    if len(template.shape) != 2:
        raise ValueError("Template must have the shape (height, width).")
    template = template[:31, :31]
    method = cv2.TM_SQDIFF
    res = cv2.matchTemplate(
        image=image.detach().numpy().astype("float32"),
        templ=template.detach().numpy().astype("float32"),
        method=method,
    )
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    return torch.tensor([top_left[1], top_left[0]], dtype=image.dtype)
