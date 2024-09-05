import torch

from paint.target_cropper.dataclasses import KMeansCluster


def compute_center_of_intensity(clusters: KMeansCluster) -> torch.Tensor:
    """
    Compute the center of intensity position from a given list of intensity clusters.

    Parameters
    ----------
    clusters : KMeansCluster
        The list of intensity clusters.

    Returns
    -------
    torch.Tensor
        Center of intensity position as height and width coordinate.
    """
    total_mass = clusters.centers.sum(dim=0)
    # Return center of intensity.
    return (clusters.center_positions * clusters.centers.unsqueeze(dim=-1)).sum(
        dim=0
    ) / total_mass
