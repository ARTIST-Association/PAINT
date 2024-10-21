import logging
import pathlib
from datetime import datetime
from typing import Optional, Union

import pystac
import requests
from pystac import STACError

import paint.util.paint_mappings as mappings
from paint.util import set_logger_config

set_logger_config()
log = logging.getLogger(__name__)
"""A logger for the STAC client."""


class StacClient:
    """
    Client to browse STAC files and download data.

    Attributes
    ----------
    output_dir : pathlib.Path
        The output directory for saving the downloaded data.`
    chunk_size: int
        Chunk size used for download (Default: `1024 * 1024).

    Methods
    -------
    get_catalog()
        Help load a STAC catalog with correct error handling.
    get_child()
        Help load a STAC child with correct error handling.
    download_file()
        Download a file given a URL.
    download_heliostat_data()
        Download heliostat data for a specified STAC collection.
    get_heliostat_data()
        Get data for one or more heliostats.
    """

    def __init__(
        self,
        output_dir: Union[str, pathlib.Path],
        chunk_size: int = 1024 * 1024,
    ) -> None:
        """
        Initialize the STAC client.

        Parameters
        ----------
        output_dir : Union[str, pathlib.Path]
            The output directory for saving the downloaded data.`
        chunk_size: int
            Chunk size used for download (Default: `1024 * 1024).
        """
        self.output_dir = pathlib.Path(output_dir)
        if not self.output_dir.is_dir():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size

    @staticmethod
    def get_catalog(href: str) -> pystac.catalog.Catalog:
        """
        Help to load a STAC catalog.

        Since pystac does not check if the URL exists before attempting to download a catalog we catch any errors raised
        and raise a value error indicating that the desired catalog does not exist.

        Parameters
        ----------
        href : str
            URL reference to the catalog that should be accessed.

        Returns
        -------
        pystac.catalog.Catalog
            Catalog, if it exists.

        Raises
        ------
        ValueError
            If the URL does not exist.
        """
        try:
            return pystac.Catalog.from_file(href=href)
        except Exception as e:
            # Log the error message for inspection.
            error_message = str(e)
            # Handle the 404 error explicitly by checking the message content.
            if "404" in error_message or "Could not read uri" in error_message:
                raise ValueError(
                    f"The desired catalog with the URL '{href}' doesn't exist (404 error)!"
                )
            else:
                # Raise the original exception for all other errors
                raise

    @staticmethod
    def get_child(
        parent: Union[pystac.catalog.Catalog, pystac.collection.Collection],
        child_id: str,
    ) -> Union[pystac.catalog.Catalog, pystac.collection.Collection, pystac.item.Item]:
        """
        Help to get a child from a STAC catalog or collection.

        Since pystac returns `None` if a child is not present, it is important we check the return type and raise
        and error if the collection is not available.

        Parameters
        ----------
        parent : Union[pystac.Catalog, pystac.Collection]
            Parent STAC catalog or collection.
        child_id : str
            ID of the child STAC catalog, collection, or item.

        Returns
        -------
        Union[pystac.Catalog, pystac.Collection, pystac.Item]
            Child STAC catalog, collection, or item.

        Raises
        ------
        STACError
            If the child ID does not exist in the parent.
        """
        child = parent.get_child(child_id)
        if child is None:
            raise STACError(f"Child with ID '{child_id}' not found in {parent.id}.")
        return child

    def download_file(self, url: str, file_name: Union[str, pathlib.Path]) -> None:
        """
        Download a file.

        Parameters
        ----------
        url : str
            URL of the file to download.
        file_name : Union[str, pathlib.Path]
            File name to be saved.
        """
        response = requests.get(url, stream=True)

        # Open the file in binary write mode and download the content
        with open(file_name, "wb") as file:
            downloaded_length = 0
            for data in response.iter_content(chunk_size=self.chunk_size):
                file.write(data)
                downloaded_length += len(data)

    def download_heliostat_data(
        self,
        heliostat_catalog: pystac.catalog.Catalog,
        collection_id: str,
        save_folder: str,
        log_message: str,
    ) -> None:
        """
        Download items from a specified collection from a heliostat and save them to a designated path.

        Parameters
        ----------
        heliostat_catalog : pystac.catalog.Catalog
            Heliostat catalog STAC.
        collection_id : str
            ID of the collection to download.
        save_folder : str
            Name of the folder to save the collection items in.
        log_message : str
            Message to log during processing.
        """
        items = self.get_child(
            parent=heliostat_catalog, child_id=collection_id
        ).get_items()
        log.info(log_message)

        for item in items:
            log.info(f"Processing and downloading item {item.id}")
            for asset in item.assets.values():
                url = asset.href
                file_end = url.split("/")[-1]
                file_name = (
                    self.output_dir
                    / heliostat_catalog.id.split("-")[0]
                    / save_folder
                    / file_end
                )
                file_name.parent.mkdir(parents=True, exist_ok=True)
                self.download_file(url, file_name)

    def get_heliostat_data(
        self,
        heliostats: list[str],
        get_calibration: bool,
        get_deflectometry: bool,
        get_properties: bool,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filtered_calibration_keys: Optional[list[str]] = None,
    ):
        """
        Download data for one or more heliostats.

        Parameters
        ----------
        heliostats : list[str]
            A list of heliostats whose data should be downloaded.
        get_calibration : bool
            Indicate whether to download calibration data.
        get_deflectometry : bool
            Indicate whether to download deflectometry data.
        get_properties : bool
            Indicate whether to download properties data.
        start_date : datetime, optional
            Optional start date to filter the heliostat data.
        end_date :  datetime, optional
            Optional end date to filter the heliostat data.
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of:`raw, processed, properties`.
        """
        # Check if keys provided to the filtered_calibration_key dictionary are acceptable
        if filtered_calibration_keys is not None:
            accepted_keys = ["raw", "processed", "properties"]
            for key in filtered_calibration_keys:
                if key not in accepted_keys:
                    raise ValueError(
                        "The filtered calibration keys can only be one or more of: `raw, processed, properties`!"
                    )

        # Find the catalogs for each desired heliostat.
        heliostat_catalogs_list = [
            self.get_catalog(
                href=mappings.HELIOSTAT_CATALOG_URL % (heliostat, heliostat)
            )
            for heliostat in heliostats
        ]

        # TODO: Include time filtering as with the weather - make sure to log an error if both dates are not provided
        # TODO: Include specific filter for the calibration data - i.e. only the raw images or something similar.
        # Download the data for each heliostat.
        for heliostat_catalog in heliostat_catalogs_list:
            log.info(f"Processing heliostat catalog {heliostat_catalog.id}")

            # Download calibration data.
            if get_calibration:
                calibration_id = (
                    mappings.CALIBRATION_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                self.download_heliostat_data(
                    heliostat_catalog,
                    calibration_id,
                    mappings.SAVE_CALIBRATION,
                    f"Processing and downloading calibration items for heliostat {heliostat_catalog.id}",
                )

            # Download deflectometry data.
            if get_deflectometry:
                deflectometry_id = (
                    mappings.DEFLECTOMETRY_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                self.download_heliostat_data(
                    heliostat_catalog,
                    deflectometry_id,
                    mappings.SAVE_DEFLECTOMETRY,
                    f"Processing and downloading deflectometry items for heliostat {heliostat_catalog.id}",
                )

            # Download properties data.
            if get_properties:
                properties_id = (
                    mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                self.download_heliostat_data(
                    heliostat_catalog,
                    properties_id,
                    mappings.SAVE_PROPERTIES,
                    f"Processing and downloading properties items for heliostat {heliostat_catalog.id}",
                )

    def download_weather_assets(
        self, weather_item, include_juelich: bool, include_dwd: bool
    ):
        """
        Download weather assets for Jülich and/or DWD depending on flags.

        Parameters
        ----------
        weather_item : pystac.item.Item
            Weather item containing assets.
        include_juelich : bool
            Indicating whether to include Jülich data.
        include_dwd : bool
            Indicating whether to include DWD data.
        """
        if "juelich" in weather_item.id and include_juelich:
            log.info(
                f"Processing and downloading Jülich weather data item {weather_item.id}"
            )
        elif "dwd" in weather_item.id and include_dwd:
            log.info(
                f"Processing and downloading DWD weather data item {weather_item.id}"
            )
        else:
            return  # If item does not match filters, skip

        # Download the assets
        for asset in weather_item.assets.values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / mappings.SAVE_WEATHER / file_end
            file_name.parent.mkdir(parents=True, exist_ok=True)
            self.download_file(url=url, file_name=file_name)

    def get_weather_data(
        self,
        include_juelich: bool,
        include_dwd: bool,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        """
        Get weather data.

        Parameters
        ----------
        include_juelich : bool
            Indicating whether to include Jülich weather data.
        include_dwd : bool
            Indicating whether to include DWD weather data.
        start_date : datetime, optional
            Optional start date to filter the weather data.
        end_date : datetime, optional
            Optional end date to filter the weather data.
        """
        if not (include_juelich or include_dwd):
            raise ValueError(
                "You must download at least one of Jülich or DWD weather data!"
            )

        weather_collection = pystac.Collection.from_file(
            href=mappings.WEATHER_COLLECTION_URL
        )

        # Set up download message
        sources = []
        if include_juelich:
            sources.append("Jülich")
        if include_dwd:
            sources.append("DWD")
        download_message = f"Downloading {' and '.join(sources)} weather data"

        # Download only for a specific time period.
        if start_date and end_date:
            log.info(
                f"{download_message} between {start_date.strftime(mappings.TIME_FORMAT)} and "
                f"{end_date.strftime(mappings.TIME_FORMAT)}"
            )
            for weather_item in weather_collection.get_items():
                item_start_time = weather_item.properties["start_datetime"]
                item_end_time = weather_item.properties["end_datetime"]
                if (
                    datetime.strptime(item_start_time, mappings.TIME_FORMAT)
                    >= start_date
                    and datetime.strptime(item_end_time, mappings.TIME_FORMAT)
                    <= end_date
                ):
                    self.download_weather_assets(
                        weather_item, include_juelich, include_dwd
                    )
        # Handle error with start and end date.
        elif start_date or end_date:
            raise ValueError("Please provide both start date and end date, or neither.")
        else:
            log.info(f"{download_message} for all available times!")
            # Download the weather data.
            for weather_item in weather_collection.get_items():
                self.download_weather_assets(weather_item, include_juelich, include_dwd)

    def get_tower_measurements(self) -> None:
        """Download tower measurements."""
        log.info("Downloading the tower measurements!")
        item = pystac.Item.from_file(href=mappings.TOWER_STAC_URL)
        for asset in item.get_assets().values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / file_end
            self.download_file(url=url, file_name=file_name)
