# from ...paint import target_cropper
import torch

import sys
import os

lib_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))
sys.path.append(lib_dir)
from paint import target_cropper


# TODO make real test
def main():
    num_k_means = 16
    applied_k_means = 5

    warped_image = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "focal_spot_image.png")
    )
    mask = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "mask.png")
    )

    focal_spot = target_cropper.detect_focal_spot(
        image=warped_image, num_k_means=num_k_means, applied_k_means=applied_k_means, mask= torch.where(mask != 0, torch.tensor(1.0), mask)
    )

    clustered_image = torch.zeros_like(warped_image)

    for k in torch.argsort(focal_spot.clusters.centers)[-applied_k_means:]:
        clustered_image[focal_spot.clusters.labels == k] += (
            focal_spot.clusters.centers[k] * 255
        )

    # Convert the tensor to a PIL image and display it
    clustered_image_pil = target_cropper.util.to_image(clustered_image)
    clustered_image_pil.show()


if __name__ == "__main__":
    main()
