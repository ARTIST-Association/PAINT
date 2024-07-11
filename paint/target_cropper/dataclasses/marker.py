from dataclasses import dataclass
import torch
from .search_region import SearchRegion


@dataclass
class Marker:
    """
    @brief A marker to be used for target image referencing.

    @param image_position The marker's supposed position in the image it is referencing.
    @param template_offset The offset between the marker position and the upper left corner of the marker's template image.
    @param enu_position The marker's position in enu field coordinates.
    @param template_image The marker's template image to be detected.
    @param search_region The region within the image where the marker template is expected to be found.
    """
    image_position: torch.Tensor
    template_offset: torch.Tensor
    enu_position: torch.Tensor
    template_image: torch.Tensor
    search_region: SearchRegion
