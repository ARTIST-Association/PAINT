from pathlib import Path
from typing import Union

import cv2
import numpy as np

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT


def load_and_preprocess_image(image_path: Path, resize: bool) -> np.ndarray:
    """
    Load and preprocess the image.

    Parameters
    ----------
    image_path : Path
        Path to the image file.
    resize : bool
        Whether to resize the image.

    Returns
    -------
    np.ndarray
        Preprocessed grayscale image.
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if resize:
        img = cv2.resize(
            src=img[
                mappings.INITIAL_HEIGHT : mappings.INITIAL_HEIGHT
                + mappings.HEIGHT_OFFSET,
                mappings.INITIAL_WIDTH : mappings.INITIAL_WIDTH + mappings.WIDTH_OFFSET,
            ],
            dsize=mappings.DESTINATION_SIZE,
        )
    return img


def get_marker_data(target: Union[str, int]) -> tuple[list[str], np.ndarray]:
    """
    Get marker names and their offsets based on the target.

    Parameters
    ----------
    target : Union[str,int]
        Target ID used to determine which marker should be used.

    Returns
    -------
    list[str]
        Required marker names.
    np.ndarray
        Offset values from the center of the template to the desired position in the template.
    """
    if target in {1, 7, mappings.STJ_LOWER}:
        return [
            "stj_left_middle",
            "stj_right_middle",
            "stj_left_bottom",
            "stj_right_bottom",
        ], np.array([[26, 78], [128, 84], [25.5, 126], [125, 127]])
    elif target in {4, 5, 6, mappings.STJ_UPPER}:
        return [
            "stj_left_top",
            "stj_right_top",
            "stj_left_middle",
            "stj_right_middle",
        ], np.array([[30, 29], [122, 27], [26, 78], [128, 84]])
    elif target in {3, mappings.MFT}:
        return [
            "mft_left_top",
            "mft_right_top",
            "mft_left_bottom",
            "mft_right_bottom",
        ], np.array([[45, 57], [200, 59], [48.5, 200], [192, 195]])
    else:
        raise ValueError(f"Unsupported target value: {target}")


def apply_template_matching(
    img_gray: np.ndarray, template: np.ndarray, search_radius: int
) -> tuple[np.ndarray, float]:
    """
    Apply template matching to detect the position of markers.

    Parameters
    ----------
    img_gray : np.ndarray
        Grayscale image on which to perform template matching.
    template : np.ndarray
        Template image for marker matching.
    search_radius : int
        Radius around detected markers to refine the position.

    Returns
    -------
    np.ndarray
        Sub-pixel adjusted position of the marker.
    float
        Maximum match quality value.
    """
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, loc = cv2.minMaxLoc(res)
    x, y = loc

    # Extract the region around the detected location for sub-pixel accuracy.
    interp_region = res[
        y - search_radius : y + search_radius + 1,
        x - search_radius : x + search_radius + 1,
    ]
    centroid_x = np.sum(np.arange(2 * search_radius + 1) * interp_region) / np.sum(
        interp_region
    )
    centroid_y = np.sum(np.arange(2 * search_radius + 1) * interp_region.T) / np.sum(
        interp_region
    )

    loc_sub = np.array([x + centroid_x - search_radius, y + centroid_y - search_radius])

    return loc_sub, max_val


def get_marker_positions(
    image_path: pathlib.Path,
    target: Union[int, str],
    search_radius: int = 10,
    resize: bool = False,
) -> tuple[np.ndarray, float]:
    """
    Load the image, detect marker positions, and return their sub-pixel locations.

    Parameters
    ----------
    image_path : Path
        Path to the image file.
    target : Union[int, str]
        Target type for marker selection.
    search_radius : int
        Radius around detected markers to refine the position. Default is ``10``.
    resize : bool
        Whether to resize the image for marker detection. Default is ``False``.

    Returns
    -------
    marker_positions : np.ndarray
        All identified marker positions. The height and width coordinates are provided.
    min_value : float
        Minimum matching quality value from template matching.
    """
    # Load and preprocess the image.
    img_gray = load_and_preprocess_image(image_path, resize)
    marker_names, offsets = get_marker_data(target)
    marker_positions = np.zeros((4, 2), dtype=np.float32)

    min_value = float("inf")  # Initialize minimum match quality.
    marker_path = Path(PAINT_ROOT) / mappings.MARKERS_FOLDER  # Path to marker templates

    # Iterate over each marker to detect and refine its position.
    for i, marker_name in enumerate(marker_names):
        template = cv2.imread(f"{marker_path}/{marker_name}.png", cv2.IMREAD_GRAYSCALE)
        loc_sub, max_val = apply_template_matching(img_gray, template, search_radius)
        marker_positions[i] = loc_sub + offsets[i]
        min_value = min(min_value, max_val)  # Track minimum match value.

    return marker_positions, min_value


def crop_image_with_template_matching(
    image_path: Path, target: Union[int, str], n_grid: int = 512
):
    """
    Use template matching to crop the images to the targets.

    Parameters
    ----------
    image_path : Path
        Path to the image file.
    target : Union[int, str]
        Target ID for marker detection.
    n_grid : int
        Size of the rectified grid. Default is 512.

    Returns
    -------
    np.ndarray
        Cropped image.

    Raises
    ------
    RuntimeError
        If the markers are not detected with sufficient accuracy.
    """
    resized = False
    marker_coords, min_ = get_marker_positions(image_path, target)

    # If match quality is low and target is MFT, retry with resizing (zoom has changed for target, i.e. the MFT).
    if min_ <= 0.85 and (target in {3, mappings.MFT}):
        marker_coords, min_ = get_marker_positions(image_path, target, resize=True)
        resized = True

    if min_ > 0.85:
        # Load the original image.
        original_image = cv2.imread(str(image_path))
        if resized:
            original_image = cv2.resize(
                src=original_image[
                    mappings.INITIAL_HEIGHT : mappings.INITIAL_HEIGHT
                    + mappings.HEIGHT_OFFSET,
                    mappings.INITIAL_WIDTH : mappings.INITIAL_WIDTH
                    + mappings.WIDTH_OFFSET,
                ],
                dsize=mappings.DESTINATION_SIZE,
            )

        # Define output coordinates for cropping.
        output_coords = np.array(
            [[0, 0], [n_grid, 0], [0, n_grid], [n_grid, n_grid]], dtype=np.float32
        )

        # Compute perspective transform and crop the image.
        transform_matrix = cv2.getPerspectiveTransform(marker_coords, output_coords)
        img_cropped = cv2.warpPerspective(
            original_image, transform_matrix, (n_grid, n_grid)
        )

        return img_cropped
    else:
        raise RuntimeError("Failed to detect markers with sufficient accuracy.")
