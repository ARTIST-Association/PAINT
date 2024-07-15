import os
import tempfile
from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock, patch

import h5py
import pandas as pd
import pytest

from paint.data.dwd_weather import DWDWeatherData


@pytest.fixture
def mock_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate mock data instead of downloading the data from DWD.

    Returns
    -------
    pd.DataFrame
        The mock metadata a weather station included in the 10min temporal resolution data request.
    pd.DataFrame
        The mock metadata a weather station included in the 1h temporal resolution data request.
    pd.DataFrame
        The mock data for the weather variables downloaded in 10min temporal resolution.
    pd.DataFrame
        The mock data for the weather variables downloaded in 1h temporal resolution.
    """
    metadata = pd.DataFrame(
        {
            "station_id": ["15000"],
            "height": [231.0],
            "latitude": [50.7983],
            "longitude": [6.0244],
            "name": ["Aachen-Orsbach"],
            "state": ["Nordrhein-Westfalen"],
        }
    )

    data_10min = pd.DataFrame(
        {
            "station_id": ["15000", "15000", "15000", "15000", "15000", "15000"],
            "parameter": [
                "radiation_global",
                "radiation_global",
                "radiation_global",
                "sunshine_duration",
                "sunshine_duration",
                "sunshine_duration",
            ],
            "date": pd.to_datetime(
                [
                    "2021-04-01 00:00:00",
                    "2021-04-01 00:10:00",
                    "2021-04-01 00:20:00",
                    "2021-04-01 00:00:00",
                    "2021-04-01 00:10:00",
                    "2021-04-01 00:20:00",
                ]
            ),
            "value": [0.0, 1.0, 2.0, 10.0, 11.0, 12.0],
        }
    )

    data_1h = pd.DataFrame(
        {
            "station_id": ["15000", "15000", "15000", "15000", "15000", "15000"],
            "parameter": [
                "cloud_cover_total",
                "cloud_cover_total",
                "cloud_cover_total",
                "weather",
                "weather",
                "weather",
            ],
            "date": pd.to_datetime(
                [
                    "2021-04-01 00:00:00",
                    "2021-04-01 01:00:00",
                    "2021-04-01 02:00:00",
                    "2021-04-01 00:00:00",
                    "2021-04-01 01:00:00",
                    "2021-04-01 02:00:00",
                ]
            ),
            "value": [3.0, 7.0, 1.0, -1.0, 100.0, 110.0],
        }
    )

    return metadata, metadata, data_10min, data_1h


@patch("paint.data.dwd_weather.DWDWeatherData._get_raw_data")
def test_dwd_weather(
    mock_request: MagicMock,
    mock_data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame],
):
    """
    Test the DWD weather data script by downloading mock data and checking if the saved HDF5 is correct.

    Note, this test does not test the DWD Wetterdienst API. If breaking changes are made to this API then this test
    will not cover these changes.

    Parameters
    ----------
    mock_request : MagicMock
        The mock requests object.
    mock_data : Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        The mock data used instead of actual downloaded data.
    """
    # Set the return value for the mocked ``_get_raw_data`` function to our test data.
    mock_request.return_value = mock_data

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        file_name = "test_dwd_weather.h5"

        dwd_weather = DWDWeatherData(
            parameters_10min=[
                "radiation_global",
                "sunshine_duration",
            ],
            parameters_1h=[
                "cloud_cover_total",
                "weather",
            ],
            station_ids=["15000"],
            start_date="2021-04-01",
            end_date="2021-04-02",
            output_path=output_path,
            file_name=file_name,
        )
        dwd_weather.download_and_save_data()

        # Check the HDF5 file
        file_path = Path(output_path, file_name)
        assert os.path.exists(file_path)

        with h5py.File(file_path, "r") as file:
            # Select station
            station = file["15000"]

            # Check metadata
            assert station.attrs["latitude"] == 50.7983
            assert station.attrs["longitude"] == 6.0244
            assert station.attrs["height"] == 231.0
            assert station.attrs["name"] == "Aachen-Orsbach"
            assert station.attrs["state"] == "Nordrhein-Westfalen"

            # Check 10min data
            assert "global_radiation_10min" in station.keys()
            assert (
                station["global_radiation_10min"]["time"][:].astype(str)
                == [
                    "2021-04-01Z00:00:00Z",
                    "2021-04-01Z00:10:00Z",
                    "2021-04-01Z00:20:00Z",
                ]
            ).all()
            assert (
                station["global_radiation_10min"]["value"][:] == [0.0, 1.0, 2.0]
            ).all()
            assert "sunshine_duration_10min" in station.keys()
            assert (
                station["sunshine_duration_10min"]["time"][:].astype(str)
                == [
                    "2021-04-01Z00:00:00Z",
                    "2021-04-01Z00:10:00Z",
                    "2021-04-01Z00:20:00Z",
                ]
            ).all()
            assert (
                station["sunshine_duration_10min"]["value"][:] == [10.0, 11.0, 12.0]
            ).all()

            # Check 1h data
            assert "cloud_cover_1h" in station.keys()
            assert (
                station["cloud_cover_1h"]["time"][:].astype(str)
                == [
                    "2021-04-01Z00:00:00Z",
                    "2021-04-01Z01:00:00Z",
                    "2021-04-01Z02:00:00Z",
                ]
            ).all()
            assert (station["cloud_cover_1h"]["value"][:] == [3.0, 7.0, 1.0]).all()
            assert "weather_type_1h" in station.keys()
            assert (
                station["weather_type_1h"]["time"][:].astype(str)
                == [
                    "2021-04-01Z00:00:00Z",
                    "2021-04-01Z01:00:00Z",
                    "2021-04-01Z02:00:00Z",
                ]
            ).all()
            assert (
                station["weather_type_1h"]["value"][:] == [-1.0, 100.0, 110.0]
            ).all()


def test_raw_download():
    """Runs the raw download function to catch any errors in the request. No assertions are tested."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        file_name = "test_raw_downlaod.h5"

        dwd_weather = DWDWeatherData(
            parameters_10min=[
                "radiation_sky_short_wave_diffuse",
                "radiation_global",
            ],
            parameters_1h=[
                "cloud_cover_total",
                "humidity",
            ],
            station_ids=["15000"],
            start_date="2021-04-01",
            end_date="2021-05-01",
            output_path=output_path,
            file_name=file_name,
        )
        dwd_weather._get_raw_data()
