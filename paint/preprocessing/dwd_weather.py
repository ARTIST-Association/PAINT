import pathlib

import h5py
import pandas as pd
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest

from paint.preprocessing.dwd_mappings import dwd_parameter_mapping


class DWDWeatherData:
    """
    Download and save DWD weather preprocessing in a HDF5 file.

    This class enables DWD weather preprocessing to be downloaded in either a 10-minute or 1-hour resolution from selected
    weather stations. The preprocessing is then saved as an HDF5 file, either grouped by resolution or by parameter.

    Attributes
    ----------
    parameters_10min : list[str]
        The parameters to be downloaded in a 10min temporal resolution.
    parameters_1h : list[str]
        The parameters to be downloaded in a 1h temporal resolution.
    station_ids : list[str]
        The station IDs to be considered when downloading preprocessing.
    start_date : str
        The start date of the downloaded preprocessing.
    end_date : str
        The end date of the downloaded preprocessing.
    output_path : str
        The path to save the downloaded preprocessing.
    file_name : str
        The name of the downloaded preprocessing (Default: "dwd_weather").
    settings : Settings
        The settings required for downloading preprocessing.
    compression_opts : dict[str, Any]
        The compression options for compressing the HDF5 file.

    Methods
    -------
    download_and_save_data()
        Download and save DWD weather preprocessing.
    """

    def __init__(
        self,
        parameters_10min: list[str],
        parameters_1h: list[str],
        station_ids: list[str],
        start_date: str,
        end_date: str,
        output_path: str,
        file_name: str = "dwd-weather.h5",
        ts_shape: str = "long",
        ts_humanize: bool = True,
        ts_si_units: bool = False,
        compression_method: str = "gzip",
        compression_level: int = 5,
    ) -> None:
        """
        Initialize the DWD weather preprocessing object.

        Parameters
        ----------
        parameters_10min : list[str]
            The parameters to be downloaded in a 10min temporal resolution.
        parameters_1h : list[str]
            The parameters to be downloaded in a 1h temporal resolution.
        station_ids : list[str]
            The station IDs to be considered when downloading preprocessing.
        start_date : str
            The start date of the downloaded preprocessing.
        end_date : str
            The end date of the downloaded preprocessing.
        output_path : str
            The path to save the downloaded preprocessing.
        file_name : str
            The name of the downloaded preprocessing (Default: "dwd_weather").
        ts_shape : str
            A string indicating how the time series shape should be handled in the ``wetterdienst`` package (Default:
            ``long``).
        ts_humanize : bool
            A boolean indicating whether the time series should be humanized or not within the ``wetterdienst``
            package (Default:``True``).
        ts_si_units : bool
            A boolean indicating whether the time series units should be converted to SI units within the
             ``wetterdienst`` package (Default:``False``).
        compression_method : str
            The method used to compress the HDF5 file.
        compression_level : int
            The compression level.
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
        self.compression_opts = {
            "compression": compression_method,
            "compression_opts": compression_level,
        }

    def _get_raw_data(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Download the raw preprocessing using the DWD Wetterdienst pacakge.

        Returns
        -------
        pd.DataFrame
            The metadata for each weather station included in the 10min temporal resolution preprocessing request.
        pd.DataFrame
            The metadata for each weather station included in the 1h temporal resolution preprocessing request.
        pd.DataFrame
            The preprocessing for the weather variables downloaded in 10min temporal resolution.
        pd.DataFrame
            The preprocessing for the weather variables downloaded in 1h temporal resolution.
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

    def download_and_save_data(self) -> pd.DataFrame:
        """
        Download the desired DWD weather preprocessing and save it to an HDF5 file.

        Returns
        -------
        pd.Dataframe
            The metadata used for creating the STAC item.
        """
        # download the preprocessing
        metadata_10min, metadata_1h, df_10min, df_1h = self._get_raw_data()
        metadata_to_save = metadata_1h[
            ["station_id", "latitude", "longitude", "height", "name"]
        ]
        assert metadata_10min.shape == metadata_1h.shape, (
            "Data is not available for all stations at the given temporal resolutions. Please check the coverage of "
            "different parameters and temporal resolutions here: "
            "https://wetterdienst.readthedocs.io/en/latest/data/coverage/dwd/observation.html"
        )

        # Create the HDF5 file.
        with h5py.File(self.output_path / self.file_name, "w") as file:
            # Include metadata for each station included in the download.
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
                # Create dataset for time with compression.
                file.create_dataset(
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_10min/time",
                    data=group.date.dt.strftime("%Y-%m-%dZ%H:%M:%SZ").to_numpy(
                        dtype=h5py.string_dtype(encoding="utf-8")
                    ),
                    **self.compression_opts,
                )

                # Create dataset for value with compression.
                file.create_dataset(
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_10min/value",
                    data=group.value.to_numpy(),
                    **self.compression_opts,
                )

            # Include parameters at a 1h temporal resolution.
            grouped_1h = df_1h.groupby(["station_id", "parameter"])
            for (station_id, parameter), group in grouped_1h:
                # Create dataset for time with compression.
                file.create_dataset(
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_1h/time",
                    data=group.date.dt.strftime("%Y-%m-%dZ%H:%M:%SZ").to_numpy(
                        dtype=h5py.string_dtype(encoding="utf-8")
                    ),
                    **self.compression_opts,
                )

                # Create dataset for value with compression.
                file.create_dataset(
                    f"{station_id}/{dwd_parameter_mapping[parameter]}_1h/value",
                    data=group.value.to_numpy(),
                    **self.compression_opts,
                )
        return metadata_to_save
