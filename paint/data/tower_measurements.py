from typing import Any, Dict, List, Tuple

import numpy as np

import paint.util.paint_mappings as mappings
from paint.util.gauss_kruger_convertor import convert_gk_to_lat_long


def extract_coordinate_tuples(coordinate_tuples_dict: Dict[Any, Any]) -> List[tuple]:
    """
    Extract the tuples of coordinates (latitude, longitude, elevation) from a nested dictionary.

    Parameters
    ----------
    coordinate_tuples_dict : Dict[Any, Any]
        A nested dictionary containing coordinate tuples as keys.

    Returns
    -------
    List[tuple]
        A list of extracted coordinate tuples.
    """
    tuples = []
    for value in coordinate_tuples_dict.values():
        if isinstance(value, dict):
            # Recursively extract tuples from nested dictionaries
            tuples.extend(extract_coordinate_tuples(value))
        elif isinstance(value, tuple) and len(value) == 3:
            # Check if the value is a 3D tuple
            tuples.append(value)
    return tuples


def find_min_max_coordinate(
    coordinate_dictionary: Dict[Any, Any],
) -> Dict[str, np.ndarray]:
    """
    Extract the min and max values of coordinates (latitude, longitude, elevation) from a nested dictionary.

    Parameters
    ----------
    coordinate_dictionary : Dict[Any, Any]
        A nested dictionary containing coordinate tuples.

    Returns
    -------
    Dict[str, np.ndarray]
        A dictionary containing min and max coordinates for latitude, longitude, and elevation.
    """
    # Extract all lat/lon/elevation tuples
    tuples = extract_coordinate_tuples(coordinate_dictionary)

    # Unzip the tuples into three lists, one for each coordinate
    latitudes, longitudes, elevations = zip(*tuples)

    # Find min and max for each coordinate
    min_latitude, max_latitude = min(latitudes), max(latitudes)
    min_longitude, max_longitude = min(longitudes), max(longitudes)
    min_elevation, max_elevation = min(elevations), max(elevations)
    return {
        mappings.LONGITUDE_KEY: np.array([min_longitude, max_longitude]),
        mappings.LATITUDE_KEY: np.array([min_latitude, max_latitude]),
        mappings.ELEVATION: np.array([min_elevation, max_elevation]),
    }


