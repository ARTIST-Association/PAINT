import pathlib

import numpy as np
import torch
from PIL import Image


def load_image(image_path: pathlib.Path, load_color: bool = False) -> torch.Tensor:
    """
    Load an image and transform it into a pytorch tensor.

    Parameters
    ----------
    image_path : pathlib.Path
        The path to the image.
    load_color : bool
        Whether all three color channels are stored.

    Returns
    -------
    torch.Tensor
        Image with a value range between 0 and 1.
    """
    image = (
        Image.open(image_path) if load_color else Image.open(image_path).convert("L")
    )  # 'L' mode is for grayscale

    # Convert the image to a tensor
    image_array = np.array(image, dtype=float) / 255.0  # shape: [H, W]
    return torch.tensor(image_array)


def to_image(tensor: torch.Tensor) -> Image.Image:
    """
    Convert a tensor into a pillow image and values from range [0,1] to [0,255].

    Parameters
    ----------
    tensor : torch.Tensor
        Input tensor to convert.

    Returns
    -------
    Image.Image
        Converted image.
    """
    return Image.fromarray(np.array((tensor * 255).tolist(), dtype=np.uint8))
