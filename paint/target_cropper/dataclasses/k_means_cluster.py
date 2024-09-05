from dataclasses import dataclass

import torch


@dataclass
class KMeansCluster:
    """
    A K-means cluster describing regions of an image.

    Attributes
    ----------
    centers : torch.Tensor
        Clusters' center values.
    labels: torch.Tensor
        Image pixels labeled to their according cluster by index.
    center_positions : torch.Tensor
        The k-means regions' center position within the image.
    """

    centers: torch.Tensor
    labels: torch.Tensor
    center_positions: torch.Tensor
