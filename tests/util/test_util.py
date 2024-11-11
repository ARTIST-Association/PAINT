import logging

import numpy as np
import pandas as pd
import pytest

import paint.util.paint_mappings as mappings
import paint.util.utils


def test_set_logger_conf() -> None:
    """Test logger configurator."""
    log = logging.getLogger(__name__)  # Get logger instance.
    paint.util.set_logger_config()
    log.info("This is a test log statement.")


def test_calculate_azimuth_and_elevation() -> None:
    """Test the calculation of azimuth and elevation based on sun position vectors."""
    sun_positions = pd.DataFrame(
        data={
            mappings.SUN_POSITION_EAST: [1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.5, -1.0],
            mappings.SUN_POSITION_NORTH: [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.5, -2.0],
            mappings.SUN_POSITION_UP: [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 10.0, -3.0],
        }
    )
    azimuth, elevation = paint.util.utils.calculate_azimuth_and_elevation(sun_positions)

    expected_azimuth = np.array(
        [90.0, 180.0, 180.0, 135.0, 90.0, 180.0, 135.0, 135.0, -26.56505118]
    )
    expected_elevation = np.array(
        [0.0, 0.0, 90.0, 0.0, 45.0, 45.0, 35.26438968, 85.95530876, -53.3007748]
    )

    assert (np.isclose(azimuth, expected_azimuth)).all()
    assert (np.isclose(elevation, expected_elevation)).all()


@pytest.mark.parametrize(
    "heliostat_id, heliostat_name", [(10841, "AH41"), (11537, "AO37"), (20352, "BC52")]
)
def test_heliostat_id_to_name(heliostat_id: int, heliostat_name: str) -> None:
    """
    Test conversion of heliostat ids to their string representation.

    Parameters
    ----------
    heliostat_id : int
        The heliostat ID as number
    heliostat_name : str
        The expected heliostat ID as string
    """
    assert paint.util.utils.heliostat_id_to_name(heliostat_id) == heliostat_name


def test_to_utc() -> None:
    """Test conversion of datetime strings from the Europe/Berlin timezone to UTC timestamps."""
    time_strings = pd.Series(
        ["2022-06-01 11:08:45", "2022-10-27 03:05:55", "2022-06-23 13:07:36"]
    )
    utc_timestamps = paint.util.utils.to_utc(time_strings)

    expected = pd.Series(
        [
            pd.Timestamp(
                year=2022, month=6, day=1, hour=9, minute=8, second=45, tz="UTC"
            ),
            pd.Timestamp(
                year=2022, month=10, day=27, hour=1, minute=5, second=55, tz="UTC"
            ),
            pd.Timestamp(
                year=2022, month=6, day=23, hour=11, minute=7, second=36, tz="UTC"
            ),
        ]
    )

    assert (utc_timestamps == expected).all()


@pytest.mark.parametrize(
    "original_time, expected_utc_time",
    [
        ("03:23:45 01-11-2023", "2023-01-11Z02:23:45Z"),
        ("20220405074517", "2022-04-05Z05:45:17Z"),
    ],
)
def test_single_time_conversion(original_time: str, expected_utc_time: str) -> None:
    """
    Test conversion of single string local times to UTC times.

    Parameters
    ----------
    original_time : str
        The original time string in the local time zone.
    expected_utc_time : str
        The expected time string in UTC time zone.
    """
    assert paint.util.utils.to_utc_single(original_time) == expected_utc_time
