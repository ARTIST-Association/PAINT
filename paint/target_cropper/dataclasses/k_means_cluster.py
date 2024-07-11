from dataclasses import dataclass
import torch


@dataclass
class KMeansCluster:
    """
    @brief A cluster of k-means regions of an image.

    @param centers The clusters' center values.
    @param labels Image pixels labeled to their according cluster by index.
    @param center_positions The k-means regions' center position within the image.
    """
    centers: torch.Tensor
    labels: torch.Tensor
    center_positions: torch.Tensor
