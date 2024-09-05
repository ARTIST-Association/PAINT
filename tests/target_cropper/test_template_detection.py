import pathlib

import torch

from paint import PAINT_ROOT, target_cropper

TEST_DATA_PATH = pathlib.Path(PAINT_ROOT) / "tests" / "target_cropper" / "test_data"


def test_template_detection():
    """Test the template detection."""
    image = target_cropper.util.load_image(TEST_DATA_PATH / "image.png")
    template = target_cropper.util.load_image(TEST_DATA_PATH / "template.png")

    template_pos = target_cropper.util.find_template_position(
        image=image,
        template=template,
        search_region=target_cropper.dataclasses.SearchRegion(
            position=torch.tensor([50, 30]), dimension=torch.tensor([100, 80])
        ),
    )
    h = 0
    w = 1
    image[
        template_pos[h] : template_pos[h] + template.shape[h],
        template_pos[w] : template_pos[w] + 1,
    ] = 0
    image[
        template_pos[h] : template_pos[h] + template.shape[h],
        template_pos[w] + template.shape[w] : template_pos[w] + template.shape[w] + 1,
    ] = 0
    image[
        template_pos[h] : template_pos[h] + 1,
        template_pos[w] : template_pos[w] + template.shape[w],
    ] = 0
    image[
        template_pos[h] + template.shape[h] : template_pos[h] + template.shape[h] + 1,
        template_pos[1] : template_pos[w] + template.shape[w],
    ] = 0

    target_cropper.util.to_image(image).show()
