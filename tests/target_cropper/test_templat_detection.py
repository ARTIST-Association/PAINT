import torch

import sys
import os

lib_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))
sys.path.append(lib_dir)
from paint import target_cropper

# TODO make real test
def main():
    image = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "template_test_data", "image.png")
    )
    template = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "template_test_data", "template.png")
    )

    template_pos = target_cropper.util.find_template_position(image=image,template=template,search_region=target_cropper.dataclasses.SearchRegion(position=torch.tensor([50,30]), dimension=torch.tensor([100,80])))
    H = 0
    W = 1
    image[template_pos[H]:template_pos[H]+template.shape[H], template_pos[W]:template_pos[W]+2] = 0
    image[template_pos[H]:template_pos[H]+template.shape[H], template_pos[W]+template.shape[W]:template_pos[W]+template.shape[W]+2] = 0
    image[template_pos[H]:template_pos[H]+2, template_pos[W]:template_pos[W]+template.shape[W]] = 0
    image[template_pos[H]+template.shape[H]:template_pos[H]+template.shape[H]+2, template_pos[1]:template_pos[W]+template.shape[W]] = 0

    target_cropper.util.to_image(image).show()


if __name__ == "__main__":
    main()