from dataclasses import dataclass

import torch

from paint.target_cropper.dataclasses.marker import Marker


@dataclass
class Target:
    """
    Data class for storing target specifications.

    Attributes
    ----------
    marker_1 : Marker
        Target's first marker.
    marker_2 : Marker
        Target's second marker.
    marker_3 : Marker
        Target's third marker.
    marker_4 : Marker
        Target's fourth marker.
    output_shape : torch.Size
        Desired image shape after target cropping. Must be in accordance with the marker image positions.
    mask : torch.Tensor, optional
        Indicate the focal spot search region. Must have the same shape as the image and values between [0,1] whereby 0
        masks the pixels as negligible.
    """

    marker_1: Marker
    marker_2: Marker
    marker_3: Marker
    marker_4: Marker
    output_shape: torch.Size
    # TODO: Switch mask to tensor of Bools to make use of native masking capabilities in torch?
    mask: torch.Tensor | None = None

    @property
    def markers(self) -> list[Marker]:
        """
        Generate the target's markers as a list.

        Returns
        -------
        list[Marker]
            All markers from the target.
        """
        return [self.marker_1, self.marker_2, self.marker_3, self.marker_4]
