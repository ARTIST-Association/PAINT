import pathlib

import torch

from paint.target_cropper import dataclasses, util
from paint.target_cropper.dataclasses import FocalSpot
from paint.target_cropper.focal_spot_detection import detect_focal_spot
from paint.target_cropper.target_detection import detect_target


def focal_spot_from_dict(
    target_data: dict,
    image_path: pathlib.Path,
    mask_path: pathlib.Path | None = None,
    num_k_means: int = 16,
) -> FocalSpot:
    """
    Determine focal spot from a dictionary.

    Parameters
    ----------
    target_data : dict
        A dictionary containing information about the target.
    image_path : pathlib.Path
        Path to the image to load.
    mask_path : pathlib.Path, optional
        Path to the mask to load. Default is ``None``.
    num_k_means : int
        The number of K-means clusters to be generated.

    Returns
    -------
    FocalSpot
        The identified focal spot.
    """
    # create target
    image = util.load_image(image_path=image_path)
    mask = (
        util.load_image(image_path=mask_path)
        if isinstance(mask_path, pathlib.Path)
        else None
    )
    target = dataclasses.Target(
        marker_1=dataclasses.Marker(
            image_position=torch.tensor([0, 0]),
            template_offset=torch.tensor([0, 0]),
            enu_position=torch.tensor(
                target_data["solar_tower_juelich_lower"]["upper_left"]
            ),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["upper_left_marker"]
            ),
        ),
        marker_2=dataclasses.Marker(
            image_position=torch.tensor([0, 400]),
            template_offset=torch.tensor([0, 1.0]),
            enu_position=torch.tensor(
                target_data["solar_tower_juelich_lower"]["upper_right"]
            ),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["upper_right_marker"]
            ),
        ),
        marker_3=dataclasses.Marker(
            image_position=torch.tensor([400, 0]),
            template_offset=torch.tensor([1.0, 0]),
            enu_position=torch.tensor(
                target_data["solar_tower_juelich_lower"]["lower_left"]
            ),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["lower_left_marker"]
            ),
        ),
        marker_4=dataclasses.Marker(
            image_position=torch.tensor([400, 400]),
            template_offset=torch.tensor([1.0, 1.00]),
            enu_position=torch.tensor(
                target_data["solar_tower_juelich_lower"]["lower_right"]
            ),
            template_image=util.load_image(
                target_data["solar_tower_juelich_lower"]["lower_right_marker"]
            ),
        ),
        output_shape=torch.Size([400, 400]),
        mask=mask,
    )

    # warp image
    warped_image = detect_target(image=image, target=target)
    focal_spot = detect_focal_spot(
        image=warped_image,
        num_k_means=num_k_means,
        target=target,
    )
    return focal_spot
