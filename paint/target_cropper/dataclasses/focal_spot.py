from dataclasses import dataclass

import torch

from paint.target_cropper.dataclasses.k_means_cluster import KMeansCluster


@dataclass
class FocalSpot:
    """
    Data class for storing focal spot information.

    Attributes
    ----------
    clusters : KmeansCluster
        Intensity clusters of the detected focal spot.
    aim_point_image : torch.Tensor
        The detected center of intensity in image coordinates (height, width).
    aim_point : torch.Tensor
        The detected center of intensity in global coordinates (E, N, U).
    """

    clusters: KMeansCluster
    aim_point_image: torch.Tensor
    aim_point: torch.Tensor
