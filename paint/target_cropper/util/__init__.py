"""
@brief collection of utils for target referencing and spot detection
"""
from .image_loading import load_image, to_image
from .template_matching import find_template_position, find_template_position_cv
from .perspective_transformation import compute_transform, apply_transform, compute_transform_cv, apply_transform_cv
from .clustering import kmeans
from .center_of_intensity import compute_center_of_intensity
from .image_cropping import crop_image, get_parent_coordinate