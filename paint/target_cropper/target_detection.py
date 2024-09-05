import torch
from matplotlib import pyplot as plt

from paint.target_cropper.dataclasses import Marker, Target
from paint.target_cropper.util import (
    apply_transform,
    compute_transform,
    find_template_position,
)


def find_marker_position(image: torch.Tensor, marker: Marker) -> torch.Tensor:
    """
    Find marker positions within an image.

    Parameters
    ----------
    image : torch.Tensor
        Image in which the marker should be found.
    marker : Marker
        Marker to be found.

    Returns
    -------
    torch.Tensor
        Marker position as (height, width).
    """
    template_position = find_template_position(
        image=image, template=marker.template_image
    )
    marker_position = template_position + torch.stack(
        [
            torch.round(marker.template_offset[0] * marker.template_image.shape[0]),
            torch.round(marker.template_offset[1] * marker.template_image.shape[1]),
        ]
    )
    return marker_position


def detect_target(image: torch.Tensor, target: Target) -> torch.Tensor:
    """
    Detect a target image.

    Parameters
    ----------
    image : torch.Tensor
        Image to be referenced, with the shape (height, width).
    target : Target
        Information about the target's marker's (control points) and the desired output image shape.

    Returns
    -------
    torch.Tensor
        Detected target image.
    """
    marker_1_position = find_marker_position(image=image, marker=target.marker_1)
    marker_2_position = find_marker_position(image=image, marker=target.marker_2)
    marker_3_position = find_marker_position(image=image, marker=target.marker_3)
    marker_4_position = find_marker_position(image=image, marker=target.marker_4)

    src = torch.stack(
        [marker_1_position, marker_2_position, marker_3_position, marker_4_position]
    )
    dst = torch.stack(
        [
            target.marker_1.image_position,
            target.marker_2.image_position,
            target.marker_3.image_position,
            target.marker_4.image_position,
        ]
    )
    plt.imshow(src.detach().cpu().numpy(), cmap="gray")
    plt.show()
    plt.imshow(dst.detach().cpu().numpy(), cmap="gray")
    plt.show()
    transform = compute_transform(source=src, destination=dst)
    return apply_transform(
        image=image, transform=transform, output_shape=target.output_shape
    )
