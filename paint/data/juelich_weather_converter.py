from pathlib import Path

import h5py
import pandas as pd

import paint.data.juelich_weather_mappings as juelich_mappings
import paint.util.paint_mappings as mappings


class JuelichWeatherConverter:
    """
    Merge the Juelich weather data and save it as an HDF5 file.

    Attributes
    ----------
    input_root_dir : Path
        The root directory to being the search for weather files.
    output_path : Path
        The output path to save the HDF5 file.
    file_name : str
        The file name used to save the HDF5 file.
    files_list: list[str]
        The list of files to be concatenated.
    compression_opts : dict[str, Any]
        The compression options for compressing the HDF5 file.

    Methods
    -------
    find_weather_files()
        Find all weather files in a given directory.
    concatenate_weather()
        Concatenates the weather files.
    merge_and_save_to_hdf5()
        Merges the weather files and save the merged data to HDF5.
    """

    def __init__(
        self,
        input_root_dir: str,
        output_path: str,
        file_name: str,
        compression_method: str = "gzip",
        compression_level: int = 5,
    ) -> None:
        """
        Initialize the weather converter.

        Parameters
        ----------
        input_root_dir : str
            The root directory to search for weather files.
        output_path : str
            The output path to save the HDF5 file.
        file_name : str
            The file name used to save the HDF5 file.
        compression_method : str
            The method used to compress the HDF5 file.
        compression_level : int
            The compression level.
        """
        self.input_root_dir = Path(input_root_dir)
        self.output_path = Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        self.file_name = file_name
        self.files_list = self.find_weather_files()
        self.compression_opts = {
            "compression": compression_method,
            "compression_opts": compression_level,
        }

    def find_weather_files(self) -> list[str]:
        """
        Recursively find all weather.txt files in the directory.

        Returns
        -------
        list[str]
            The list of weather.txt files to be concatenated.
        """
        return [str(file) for file in self.input_root_dir.rglob("*.txt")]

    def concatenate_weather(self) -> pd.DataFrame:
        """
        Load all weather.txt files as a data frame and return the concatenated data frame.

        Returns
        -------
        pd.DataFrame
            The concatenated data frame.
        """
        df_list = []
        for file in self.files_list:
            # Read CSV.
            print(f"Attempting to read and clean {file}.")
            df = pd.read_csv(
                file,
                sep="\t",
                skiprows=[1],
                index_col=0,
                decimal=",",
            )
            # Remove NaNs.
            df = df[~df.index.isna()]
            if df.index.name != "Date":
                # Convert date and time.
                df["DateTime"] = pd.to_datetime(
                    df.index + " " + df["Date"], format="%d.%m.%Y %H:%M:%S"
                )
                df["DateTime"] = (
                    df["DateTime"]
                    .dt.tz_localize("Europe/Berlin", ambiguous="infer")
                    .dt.tz_convert("UTC")
                )
            else:
                # Convert date and time.
                df["DateTime"] = pd.to_datetime(
                    df.index + " " + df["Time"], format="%d.%m.%Y %H:%M:%S"
                )
                df["DateTime"] = (
                    df["DateTime"]
                    .dt.tz_localize(
                        "Europe/Berlin",
                        ambiguous="infer",
                    )
                    .dt.tz_convert("UTC")
                )

            # Clean data frame.
            df = df.drop(
                columns=[
                    "Date",
                    "Time",
                    "TriggerBarometer",
                    "Fuse1",
                    "Fuse2",
                    "Fuse3",
                    "Fuse4",
                    "Fuse5",
                    "Fuse6",
                    "Fuse7",
                    "Fuse9",
                    "UPS",
                    "OvervoltageProtection",
                    "Lnet",
                    "Tb",
                    "Ld",
                    "Direktunnormiert",
                    "Globalunnormiert",
                    "Diffusunnormiert",
                    "Direkttempfaktor",
                    "Globaltempfaktor",
                    "Diffustempfaktor",
                    "Gloabalwinkelfaktor",
                    "Diffuswinkelfaktor",
                    "Azimuth",
                    "Elevation",
                    "DNI Korr Norm",
                ],
                errors="ignore",
            )
            df.index = df["DateTime"].dt.strftime(mappings.TIME_FORMAT)
            df = df.drop(columns="DateTime")
            df_list.append(df)
        # Append all data frames.
        full_df = pd.concat(df_list)
        print("All files concatenated!")
        return full_df.sort_index()

    def merge_and_save_to_hdf5(self) -> pd.Series:
        """
        Merge the weather files and save the merged data to HDF5.

        Returns
        -------
        pd.Series
         The metadata for the merged data frame to be used for STAC creation.
        """
        full_weather_df = self.concatenate_weather()

        metadata = pd.Series(
            {
                mappings.JUELICH_START: full_weather_df.index.min(),
                mappings.JUELICH_END: full_weather_df.index.max(),
            }
        )

        # Ccreate HDF5 file.
        with h5py.File(self.output_path / self.file_name, "w") as file:
            # Save the time data.
            file.create_dataset(
                "time", data=full_weather_df.index.to_numpy(), **self.compression_opts
            )

            # Save each column with compression.
            for column in full_weather_df.columns:
                parameter_name = juelich_mappings.juelich_weather_parameter_mapping[
                    column
                ]
                file.create_dataset(
                    parameter_name,
                    data=full_weather_df[column].to_numpy(),
                    **self.compression_opts,
                )
                file[parameter_name].attrs[
                    juelich_mappings.DESCRIPTION
                ] = juelich_mappings.juelich_metadata_description[parameter_name]
                file[parameter_name].attrs[
                    juelich_mappings.UNITS
                ] = juelich_mappings.juelich_metadata_units[parameter_name]

        return metadata