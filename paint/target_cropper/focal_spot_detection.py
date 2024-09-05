import torch

from paint.target_cropper.dataclasses import FocalSpot, Target
from paint.target_cropper.util import compute_center_of_intensity, kmeans


def detect_focal_spot(
    image: torch.Tensor,
    num_k_means: int,
    target: Target,
) -> FocalSpot:
    """
    Detect a focal spot within an image by applying K-means clustering to the image.

    Parameters
    ----------
    image : torch.Tensor
        Image containing the focal spot to be detected with the shape (height, width)
    num_k_means : int
        Number of k-means clusters to be generated.
    target : Target
        Markers used to determine the focal spot position.

    Returns
    -------
    FocalSpot
        Detected focal spot.
    """
    if image.shape != torch.Size([2]):
        raise ValueError("The image must have the shape (height, width).")
    masked_image = (
        torch.mul(image, target.mask)
        if isinstance(target.mask, torch.Tensor)
        else image
    )
    clusters = kmeans(image=masked_image, num_clusters=num_k_means)
    aim_point = compute_center_of_intensity(clusters=clusters)

    v = (target.marker_2.enu_position - target.marker_1.enu_position).to(
        aim_point.dtype
    )
    u = (target.marker_3.enu_position - target.marker_1.enu_position).to(
        aim_point.dtype
    )
    v_prime = (target.marker_2.image_position - target.marker_1.image_position).to(
        aim_point.dtype
    )
    u_prime = (target.marker_3.image_position - target.marker_1.image_position).to(
        aim_point.dtype
    )

    a = torch.stack([u_prime, v_prime])
    alpha = torch.inverse(a) @ aim_point
    aim_point_global = alpha[0] * u + alpha[1] * v + target.marker_1.enu_position

    return FocalSpot(
        clusters=clusters, aim_point_image=aim_point, aim_point=aim_point_global
    )
