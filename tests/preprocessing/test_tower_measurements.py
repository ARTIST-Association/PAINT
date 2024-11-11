from typing import Any

import deepdiff
import numpy as np
import pytest

from paint.preprocessing.tower_measurements import get_tower_measurements


@pytest.mark.parametrize(
    "expected_extremes, expected_measurements",
    [
        (
            {
                "longitude": np.array([6.38753589, 6.38788605]),
                "latitude": np.array([50.91339184, 50.91342774]),
                "Elevation": np.array([119.268, 144.82]),
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
                            50.91339203683997,
                            6.387824563513243,
                            130.09766666666667,
                        ),
                        "upper_left": (50.91339196507306, 6.387885982262168, 133.684),
                        "upper_middle": (50.91339190867828, 6.387824583774972, 133.71),
                        "upper_right": (50.91339211259599, 6.387763286988281, 133.719),
                        "lower_left": (50.91339186595943, 6.387886052532388, 126.476),
                        "lower_right": (50.91339215692524, 6.387763472205384, 126.506),
                    },
                },
                "solar_tower_juelich_lower": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (50.91339203683997, 6.387824563513243, 122.8815),
                        "upper_left": (50.91339186595943, 6.387886052532388, 126.476),
                        "upper_right": (50.91339215692524, 6.387763472205384, 126.506),
                        "lower_left": (50.913391839040266, 6.38788603808917, 119.268),
                        "lower_middle": (
                            50.913392106574314,
                            6.387824542765122,
                            119.269,
                        ),
                        "lower_right": (50.9133923375531, 6.387763217765237, 119.279),
                    },
                },
                "multi_focus_tower": {
                    "type": "planar",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (50.91339645088695, 6.387574436728054, 138.97975),
                        "upper_left": (50.91339628900999, 6.387612983329584, 142.175),
                        "upper_right": (50.913396616772935, 6.387536032350528, 142.172),
                        "lower_left": (50.91339634341573, 6.387612841591359, 135.789),
                        "lower_right": (50.91339655432386, 6.3875358896401675, 135.783),
                    },
                },
                "receiver": {
                    "type": "convex_cylinder",
                    "normal_vector": (0, 1, 0),
                    "coordinates": {
                        "center": (
                            50.91341660151,
                            6.387825304776098,
                            142.22674999999998,
                        ),
                        "receiver_outer_upper_left": (
                            50.91342727218299,
                            6.387856856914401,
                            144.805,
                        ),
                        "receiver_outer_upper_right": (
                            50.91342773925188,
                            6.387792121250145,
                            144.82,
                        ),
                        "receiver_outer_lower_left": (
                            50.91340547556243,
                            6.3878562915348525,
                            139.596,
                        ),
                        "receiver_outer_lower_right": (
                            50.91340570660373,
                            6.387792250671612,
                            139.592,
                        ),
                        "receiver_inner_lower_left": (
                            50.913406544144294,
                            6.387853925842858,
                            139.86,
                        ),
                        "receiver_inner_lower_right": (
                            50.91340664929649,
                            6.387795301404112,
                            139.862,
                        ),
                        "receiver_inner_upper_left": (
                            50.91342645401072,
                            6.387854205350705,
                            144.592,
                        ),
                        "receiver_inner_upper_right": (
                            50.91342676647371,
                            6.387795411983428,
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
