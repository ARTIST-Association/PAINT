import torch
from .dataclasses import Target, Marker
from .util import find_template_position, compute_transform, apply_transform, to_image
import matplotlib.pyplot as plt

def find_marker_position(image: torch.Tensor, marker: Marker) -> torch.Tensor:
    """
    @brief Finds marker positions within an image.

    @param image The image to find the marker in.
    @param marker The marker to be found.

    @return marker position as (height, width).
    """
    template_position = find_template_position(
        image=image, template=marker.template_image
    )
    marker_position = template_position
    return marker_position


def detect_target(image: torch.Tensor, target: Target) -> torch.Tensor:
    """
    @brief References a target image to the desired cropped image.

    @param image The image to be referenced. Must have shape (height x width).
    @param target Information about the target's marker's (control points) and the desired output image shape.

    @return The referenced image of shape target.output_shape.
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
    transform = compute_transform(src=src, dst=dst)
    warped_image = apply_transform(image=image, transform=transform, output_shape=target.output_shape)
    return warped_image
