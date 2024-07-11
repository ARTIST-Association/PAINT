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
    target_size = 70,50
    template_pos = target_cropper.util.find_template_position(image=image,template=template,search_region=target_cropper.dataclasses.SearchRegion(position=torch.tensor([50,30]), dimension=torch.tensor([100,80])))
    pass


if __name__ == "__main__":
    main()