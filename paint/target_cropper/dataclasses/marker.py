from dataclasses import dataclass

import torch

from paint.target_cropper.dataclasses.search_region import SearchRegion


@dataclass
class Marker:
    """
    A marker used for target image referencing.

    Attributes
    ----------
    image_position : torch.Tensor
        Marker supposed position in (height, width) in the image it is referencing.
    template_offset : torch.Tensor
        Offset between the marker position and the upper left corner of the marker's template image in (height, width).
    enu_position : torch.Tensor
        Marker position in enu field coordinates [E,N,U].
    template_image : torch.Tensor
        Marker template image to be detected.
    search_region : torch.Tensor, optional
        Region within the image where the marker template is expected to be found.
    """

    image_position: torch.Tensor
    template_offset: torch.Tensor
    enu_position: torch.Tensor
    template_image: torch.Tensor
    search_region: SearchRegion | None = None
