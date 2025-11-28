from typing import Any

import numpy as np

import paint.util.paint_mappings as mappings
from paint.util.gauss_kruger_converter import convert_gk_to_lat_long


def extract_coordinate_tuples(coordinate_tuples_dict: dict[Any, Any]) -> list[tuple]:
    """
    Extract the tuples of coordinates (latitude, longitude, elevation) from a nested dictionary.

    Parameters
    ----------
    coordinate_tuples_dict : dict[Any, Any]
        A nested dictionary containing coordinate tuples as keys.

    Returns
    -------
    list[tuple]
        The list of extracted coordinate tuples.
    """
    coordinate_tuples = []
    for value in coordinate_tuples_dict.values():
        if isinstance(value, dict):
            # Recursively extract tuples from nested dictionaries.
            coordinate_tuples.extend(extract_coordinate_tuples(value))
        elif isinstance(value, tuple) and len(value) == 3:
            # Check if the value is a 3D tuple.
            coordinate_tuples.append(value)
    return coordinate_tuples


def find_min_max_coordinate(
    coordinate_dictionary: dict[Any, Any],
) -> dict[str, np.ndarray]:
    """
    Extract the min and max values of coordinates (latitude, longitude, elevation) from a nested dictionary.

    Parameters
    ----------
    coordinate_dictionary : dict[Any, Any]
        A nested dictionary containing coordinate tuples.

    Returns
    -------
    dict[str, np.ndarray]
        A dictionary containing min and max coordinates for latitude, longitude, and elevation.
    """
    # Extract all lat/lon/elevation tuples.
    tuples = extract_coordinate_tuples(coordinate_dictionary)

    # Unzip the tuples into three lists, one for each coordinate.
    latitudes, longitudes, elevations = zip(*tuples)

    # Find min and max for each coordinate.
    min_latitude, max_latitude = min(latitudes), max(latitudes)
    min_longitude, max_longitude = min(longitudes), max(longitudes)
    min_elevation, max_elevation = min(elevations), max(elevations)
    return {
        mappings.LONGITUDE_KEY: np.array([min_longitude, max_longitude]),
        mappings.LATITUDE_KEY: np.array([min_latitude, max_latitude]),
        mappings.ELEVATION: np.array([min_elevation, max_elevation]),
    }


