import torch
from .util import kmeans, compute_center_of_intensity, compute_affine_transform
from .dataclasses import FocalSpot, Target
from typing import Optional

def detect_focal_spot(
    image: torch.Tensor, num_k_means: int, applied_k_means: int, target: Target,
) -> FocalSpot:
    """
    @brief Detects a focal spot within an image by applying k-means clustering to the image.

    @param image The image where the focal spot is to be detected in. Must have shape (height x width)
    @param num_k_means The number of k-means clusters to be generated.
    @param applied_k_means: The upper n k-means clusters to be assumed to belong to the focal spot.
    @param target: Target data to be applied to determine the focal spot position

    @return The detected focal spot.
    """
    masked_image = torch.mul(image, target.mask) if isinstance(target.mask, torch.Tensor) else image
    clusters = kmeans(image=masked_image, num_clusters=num_k_means)
    aim_point = compute_center_of_intensity(clusters=clusters)
    
    v = (target.marker_2.enu_position - target.marker_1.enu_position).to(aim_point.dtype)
    u = (target.marker_3.enu_position - target.marker_1.enu_position).to(aim_point.dtype)
    v_prime = (target.marker_2.image_position - target.marker_1.image_position).to(aim_point.dtype)
    u_prime = (target.marker_3.image_position - target.marker_1.image_position).to(aim_point.dtype)

    A = torch.stack([u_prime, v_prime])
    alpha = torch.inverse(A) @ aim_point
    aim_point_global = alpha[0] * u + alpha[1] * v + target.marker_1.enu_position

    return FocalSpot(clusters=clusters, aim_point_image=aim_point, aim_point=aim_point_global)
