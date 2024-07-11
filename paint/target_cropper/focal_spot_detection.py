import torch
from .util import kmeans, compute_center_of_intensity
from .dataclasses import FocalSpot
from typing import Optional

def detect_focal_spot(
    image: torch.Tensor, num_k_means: int, applied_k_means: int, mask: Optional[torch.Tensor] = None,
) -> FocalSpot:
    """
    @brief Detects a focal spot within an image by applying k-means clustering to the image.

    @param image The image where the focal spot is to be detected in. Must have shape (height x width)
    @param num_k_means The number of k-means clusters to be generated.
    @param applied_k_means: The upper n k-means clusters to be assumed to belong to the focal spot.
    @param mask: Mask to indicate the focal spot search region. Must have same shape as image and values between [0,1] whereby 0 masks the pixels as negligible.

    @return The detected focal spot.
    """
    masked_image = torch.mul(image, mask) if isinstance(mask, torch.Tensor) else image
    clusters = kmeans(image=masked_image, num_clusters=num_k_means)
    aim_point = compute_center_of_intensity(clusters=clusters)
    return FocalSpot(clusters=clusters, aim_point=aim_point)
