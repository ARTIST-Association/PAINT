import cv2
import torch


def compute_transform(source: torch.Tensor, destination: torch.Tensor) -> torch.Tensor:
    """
    Compute a perspective transformation (matrix) from given source and destination control points using OpenCV.

    Parameters
    ----------
    source : torch.Tensor
        Source control points to be mapped onto the destination points.
    destination : torch.Tensor
        Destination control points, with the same shape as the source.

    Returns
    -------
    torch.Tensor
        Perspective transformation with the shape (2, 3).
    """
    if source.shape != destination.shape:
        raise ValueError(
            "The source and destination control-points must have the same shape!"
        )
    return torch.tensor(
        cv2.getPerspectiveTransform(
            source[:, [1, 0]].detach().numpy().astype("float32"),
            destination[:, [1, 0]].detach().numpy().astype("float32"),
        )
    )


def apply_transform(
    image: torch.Tensor, transform: torch.Tensor, output_shape: torch.Size
) -> torch.Tensor:
    """
    Apply a perspective transformation to an image using OpenCV.

    Parameters
    ----------
    image : torch.Tensor
        Image to be transformed. Must have shape (height, width).
    transform : torch.Tensor
        Transformation to be applied. Must have shape (2, 3).
    output_shape : torch.Tensor
        The desired output shape of the transformed image (height, width).

    Returns
    -------
    torch.Tensor
        Transformed image with the desired output shape.
    """
    if transform.shape != torch.Size([2, 3]):
        raise ValueError("The transform must have shape (2,3).")
    warped_image = cv2.warpPerspective(
        image.detach().numpy().astype("float32"),
        transform.detach().numpy().astype("float32"),
        output_shape,
    )
    return torch.tensor(warped_image, dtype=image.dtype)
