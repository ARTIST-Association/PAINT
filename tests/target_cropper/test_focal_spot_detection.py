import os
import pathlib
import sys

import torch

from paint import PAINT_ROOT, target_cropper

lib_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))
sys.path.append(lib_dir)


def test_focal_spot_detection() -> None:
    """Test the focal spot detection."""
    num_k_means = 16
    applied_k_means = 5

    warped_image = target_cropper.util.load_image(
        pathlib.Path(PAINT_ROOT)
        / "tests"
        / "target_cropper"
        / "test_data"
        / "focal_spot_image.png"
    )

    mask = target_cropper.util.load_image(
        pathlib.Path(PAINT_ROOT) / "tests" / "target_cropper" / "test_data" / "mask.png"
    )
    mask = torch.where(mask != 0, torch.tensor(1.0), mask)

    target = target_cropper.dataclasses.Target(
        marker_1=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([0, 0]),
            template_offset=torch.tensor([0, 0.5]),
            enu_position=torch.tensor([-1, 0, 1]),
            template_image=target_cropper.util.load_image(
                pathlib.Path(PAINT_ROOT)
                / "tests"
                / "target_cropper"
                / "test_data"
                / "stj_center_left.png"
            ),
        ),
        marker_2=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([0, 400]),
            template_offset=torch.tensor([0.5, 1.0]),
            enu_position=torch.tensor([1, 0, 1]),
            template_image=target_cropper.util.load_image(
                pathlib.Path(PAINT_ROOT)
                / "tests"
                / "target_cropper"
                / "test_data"
                / "stj_center_right.png"
            ),
        ),
        marker_3=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 0]),
            template_offset=torch.tensor([1.0, 0.5]),
            enu_position=torch.tensor([-1, 0, -1]),
            template_image=target_cropper.util.load_image(
                pathlib.Path(PAINT_ROOT)
                / "tests"
                / "target_cropper"
                / "test_data"
                / "stj_lower_left.png"
            ),
        ),
        marker_4=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 400]),
            template_offset=torch.tensor([0.5, 0]),
            enu_position=torch.tensor([1, 0, -1]),
            template_image=target_cropper.util.load_image(
                pathlib.Path(PAINT_ROOT)
                / "tests"
                / "target_cropper"
                / "test_data"
                / "stj_lower_right.png"
            ),
        ),
        output_shape=torch.Size([400, 400]),
        mask=mask,
    )

    focal_spot = target_cropper.detect_focal_spot(
        image=warped_image,
        num_k_means=num_k_means,
        target=target,
    )

    # TODO retransform image coordinates to field coordinates
    # equal to target detection
    # approach 1 (schöner für pytorch):
    # use marker image coordinates 2d [w,h] -> [w,h,0]
    # get marker e,n,u coordiantes
    # compute transformation from marker stc [w,h,0] dest [e,n,u]
    # apply transformation to focal spot [w,h,0] -> [e,n,u] -> aim point

    # approach 2 (dlr):
    # split target into triangles
    # use barycentric coordinates from [w,h] -> barycentric -> [e,n,u]

    clustered_image = torch.zeros_like(warped_image)

    for k in torch.argsort(focal_spot.clusters.centers)[-applied_k_means:]:
        clustered_image[focal_spot.clusters.labels == k] += (
            focal_spot.clusters.centers[k] * 255
        )

    # Convert the tensor to a PIL image and display it
    clustered_image_pil = target_cropper.util.to_image(clustered_image)
    clustered_image_pil.show()
