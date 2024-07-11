import torch
import torch.nn.functional as F
from ..dataclasses import KMeansCluster


def generate_pixel_positions(width : int, height : int) -> torch.Tensor:
    """
    @brief generate a list of pixel positions from given width and height.
    
    @param width The image width.
    @param height The image height.

    @return tensor of pixel positions for an image
    """
    positions = []
    for y in range(height):
        for x in range(width):
            positions.append((x, y))
    return torch.tensor(positions, dtype=torch.float32)


def kmeans(
    image: torch.Tensor, num_clusters: int, num_iters: int = 100
) -> KMeansCluster:
    """
    @brief computes k-means intensity clustering on a given grey scale image.

    @param image The given image (must be grayscale).
    @param num_clusters The number of k-means clusters to be generated.
    @param num_iters Allowed number of iterations to create the clusters.

    @return clustered image data
    """

    # Generate random cluster centers
    pixel_values = image.flatten()
    centers = torch.linspace(0, 1, steps=num_clusters)

    for i in range(num_iters):
        # Assign each point to the closest cluster center
        labels = torch.argmin(
            torch.abs(pixel_values.unsqueeze(dim=1).repeat(1, num_clusters) - centers), dim=1
        )

        # Compute new cluster centers as the mean of points in each cluster
        new_centers = torch.stack(
            [pixel_values[labels == k].mean() for k in range(num_clusters)]
        )

        # If centers do not change, break early
        if torch.all(centers == new_centers):
            break

        centers = new_centers

    # compute cluster center positions
    pixel_positions = generate_pixel_positions(image.shape[0], image.shape[1])
    center_positions = torch.stack(
        [pixel_positions[labels == k].mean(dim=0) for k in range(num_clusters)]
    )

    return KMeansCluster(
        centers=centers,
        labels=labels.reshape((400, 400)),
        center_positions=center_positions,
    )
