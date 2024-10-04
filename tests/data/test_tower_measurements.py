from typing import Any

import deepdiff
import numpy as np
import pytest

from paint.data.tower_measurements import get_tower_measurements


@pytest.mark.parametrize(
    "expected_extremes, expected_measurements",
    [
        (
            {
                "Elevation": np.array([119.268, 144.82]),
                "latitude": np.array([50.91338895, 50.91342485]),
                "longitude": np.array([6.38750587, 6.38785603]),
            },
            {
                "power_plant_properties": {
                    "ID": "WRI1030197",
                    "coordinates": (50.913296351383806, 6.387514846666862, 87),
                },
                "solar_tower_juelich_upper": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (
                            50.91338911716799,
                            6.387794544159513,
                            130.09766666666667,
                        ),
                        "upper_left": (50.913389071462866, 6.38785596334749, 133.684),
                        "upper_middle": (50.91338901475729, 6.387794564665748, 133.71),
                        "upper_right": (50.91338921836604, 6.3877332676815515, 133.719),
                        "lower_left": (50.9133889723491, 6.387856033619183, 126.476),
                        "lower_right": (
                            50.913389262696434,
                            6.3877334528986855,
                            126.506,
                        ),
                    },
                },
                "solar_tower_juelich_lower": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (50.91338911716799, 6.387794544159513, 122.8815),
                        "upper_left": (50.9133889723491, 6.387856033619183, 126.476),
                        "upper_right": (
                            50.913389262696434,
                            6.3877334528986855,
                            126.506,
                        ),
                        "lower_left": (50.91338894542973, 6.387856019176258, 119.268),
                        "lower_middle": (
                            50.91338921265412,
                            6.3877945236532705,
                            119.269,
                        ),
                        "lower_right": (50.91338944332391, 6.3877331984554475, 119.279),
                    },
                },
                "multi_focus_tower": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (50.91339355918569, 6.3875444167659845, 138.97975),
                        "upper_left": (50.91339339404057, 6.387582963492142, 142.175),
                        "upper_right": (50.91339372141597, 6.387506012264232, 142.172),
                        "lower_left": (50.91339344844586, 6.387582821752781, 135.789),
                        "lower_right": (50.91339365896585, 6.387505869554209, 135.783),
                    },
                },
                "receiver": {
                    "type": "convex_cylinder",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (
                            50.91341371314919,
                            6.387794691724733,
                            142.22674999999998,
                        ),
                        "receiver_outer_upper_left": (
                            50.91342437860029,
                            6.387826837461327,
                            144.805,
                        ),
                        "receiver_outer_upper_right": (
                            50.91342484534406,
                            6.387762101585306,
                            144.82,
                        ),
                        "receiver_outer_lower_left": (
                            50.91340258186895,
                            6.387826272355175,
                            139.596,
                        ),
                        "receiver_outer_lower_right": (
                            50.913402812587535,
                            6.38776223128536,
                            139.592,
                        ),
                        "receiver_inner_lower_left": (
                            50.913403650444145,
                            6.387823906642166,
                            139.86,
                        ),
                        "receiver_inner_lower_right": (
                            50.91340375530039,
                            6.387765282015661,
                            139.862,
                        ),
                        "receiver_inner_upper_left": (
                            50.91342356041054,
                            6.387824185899528,
                            144.592,
                        ),
                        "receiver_inner_upper_right": (
                            50.91342387257775,
                            6.387765392341336,
                            144.593,
                        ),
                    },
                },
            },
        )
    ],
)
def test_tower_measurements(
    expected_extremes: dict[str, np.ndarray], expected_measurements: dict[Any, Any]
):
    """
    Test that the tower measurements are returned as expected.

    Parameters
    ----------
    expected_extremes : dict[str, np.ndarray]
        The expected max and min values from each coordinate.
    expected_measurements : dict[Any, Any]
        The expected tower measurements dictionary.
    """
    extremes, measurements = get_tower_measurements(use_wgs84=True)
    assert not deepdiff.DeepDiff(
        extremes,
        expected_extremes,
        ignore_numeric_type_changes=True,
        significant_digits=7,
    )
    assert not deepdiff.DeepDiff(
        measurements,
        expected_measurements,
        ignore_numeric_type_changes=True,
        significant_digits=7,
    )
