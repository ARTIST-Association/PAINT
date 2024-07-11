from dataclasses import dataclass
from .k_means_cluster import KMeansCluster
import torch


@dataclass
class FocalSpot:
    """
    @brief data class for storing focal spot information.

    @param clusters Intensity clusters of the detected focal spot.
    @param aim_point The detected center of intensity.
    """
    clusters: KMeansCluster
    aim_point: torch.Tensor
