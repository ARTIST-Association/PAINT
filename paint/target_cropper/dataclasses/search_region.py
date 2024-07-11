from dataclasses import dataclass
import torch

@dataclass
class SearchRegion:
    """
    @brief A search region for more efficient template matching.

    @param position The search region's position (upper left corner) as (height, width).
    @param dimension The search regions' lower right corner relative to the regions' position (heigh, width).
    """
    position: torch.Tensor
    dimension: torch.Tensor