def get_tower_measurements() -> tuple[dict[str, np.ndarray], dict[Any, Any]]:
    """
    Generate the tower measurement data.

    This data takes the measured Gauss-Kruger coordinates for each considered calibration target and receiver, converts
    them to latitude and longitude coordinates, considers the elevation and returns these values in a dictionary.
    Additionally, the min and max values for each of the dimensions in the coordinates are saved for the STAC item
    creation.

    Returns
    -------
    dict[str, np.ndarray]
        The saved max and min values for each dimension in the coordinates.
    dict[Any, Any]
        The measurement dictionary.
    """
    # ------------------ Solar Tower Juelich (STJ) Upper Coordinates --------------------------------------------------
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

    # Save coordinates for STJ upper target.
    stj_upper_coordinates = {
        mappings.CENTER: mappings.STJ_UPPER_CENTER,
        mappings.UPPER_LEFT: stj_upper_left,
        mappings.UPPER_MIDDLE: stj_upper_middle,
        mappings.UPPER_RIGHT: stj_upper_right,
        mappings.LOWER_LEFT: stj_middle_left,
        mappings.LOWER_RIGHT: stj_middle_right,
    }

    # ------------------ Solar Tower Juelich (STJ) LOWER Coordinates -----------------------------------------------
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

    # Save coordinates for STJ lower target.
    stj_lower_coordinates = {
        mappings.CENTER: mappings.STJ_LOWER_CENTER,
        mappings.UPPER_LEFT: stj_middle_left,
        mappings.UPPER_RIGHT: stj_middle_right,
        mappings.LOWER_LEFT: stj_lower_left,
        mappings.LOWER_MIDDLE: stj_lower_middle,
        mappings.LOWER_RIGHT: stj_lower_right,
    }

    # ------------------ Multi Focus Tower (MFT) Coordinates ----------------------------------------------------
    mft_upper_left = convert_gk_to_lat_long(
        2527302.216,
        5642083.778,
    ) + (142.175,)
    mft_upper_right = convert_gk_to_lat_long(
        2527296.804,
        5642083.786,
    ) + (142.172,)
    mft_lower_right = convert_gk_to_lat_long(
        2527296.794,
        5642083.779,
    ) + (135.783,)
    mft_lower_left = convert_gk_to_lat_long(
        2527302.206,
        5642083.784,
    ) + (135.789,)

    # Save coordinates for MFT target.
    mft_coordinates = {
        mappings.CENTER: mappings.MFT_CENTER,
        mappings.UPPER_LEFT: mft_upper_left,
        mappings.UPPER_RIGHT: mft_upper_right,
        mappings.LOWER_LEFT: mft_lower_left,
        mappings.LOWER_RIGHT: mft_lower_right,
    }

    # ------------------ Receiver Coordinates ----------------------------------------------------
    receiver_outer_upper_left = convert_gk_to_lat_long(
        2527319.349,
        5642087.315,
    ) + (144.805,)
    receiver_inner_upper_left = convert_gk_to_lat_long(
        2527319.163,
        5642087.223,
    ) + (144.592,)
    receiver_inner_upper_right = convert_gk_to_lat_long(
        2527315.028,
        5642087.236,
    ) + (144.593,)
    receiver_outer_upper_right = convert_gk_to_lat_long(
        2527314.796,
        5642087.343,
    ) + (144.82,)
    receiver_outer_lower_left = convert_gk_to_lat_long(
        2527319.322,
        5642084.89,
    ) + (139.596,)
    receiver_inner_lower_left = convert_gk_to_lat_long(
        2527319.155,
        5642085.008,
    ) + (139.86,)
    receiver_inner_lower_right = convert_gk_to_lat_long(
        2527315.032,
        5642084.998,
    ) + (139.862,)
    receiver_outer_lower_right = convert_gk_to_lat_long(
        2527314.818,
        5642084.892,
    ) + (139.592,)

    # Save receiver coordinates.
    receiver_coordinates = {
        mappings.CENTER: mappings.RECEIVER_CENTER,
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
    # Create full tower measurements dictionary.
    tower_coordinates = {
        mappings.STJ_UPPER: stj_upper_coordinates,
        mappings.STJ_LOWER: stj_lower_coordinates,
        mappings.MFT: mft_coordinates,
        mappings.RECEIVER: receiver_coordinates,
    }
    power_plant_lat, power_plant_lon = convert_gk_to_lat_long(
        mappings.GK_RIGHT_BASE, mappings.GK_HEIGHT_BASE
    )

    tower_properties = {
        mappings.POWER_PLANT_KEY: {
            mappings.ID_KEY: mappings.POWER_PLANT_GPPD_ID,
            mappings.TOWER_COORDINATES_KEY: (
                power_plant_lat,
                power_plant_lon,
                mappings.POWER_PLANT_ALT,
            ),
        },
        mappings.STJ_UPPER: {
            mappings.TOWER_TYPE_KEY: mappings.PLANAR_KEY,
            mappings.TOWER_NORMAL_VECTOR_KEY: mappings.TOWER_NORMAL_VECTOR,
            mappings.TOWER_COORDINATES_KEY: stj_upper_coordinates,
        },
        mappings.STJ_LOWER: {
            mappings.TOWER_TYPE_KEY: mappings.PLANAR_KEY,
            mappings.TOWER_NORMAL_VECTOR_KEY: mappings.TOWER_NORMAL_VECTOR,
            mappings.TOWER_COORDINATES_KEY: stj_lower_coordinates,
        },
        mappings.MFT: {
            mappings.TOWER_TYPE_KEY: mappings.PLANAR_KEY,
            mappings.TOWER_NORMAL_VECTOR_KEY: mappings.TOWER_NORMAL_VECTOR,
            mappings.TOWER_COORDINATES_KEY: mft_coordinates,
        },
        mappings.RECEIVER: {
            mappings.TOWER_TYPE_KEY: mappings.CONVEX_CYLINDER_KEY,
            mappings.TOWER_NORMAL_VECTOR_KEY: mappings.RECEIVER_NORMAL_VECTOR,
            mappings.TOWER_COORDINATES_KEY: receiver_coordinates,
        },
    }

    # Also save min and max of all coordinates for STAC file.
    return find_min_max_coordinate(tower_coordinates), tower_properties
