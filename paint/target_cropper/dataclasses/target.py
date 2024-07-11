from dataclasses import dataclass
from .marker import Marker
import torch


@dataclass
class Target:
    marker_1: Marker
    marker_2: Marker
    marker_3: Marker
    marker_4: Marker
    output_shape: torch.Size
    mask: torch.Tensor
