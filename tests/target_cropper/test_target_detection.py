import pathlib

import torch

from paint import PAINT_ROOT, target_cropper

TEST_DATA_PATH = pathlib.Path(PAINT_ROOT) / "tests" / "target_cropper" / "test_data"


def test_target_detection():
    """Test the target detection."""
    image = target_cropper.util.load_image(TEST_DATA_PATH / "uncropped_image.png")
    target = target_cropper.dataclasses.Target(
        marker_1=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 0]),
            template_offset=torch.tensor([0, 0.5]),
            enu_position=torch.tensor([0, 0, 1]),
            template_image=target_cropper.util.load_image(
                TEST_DATA_PATH / "markerLB.png"
            ),
        ),
        marker_2=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([200, 0]),
            template_offset=torch.tensor([0.5, 1.0]),
            enu_position=torch.tensor([1, 0, 0]),
            template_image=target_cropper.util.load_image(
                TEST_DATA_PATH / "markerLM.png"
            ),
        ),
        marker_3=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 400]),
            template_offset=torch.tensor([1.0, 0.5]),
            enu_position=torch.tensor([0, 0, -1]),
            template_image=target_cropper.util.load_image(
                TEST_DATA_PATH / "markerRB.png"
            ),
        ),
        marker_4=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([200, 400]),
            template_offset=torch.tensor([0.5, 0]),
            enu_position=torch.tensor([-1, 0, 0]),
            template_image=target_cropper.util.load_image(
                TEST_DATA_PATH / "markerRM.png"
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
