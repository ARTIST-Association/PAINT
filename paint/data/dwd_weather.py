import argparse
import pathlib
from typing import List, Tuple

import h5py
import pandas as pd
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest

from paint import PAINT_ROOT
from paint.data.dwd_mappings import dwd_parameter_mapping


class DWDWeatherData:
    """
    Download and save DWD Weather data in a HDF5 file.

    This class enables DWD weather data to be downloaded in either a 10-minute or 1-hour resolution from selected
    weather stations. The data is then saved as an HDF5 file, either grouped by resolution or by parameter.
    """

    def __init__(
        self,
        parameters_10min: List[str],
        parameters_1h: List[str],
        station_ids: List[str],
        start_date: str,
        end_date: str,
        output_path: str,
        file_name: str = "dwd_weather.h5",
        ts_shape: str = "long",
        ts_humanize: bool = True,
        ts_si_units: bool = False,
    ) -> None:
        """
        Initialize the DWD weather data object.

        Parameters
        ----------
        parameters_10min : list of str
            The parameters to be downloaded in a 10min temporal resolution.
        parameters_1h : list of str
            The parameters to be downloaded in a 1h temporal resolution.
        station_ids : list of str
            The station IDs to be considered when downloading data.
        start_date : str
            The start date of the downloaded data.
        end_date : str
            The end date of the downloaded data.
        output_path : str
            The path to save the downloaded data.
        file_name : str
            The name of the downloaded data (Default: "dwd_weather").
        ts_shape : str
            A string indicating how the time series shape should be handled in the ``wetterdienst`` package (Default:
            ``long``).
        ts_humanize : bool
            A boolean indicating whether the time series should be humanized or not within the ``wetterdienst``
            package (Default:``True``).
        ts_si_units : bool
            A boolean indicating whether the time series units should be converted to SI units within the
             ``wetterdienst`` package (Default:``False``).
        """
        self.parameters_10min = parameters_10min
        self.parameters_1h = parameters_1h
        self.station_ids = station_ids
        self.start_date = start_date
        self.end_date = end_date
        self.output_path = pathlib.Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        self.file_name = file_name
        self.settings = Settings(
            ts_shape=ts_shape, ts_humanize=ts_humanize, ts_si_units=ts_si_units
        )

    def _get_raw_data(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Download the raw data using the DWD Wetterdienst pacakge.

        Returns
        -------
        pd.DataFrame
            The metadata for each weather station included in the 10min temporal resolution data request.
        pd.DataFrame
            The metadata for each weather station included in the 1h temporal resolution data request.
        pd.DataFrame
            The data for the weather variables downloaded in 10min temporal resolution.
        pd.DataFrame
            The data for the weather variables downloaded in 1h temporal resolution.
        """
        request_10min = DwdObservationRequest(
            parameter=self.parameters_10min,
            resolution="Minute_10",
            start_date=self.start_date,
            end_date=self.end_date,
            settings=self.settings,
        ).filter_by_station_id(station_id=self.station_ids)
        request_1h = DwdObservationRequest(
            parameter=self.parameters_1h,
            resolution="hourly",
            start_date=self.start_date,
            end_date=self.end_date,
            settings=self.settings,
        ).filter_by_station_id(station_id=self.station_ids)

        return (
            request_10min.df.to_pandas(),
            request_1h.df.to_pandas(),
            request_10min.values.all().df.to_pandas(),
            request_1h.values.all().df.to_pandas(),
        )

    def download_and_save_data(self) -> None:
        """Download the desired DWD weather data and save it to an HDF5 file."""
        # Download the data.
        metadata_10min, metadata_1h, df_10min, df_1h = self._get_raw_data()

        assert metadata_10min.shape == metadata_1h.shape, (
            "Data is not available for all stations at the given temporal resolutions. Please check the coverage of "
            "different parameters and temporal resolutions here: "
            "https://wetterdienst.readthedocs.io/en/latest/data/coverage/dwd/observation.html"
        )

        # Create HDF5 file.
        with h5py.File(self.output_path / self.file_name, "w") as file:
            # Include metadata for each station included in the download
            for station_id in self.station_ids:
                file.create_group(station_id)
                file[station_id].attrs["latitude"] = metadata_1h[
                    metadata_1h.station_id == station_id
                ].latitude.values[0]
                file[station_id].attrs["longitude"] = metadata_1h[
                    metadata_1h.station_id == station_id
                ].longitude.values[0]
                file[station_id].attrs["height"] = metadata_1h[
                    metadata_1h.station_id == station_id
                ].height.values[0]
                file[station_id].attrs["name"] = metadata_1h[
                    metadata_1h.station_id == station_id
                ].name.values[0]
                file[station_id].attrs["state"] = metadata_1h[
                    metadata_1h.station_id == station_id
                ].state.values[0]

            # Include parameters at a 10min temporal resolution.
            grouped_10min = df_10min.groupby(["station_id", "parameter"])
            for (station_id, parameter), group in grouped_10min:
                file[
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_10min/time"
                ] = group.date.dt.strftime("%Y-%m-%d %H:%M:%S").to_numpy(
                    dtype=h5py.string_dtype(encoding="utf-8")
                )
                file[
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_10min/value"
                ] = group.value.to_numpy()

            # Include parameters at a 1h temporal resolution.
            grouped_1h = df_1h.groupby(["station_id", "parameter"])
            for (station_id, parameter), group in grouped_1h:
                file[
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_1h/time"
                ] = group.date.dt.strftime("%Y-%m-%d %H:%M:%S").to_numpy(
                    dtype=h5py.string_dtype(encoding="utf-8")
                )
                file[
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_1h/value"
                ] = group.value.to_numpy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parameters_10min",
        default=[
            "radiation_sky_short_wave_diffuse",
            "radiation_global",
            "sunshine_duration",
            "radiation_sky_long_wave",
        ],
    )
    parser.add_argument(
        "--parameters_1h",
        default=[
            "cloud_cover_total",
            "humidity",
            "pressure_vapor",
            "visibility_range",
            "weather",
        ],
    )
    parser.add_argument("--station_ids", default=["15000"])
    parser.add_argument("--start_date", type=str, default="2021-04-01")
    parser.add_argument("--end_date", type=str, default="2024-03-01")
    parser.add_argument("--output_path", type=str, default=f"{PAINT_ROOT}/DWD_data/")
    parser.add_argument("--file_name", type=str, default="dwd_weather.h5")
    parser.add_argument("--ts_shape", type=str, default="long")
    parser.add_argument("--ts_humanize", action="store_true", default=True)
    parser.add_argument("--ts_si_units", action="store_false", default=False)
    args = parser.parse_args()
    dwd_weather = DWDWeatherData(
        parameters_10min=args.parameters_10min,
        parameters_1h=args.parameters_1h,
        station_ids=args.station_ids,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=args.output_path,
        ts_shape=args.ts_shape,
        ts_humanize=args.ts_humanize,
        ts_si_units=args.ts_si_units,
    )
    dwd_weather.download_and_save_data()
