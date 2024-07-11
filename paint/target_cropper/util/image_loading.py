from PIL import Image
import os
import torch
import numpy as np


def load_image(image_path: os.path, load_color: bool = False) -> torch.Tensor:
    """
    @brief Loads an image and transforms it into a pytorch tensor.

    @param image_path The path to the image.
    @param load_color If True all three color channels are stored, else the image is converted to grey scale.

    @return Image as tensor with value range [0,1]
    """
    image = (
        Image.open(image_path) if load_color else Image.open(image_path).convert("L")
    )  # 'L' mode is for grayscale

    # Convert the image to a tensor
    image_np = np.array(image, dtype=float) / 255.0  # shape: [H, W]
    image_tensor = torch.tensor(image_np)
    return image_tensor


def to_image(tensor: torch.Tensor) -> Image:
    """
    @brief Converts a tensor into a pillow image. Also converts values from range [0,1] to [0,255]
    @return Pillow Image
    """
    return Image.fromarray(np.array((tensor*255).tolist(), dtype=np.uint8))
