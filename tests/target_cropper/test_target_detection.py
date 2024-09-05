import os
import sys

import torch

from paint import target_cropper

lib_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))
sys.path.append(lib_dir)


def test_target_detection():
    """Test the target detection."""
    image = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "uncropped_image.png")
    )
    target = target_cropper.dataclasses.Target(
        marker_1=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([0, 200]),
            template_offset=torch.tensor([0, 0.5]),
            enu_position=torch.tensor([0, 0, 1]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "templates", "upper_center.png")
            ),
        ),
        marker_2=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([200, 400]),
            template_offset=torch.tensor([0.5, 1.0]),
            enu_position=torch.tensor([1, 0, 0]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "templates", "center_right.png")
            ),
        ),
        marker_3=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 200]),
            template_offset=torch.tensor([1.0, 0.5]),
            enu_position=torch.tensor([0, 0, -1]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "templates", "lower_center.png")
            ),
        ),
        marker_4=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([200, 0]),
            template_offset=torch.tensor([0.5, 0]),
            enu_position=torch.tensor([-1, 0, 0]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "templates", "center_left.png")
            ),
        ),
        output_shape=torch.Size([400, 400]),
        mask=None,
    )

    # warp image
    warped_image = target_cropper.detect_target(image=image, target=target)

    # Convert the tensor to a PIL image and display it
    warped_image_pil = target_cropper.util.to_image(warped_image)
    warped_image_pil.show()
