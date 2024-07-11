import torch
import torch.nn.functional as F


def compute_transform(src: torch.Tensor, dst: torch.Tensor) -> torch.Tensor:
    """
    @brief Computes a perspective transformation (matrix) from given source and destination control points.

    @param src Source control points to be mapped onto the destination points.
    @param dst Destination control points (must have same shape as src).

    @return perspective transformation tensor of shape (2 x 3)
    """

    # Construct the matrix A
    A = torch.zeros((8, 6), dtype=torch.float32)
    for i in range(4):
        x, y = src[i]
        u, v = dst[i]
        A[2 * i] = torch.tensor([x, y, 1, 0, 0, 0], dtype=torch.float32)
        A[2 * i + 1] = torch.tensor([0, 0, 0, x, y, 1], dtype=torch.float32)

    # Construct the vector B
    B = torch.tensor(dst, dtype=torch.float32).view(-1)

    # Solve the equation A * M = B using SVD
    U, S, V = torch.linalg.svd(A)
    S_inv = torch.diag_embed(1.0 / S[:6])  # Take the pseudo-inverse
    M = torch.matmul(torch.matmul(V[:, :6], S_inv), torch.transpose(U[:, :6], 0, 1))
    M = torch.matmul(M, B)

    # Reshape M to be a 2x3 matrix
    M = torch.reshape(M, (2, 3))

    return M


def apply_transform(image: torch.Tensor, transform: torch.Tensor, output_shape: torch.Size) -> torch.Tensor:
    """
    @brief Applies a perspective transformation to an image.

    @param image Image to be transformed. Must have shape (height x width).
    @param transform The transformation to be applied. Must have shape (2 x 3).
    @param output_shape The desired output shape of the transformed image (height x width).

    @return transformed image with output_shape.
    """
    # Generate the perspective grid
    grid = F.affine_grid(
        transform.unsqueeze(0), torch.Size((1, 1, output_shape[0], output_shape[1])), align_corners=False
    )

    # Apply the grid to the image
    warped_image = F.grid_sample(image.unsqueeze(0).unsqueeze(0), grid, align_corners=False).squeeze()
    return warped_image
