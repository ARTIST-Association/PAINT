from dataclasses import dataclass
from .marker import Marker
import torch
import typing

@dataclass
class Target:
    """
    @brief data class for storing target specifications

    @param marker_1 the target's first marker
    @param marker_2 the target's second marker
    @param marker_3 the target's third marker
    @param marker_4 the target's fourth marker
    @param output_shape the desired image shape after target cropping. Must be in accordance with the marker image positions.
    @param mask Mask to indicate the focal spot search region. Must have same shape as image and values between [0,1] whereby 0 masks the pixels as negligible.
    """
    marker_1: Marker
    marker_2: Marker
    marker_3: Marker
    marker_4: Marker
    output_shape: torch.Size
    mask: typing.Optional[torch.Tensor]

    @property
    def markers(self) -> typing.List[Marker]:
        """
        @brief returns the target's markers as a list

        @return list of markers
        """
        return [self.marker_1, self.marker_2, self.marker_3, self.marker_4]