from dataclasses import dataclass

import torch


@dataclass
class SearchRegion:
    """
    A search region for more efficient template matching.

    Attributes
    ----------
    position : torch.Tensor
        Search region position (upper left corner) as width/height.
    dimension : torch.Tensor
        Search region's lower right corner relative to the region's position in (height, width).
    """

    position: torch.Tensor
    dimension: torch.Tensor
