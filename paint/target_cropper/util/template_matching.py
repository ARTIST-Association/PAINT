import torch
import torch.nn.functional as F
from ..dataclasses import SearchRegion
from .image_cropping import crop_image, get_parent_coordinate
from typing import Optional

# TODO this function does not yet work. MUST BE FIXED!
def find_template_position(image: torch.Tensor, template: torch.Tensor, search_region: Optional[SearchRegion] = None) -> torch.Tensor:
    """
    @brief Finds a template within an image by computing the image likeliness matrix via convolution.

    @param image The image where the template is to be found in. Must have shape (height x width).
    @param template The template to be found. Must have shape (height x width).
    @param search_region The region within the given image where the template is expected to be found.

    @return The found upper left corner of the template image (height, width).
    """

    # Perform template matching using convolution
    cropped_image = crop_image(image=image, upper_left=search_region.position, lower_right=search_region.position+search_region.dimension) if isinstance(search_region, SearchRegion) else image
    result = F.conv2d(
        input=cropped_image.unsqueeze(dim=0).unsqueeze(dim=0), # minibatch,in_channels,iH,iW
        weight=template.unsqueeze(dim=0).unsqueeze(dim=0), # out_channels, in_channesl / groups, kH, kW
        padding="valid",
        bias=None
    ).squeeze()

    # alternative:
    # conv_layer = torch.nn.Conv2d(in_channels=1, out_channels=1, kernel_size=template.shape, bias=False)
    # conv_layer.weight.data = template.unsqueeze(dim=0).unsqueeze(dim=0)
    # result = conv_layer(cropped_image.unsqueeze(dim=0).unsqueeze(dim=0)).squeeze()

    # Find the location of the highest value in the cropped image
    height, width = result.shape # use result shape, because result is cropped from original image due to padding, but has same starting point
    max_val, max_idx = torch.max(result.view(-1), 0)
    max_idx = max_idx.item()
    max_pos = (max_idx // width, max_idx % width) # get height = round(max_idx / padded_width), width = rest(max_idx / padded_width)
    return get_parent_coordinate(cropped_coordinate=torch.tensor(max_pos), upper_left=search_region.position)
