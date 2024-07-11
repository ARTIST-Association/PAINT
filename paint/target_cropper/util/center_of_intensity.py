import torch
from ..dataclasses import KMeansCluster


def compute_center_of_intensity(clusters: KMeansCluster):
    """
    @brief computes the center of intensity position from a given list of intensity clusters

    @return center of intensity position as width and height coordinate
    """
    total_mass = clusters.centers.sum(dim=0)
    center_of_intensity = (
        clusters.center_positions * clusters.centers.unsqueeze(dim=-1)
    ).sum(dim=0) / total_mass

    return center_of_intensity
