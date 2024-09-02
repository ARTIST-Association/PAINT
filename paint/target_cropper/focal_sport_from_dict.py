import typing
import os
import torch
import json
from . import util
from . import dataclasses
from .focal_spot_detection import detect_focal_spot
from .target_detection import detect_target

def focal_spot_from_dict(target_data : dict, image_path : str, mask_path: typing.Optional[str] = None, num_k_means=16, applied_k_means=5):
    # create target
    image = util.load_image(image_path=image_path)
    mask = util.load_image(image_path=mask_path) if isinstance(mask_path, str) else None
    target = dataclasses.Target(
        marker_1=dataclasses.Marker(
            image_position=torch.tensor([0, 0]),
            template_offset=torch.tensor([0, 0]),
            enu_position=torch.tensor(target_data["solar_tower_juelich_lower"]["upper_left"]),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["upper_left_marker"]
            ),
        ),
        marker_2=dataclasses.Marker(
            image_position=torch.tensor([0, 400]),
            template_offset=torch.tensor([0, 1.0]),
            enu_position=torch.tensor(target_data["solar_tower_juelich_lower"]["upper_right"]),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["upper_right_marker"]
            ),
        ),
        marker_3=dataclasses.Marker(
            image_position=torch.tensor([400, 0]),
            template_offset=torch.tensor([1.0, 0]),
            enu_position=torch.tensor(target_data["solar_tower_juelich_lower"]["lower_left"]),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["lower_left_marker"]
            ),
        ),
        marker_4=dataclasses.Marker(
            image_position=torch.tensor([400, 400]),
            template_offset=torch.tensor([1.0, 1.00]),
            enu_position=torch.tensor(target_data["solar_tower_juelich_lower"]["lower_right"]),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["lower_right_marker"]
            ),
        ),
        output_shape=torch.Size([400,400]),
        mask = mask
    )

    # warp image
    warped_image = detect_target(image=image, target=target)
    focal_spot = detect_focal_spot(
        image=warped_image, num_k_means=num_k_means, applied_k_means=applied_k_means, target=target
    )
    return focal_spot

if __name__ == "__main__":
    image_path = ""
    marker_path = ""
    target_data_path = ""
    mask_path = None

    with open(target_data_path, "r") as file:
        target_data = json.load(file)

    focal_spot_from_dict(target_data=target_data, image_path=image_path, mask_path=mask_path, num_k_means=16, applied_k_means=5)