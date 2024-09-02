# from ...paint import target_cropper
import torch

import sys
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

lib_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir))
sys.path.append(lib_dir)
from paint import target_cropper


# TODO make real test
def main():
    num_k_means = 16
    applied_k_means = 5

    image = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "stj_data", "stj_target.png")
    )
    mask = target_cropper.util.load_image(
        os.path.join(__file__, os.pardir, "mask.png")
    )
    # mask = torch.where(mask != 0, torch.tensor(1.0), mask)
    mask = None

    with open(os.path.join(__file__, os.pardir, "stj_data", "stj-tower-measurements.json"), "r") as file:
        data_dict = json.load(file)

    target = target_cropper.dataclasses.Target(
        marker_1=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([0, 0]),
            template_offset=torch.tensor([0, 0]),
            enu_position=torch.tensor(data_dict["solar_tower_juelich_lower"]["upper_left"]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "stj_data", "stj_center_left.png")
            ),
        ),
        marker_2=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([0, 400]),
            template_offset=torch.tensor([0, 1.0]),
            enu_position=torch.tensor(data_dict["solar_tower_juelich_lower"]["upper_right"]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "stj_data", "stj_center_right.png")
            ),
        ),
        marker_3=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 0]),
            template_offset=torch.tensor([1.0, 0]),
            enu_position=torch.tensor(data_dict["solar_tower_juelich_lower"]["lower_left"]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "stj_data", "stj_lower_left.png")
            ),
        ),
        marker_4=target_cropper.dataclasses.Marker(
            image_position=torch.tensor([400, 400]),
            template_offset=torch.tensor([1.0, 1.00]),
            enu_position=torch.tensor(data_dict["solar_tower_juelich_lower"]["lower_right"]),
            template_image=target_cropper.util.load_image(
                os.path.join(__file__, os.pardir, "stj_data", "stj_lower_right.png")
            ),
        ),
        output_shape=torch.Size([400,400]),
        mask = mask
    )

    # warp image
    warped_image = target_cropper.detect_target(image=image, target=target)

    focal_spot = target_cropper.detect_focal_spot(
        image=warped_image, num_k_means=num_k_means, applied_k_means=applied_k_means, target=target
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

    lats = [m.enu_position[0] for m in target.markers]
    lons = [m.enu_position[1] for m in target.markers]
    alts = [m.enu_position[2] for m in target.markers]

    # Create a 3D scatter plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the points
    ax.scatter(lats, lons, alts, c='blue', marker='o')
    ax.scatter(focal_spot.aim_point[0], focal_spot.aim_point[1], focal_spot.aim_point[2], c="red", marker="x")

    # Set labels
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Altitude (m)')
    # ax.axis("equal")

    # Set the title
    ax.set_title('WGS84 Coordinates on a 3D Map')

    # Show the plot
    plt.show()
    plt.waitforbuttonpress()

if __name__ == "__main__":
    main()
