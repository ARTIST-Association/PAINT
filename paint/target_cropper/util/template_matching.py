import torch
import torch.nn.functional as F
from ..dataclasses import SearchRegion
from .image_cropping import crop_image, get_parent_coordinate
from typing import Optional
import cv2

def find_template_position_cv(image: torch.Tensor, template: torch.Tensor, search_region: Optional[SearchRegion] = None):
    """
    @brief Finds a template within an image by computing the image likeliness matrix via convolution using OpenCV.

    @param image The image where the template is to be found in. Must have shape (height x width).
    @param template The template to be found. Must have shape (height x width).
    @param search_region The region within the given image where the template is expected to be found.

    @return T
    """

    template = template[:31,:31]
    method = cv2.TM_SQDIFF
    res = cv2.matchTemplate(image=image.detach().numpy().astype("float32"), templ=template.detach().numpy().astype("float32"), method=method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    return torch.tensor([top_left[1], top_left[0]], dtype=image.dtype)

# TODO this function does not yet work. MUST BE FIXED!
def find_template_position(image: torch.Tensor, template: torch.Tensor, search_region: Optional[SearchRegion] = None) -> torch.Tensor:
    """
    @brief Finds a template within an image by computing the image likeliness matrix via convolution. Not fully tested!

    @param image The image where the template is to be found in. Must have shape (height x width).
    @param template The template to be found. Must have shape (height x width).
    @param search_region The region within the given image where the template is expected to be found.

    @return The found upper left corner of the template image (height, width).
    """

    template = template[:31,:31]

    # Perform template matching using convolution
    cropped_image = (crop_image(image=image, upper_left=search_region.position, lower_right=search_region.position+search_region.dimension) if isinstance(search_region, SearchRegion) else image).unsqueeze(dim=0).unsqueeze(dim=0)
    
    # normalize the template
    normalized_template = (template - template.mean()) / (template.std() if template.std().item() != 0 else 1)


    # Step 2: Compute the local mean and std for each sliding window in the image
    # Create a kernel of ones with the same size as the template
    Ht, Wt = template.shape
    kernel = torch.ones(1, 1, Ht, Wt)

    # Compute local mean
    mean = F.conv2d(cropped_image, kernel, padding=(Ht//2, Wt//2)) / (Ht * Wt)

    # Compute local squared mean
    squared_mean = F.conv2d(cropped_image**2, kernel, padding=(Ht//2, Wt//2)) / (Ht * Wt)

    # Compute local std
    std = torch.sqrt(squared_mean - mean**2 + 1e-5)  # Add small value to avoid division by zero

    # Normalize the image locally
    normalized_image = (cropped_image - mean) / std
    
    # perform cross image correlation
    result = F.conv2d(
        input=normalized_image, # minibatch,in_channels,iH,iW
        weight=normalized_template.unsqueeze(dim=0).unsqueeze(dim=0), # out_channels, in_channesl / groups, kH, kW
        padding=(Ht//2, Wt//2),
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
    max_pos = (max_idx % width, max_idx % width) # get height = round(max_idx / padded_width), width = rest(max_idx / padded_width)
    max_pos_2 = get_parent_coordinate(cropped_coordinate=torch.tensor(max_pos), upper_left=search_region.position)   
    return max_pos_2