def get_tower_measurements() -> Tuple[Dict[str, np.ndarray], Dict[Any, Any]]:
    """
    Generate the tower measurement data.

    This data takes the measured Gauss-Kruger coordinates for each considered calibration target and receiver, converts
    them to latitude and longitude coordinates, considers the elevation and returns these values in a dictionary.
    Additionally, the min and max values for each of the dimensions in the coordinates are saved for the STAC item
    creation.

    Returns
    -------
    Tuple[Dict[str, np.ndarray], Dict[Any, Any]]
        The saved max and min values for each dimension in the coordinates, and the measurement dictionary.
    """
    # ------------------ STJ Upper Coordinates ----------------------------------------------------
    stj_upper_left = convert_gk_to_lat_long(
        2527321.418,
        5642083.398,
    ) + (133.684,)
    stj_upper_middle = convert_gk_to_lat_long(
        2527317.1,
        5642083.369,
    ) + (133.71,)
    stj_upper_right = convert_gk_to_lat_long(
        2527312.789,
        5642083.369,
    ) + (133.719,)
    stj_middle_left = convert_gk_to_lat_long(
        2527321.423,
        5642083.387,
    ) + (126.476,)
    stj_middle_right = convert_gk_to_lat_long(
        2527312.802,
        5642083.374,
    ) + (126.506,)

    # Save coordinates for STJ Upper target
    stj_upper_coordinates = {
        mappings.CENTER: mappings.STJ_UPPER_COORDINATES,
        mappings.UPPER_LEFT: stj_upper_left,
        mappings.UPPER_MIDDLE: stj_upper_middle,
        mappings.UPPER_RIGHT: stj_upper_right,
        mappings.LOWER_LEFT: stj_middle_left,
        mappings.LOWER_RIGHT: stj_middle_right,
    }

    # ------------------ STJ LOWER Coordinates ----------------------------------------------------
    stj_lower_left = convert_gk_to_lat_long(
        2527321.422,
        5642083.384,
    ) + (119.268,)
    stj_lower_middle = convert_gk_to_lat_long(
        2527317.097,
        5642083.391,
    ) + (119.269,)
    stj_lower_right = convert_gk_to_lat_long(
        2527312.784,
        5642083.394,
    ) + (119.279,)

    # save coordinates for STJ Lower target
    stj_lower_coordinates = {
        mappings.CENTER: mappings.STJ_LOWER_COORDINATES,
        mappings.UPPER_LEFT: stj_middle_left,
        mappings.UPPER_RIGHT: stj_middle_right,
        mappings.LOWER_LEFT: stj_lower_left,
        mappings.LOWER_MIDDLE: stj_lower_middle,
        mappings.LOWER_RIGHT: stj_lower_right,
    }

    # ------------------ MFT Coordinates ----------------------------------------------------
    mft_upper_left = convert_gk_to_lat_long(2527302.216, 5642083.778) + (142.175,)
    mft_upper_right = convert_gk_to_lat_long(2527296.804, 5642083.786) + (142.172,)
    mft_lower_right = convert_gk_to_lat_long(2527296.794, 5642083.779) + (135.783,)
    mft_lower_left = convert_gk_to_lat_long(2527302.206, 5642083.784) + (135.789,)

    # save coordinates for MFT target
    mft_coordinates = {
        mappings.CENTER: mappings.MFT_COORDINATES,
        mappings.UPPER_LEFT: mft_upper_left,
        mappings.UPPER_RIGHT: mft_upper_right,
        mappings.LOWER_LEFT: mft_lower_left,
        mappings.LOWER_RIGHT: mft_lower_right,
    }

    # ------------------ Receiver Coordinates ----------------------------------------------------
    receiver_outer_upper_left = convert_gk_to_lat_long(2527319.349, 5642087.315) + (
        144.805,
    )
    receiver_inner_upper_left = convert_gk_to_lat_long(2527319.163, 5642087.223) + (
        144.592,
    )
    receiver_inner_upper_right = convert_gk_to_lat_long(2527315.028, 5642087.236) + (
        144.593,
    )
    receiver_outer_upper_right = convert_gk_to_lat_long(2527314.796, 5642087.343) + (
        144.82,
    )
    receiver_outer_lower_left = convert_gk_to_lat_long(2527319.322, 5642084.89) + (
        139.596,
    )
    receiver_inner_lower_left = convert_gk_to_lat_long(2527319.155, 5642085.008) + (
        139.86,
    )
    receiver_inner_lower_right = convert_gk_to_lat_long(2527315.032, 5642084.998) + (
        139.862,
    )
    receiver_outer_lower_right = convert_gk_to_lat_long(2527314.818, 5642084.892) + (
        139.592,
    )

    # save receiver coordinates
    receiver_coordinates = {
        mappings.CENTER: mappings.RECEIVER_COORDINATES,
        mappings.RECEIVER_OUTER_UPPER_LEFT: receiver_outer_upper_left,
        mappings.RECEIVER_OUTER_UPPER_RIGHT: receiver_outer_upper_right,
        mappings.RECEIVER_OUTER_LOWER_LEFT: receiver_outer_lower_left,
        mappings.RECEIVER_OUTER_LOWER_RIGHT: receiver_outer_lower_right,
        mappings.RECEIVER_INNER_LOWER_LEFT: receiver_inner_lower_left,
        mappings.RECEIVER_INNER_LOWER_RIGHT: receiver_inner_lower_right,
        mappings.RECEIVER_INNER_UPPER_LEFT: receiver_inner_upper_left,
        mappings.RECEIVER_INNER_UPPER_RIGHT: receiver_inner_upper_right,
    }

    # ------------------ Final Coordinates ----------------------------------------------------
    # create full tower measurements dictionary
    tower_measurements = {
        mappings.STJ_UPPER: stj_upper_coordinates,
        mappings.STJ_LOWER: stj_lower_coordinates,
        mappings.MFT: mft_coordinates,
        mappings.RECEIVER: receiver_coordinates,
    }

    # save min and max of all coordinates for STAC file
    extreme_coordinates = find_min_max_coordinate(tower_measurements)

    return extreme_coordinates, tower_measurements


if __name__ == "__main__":
    a, b = get_tower_measurements()
    print("HI")
