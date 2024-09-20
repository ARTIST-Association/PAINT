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
                "longitude": np.array([6.38750587, 6.38785603]),
                "latitude": np.array([50.91338895, 50.91342485]),
                "Elevation": np.array([119.268, 144.82]),
            },
            {
                "solar_tower_juelich_upper": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (
                            50.91338911716799,
                            6.387794544159513,
                            130.09766666666667,
                        ),
                        "upper_left": (50.913389074925156, 6.38785596334749, 133.684),
                        "upper_middle": (50.91338901821958, 6.387794564665748, 133.71),
                        "upper_right": (50.91338922182834, 6.3877332676815515, 133.719),
                        "lower_left": (50.91338897581139, 6.387856033619183, 126.476),
                        "lower_right": (
                            50.913389266158724,
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
                        "upper_left": (50.91338897581139, 6.387856033619183, 126.476),
                        "upper_right": (
                            50.913389266158724,
                            6.3877334528986855,
                            126.506,
                        ),
                        "lower_left": (50.913388948892035, 6.387856019176258, 119.268),
                        "lower_middle": (
                            50.91338921611639,
                            6.3877945236532705,
                            119.269,
                        ),
                        "lower_right": (50.91338944678619, 6.3877331984554475, 119.279),
                    },
                },
                "multi_focus_tower": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (50.91339355918569, 6.3875444167659845, 138.97975),
                        "upper_left": (50.91339339750286, 6.387582963492142, 142.175),
                        "upper_right": (50.91339372487825, 6.387506012264232, 142.172),
                        "lower_left": (50.91339345190814, 6.387582821752781, 135.789),
                        "lower_right": (50.913393662428156, 6.387505869554209, 135.783),
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
                            50.91342438206257,
                            6.387826837461327,
                            144.805,
                        ),
                        "receiver_outer_upper_right": (
                            50.913424848806365,
                            6.387762101585306,
                            144.82,
                        ),
                        "receiver_outer_lower_left": (
                            50.91340258533124,
                            6.387826272355175,
                            139.596,
                        ),
                        "receiver_outer_lower_right": (
                            50.91340281604982,
                            6.38776223128536,
                            139.592,
                        ),
                        "receiver_inner_lower_left": (
                            50.913403653906435,
                            6.387823906642166,
                            139.86,
                        ),
                        "receiver_inner_lower_right": (
                            50.91340375876268,
                            6.387765282015661,
                            139.862,
                        ),
                        "receiver_inner_upper_left": (
                            50.91342356387283,
                            6.387824185899528,
                            144.592,
                        ),
                        "receiver_inner_upper_right": (
                            50.91342387604005,
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
    extremes, measurements = get_tower_measurements()
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
