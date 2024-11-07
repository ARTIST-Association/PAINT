import logging
import pathlib
from datetime import datetime
from typing import Optional, Union

import pystac
import requests

import paint.util.paint_mappings as mappings
from paint.util import set_logger_config

set_logger_config()
log = logging.getLogger(__name__)  # Logger for the STAC client


class StacClient:
    """
    Client to browse STAC files and download data.

    Attributes
    ----------
    output_dir : pathlib.Path
        The output directory for saving the downloaded data.
    chunk_size : int
        Chunk size used for download (Default: 1024 * 1024).

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
            The output directory for saving the downloaded data.
        chunk_size : int
            Chunk size used for download (Default: 1024 * 1024).
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

        Since pystac returns `None` if a child is not present, it is important we log a warning if this is the case.

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
        """
        child = parent.get_child(child_id)
        if child is None:
            log.warning(
                f"The child with ID {child_id} is not available, data for this child will not be downloaded."
            )
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

    def process_heliostat_items(
        self,
        items: list[pystac.item.Item],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filtered_calibration_keys: Optional[list[str]],
        collection_id: str,
        heliostat_catalog_id: str,
        save_folder: str,
    ) -> None:
        """
        Process and download items, either with or without date filtering and calibration key filtering.

        Parameters
        ----------
        items : list[pystac.item.Item]
            List of items to be processed.
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default is None).
        end_date :  datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default is None).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of:`raw_image, cropped_image,
            flux_image, flux_centered_image, calibration_properties`. If no list is provided, all calibration data is
            downloaded (Default is None).
        collection_id : str
            ID of the collection to download.
        heliostat_catalog_id : str
            The ID of the considered heliostat catalog.
        save_folder : str
            Name of the folder to save the collection items in.
        """
        for item in items:
            item_time = item.properties["datetime"]
            if start_date and end_date:
                # If start and end dates are provided, filter based on them
                if not (
                    start_date
                    <= datetime.strptime(item_time, mappings.TIME_FORMAT)
                    <= end_date
                ):
                    continue

            log.info(f"Processing and downloading item {item.id}")

            if (
                filtered_calibration_keys is not None
                and mappings.SAVE_CALIBRATION.lower() in collection_id.split("-")
            ):
                # Only process the calibration keys if provided
                for key, asset in item.assets.items():
                    if key in filtered_calibration_keys:
                        self.download_heliostat_asset(
                            asset, heliostat_catalog_id, save_folder
                        )
            else:
                # Process all assets in the item
                for asset in item.assets.values():
                    self.download_heliostat_asset(
                        asset, heliostat_catalog_id, save_folder
                    )

    def download_heliostat_asset(
        self, asset: pystac.asset.Asset, heliostat_catalog_id: str, save_folder: str
    ) -> None:
        """
        Download the asset from the provided URL and save it to the selected location.

        Parameters
        ----------
        asset : pystac.asset.Asset
            STAC asset to be downloaded and saved.
        heliostat_catalog_id : str
            The ID of the considered heliostat catalog.
        save_folder : str
            Name of the folder to save the asset in.
        """
        url = asset.href
        file_end = url.split("/")[-1]
        file_name = (
            self.output_dir
            / heliostat_catalog_id.split("-")[0]
            / save_folder
            / file_end
        )
        file_name.parent.mkdir(parents=True, exist_ok=True)
        self.download_file(url, file_name)

    def download_heliostat_data(
        self,
        heliostat_catalog: pystac.catalog.Catalog,
        collection_id: str,
        save_folder: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filtered_calibration_keys: Optional[list[str]] = None,
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
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default is None).
        end_date :  datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default is None).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of:`raw_image, cropped_image,
            flux_image, flux_centered_image, calibration_properties`. If no list is provided, all calibration data is
            downloaded (Default is None).
        """
        child = self.get_child(parent=heliostat_catalog, child_id=collection_id)
        if child is None:
            log.warning(
                f"No data downloaded for {collection_id} in {heliostat_catalog.id}!"
            )
            return

        items = child.get_items()

        # Log if data is filtered by date.
        if start_date and end_date:
            log.info(
                f"Downloading data between {start_date.strftime(mappings.TIME_FORMAT)} and {end_date.strftime(mappings.TIME_FORMAT)}"
            )

        # Call the helper function to process and download items.
        self.process_heliostat_items(
            items,
            start_date,
            end_date,
            filtered_calibration_keys,
            collection_id,
            heliostat_catalog.id,
            save_folder,
        )

    def get_heliostat_data(
        self,
        heliostats: Optional[list[str]] = None,
        collections: Optional[list[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filtered_calibration_keys: Optional[list[str]] = None,
    ):
        """
        Download data for one or more heliostats.

        Parameters
        ----------
        heliostats : list[str], optional
            An optional list of heliostats whose data should be downloaded, if `None` data for all heliostats is
            downloaded (Default is None).
        collections : list[str], optional
            List of collections to be downloaded. These collections must be one of: `calibration, deflectometry,
            properties`. If no list is provided, all collections are downloaded (Default is None).
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default is None).
        end_date :  datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default is None).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of:`raw_image, cropped_image,
            flux_image, flux_centered_image, calibration_properties`. If no list is provided, all calibration data is
            downloaded (Default is None).
        """
        # Check if keys provided to the filtered_calibration_key dictionary are acceptable
        if heliostats is None:
            log.warning(
                "No heliostats selected - downloading data for all heliostats! This may take a while..."
            )
            root = self.get_catalog(href=mappings.CATALOGUE_URL)
            heliostat_catalogs_list = list(root.get_children())
            for i in range(
                len(heliostat_catalogs_list) - 1, -1, -1
            ):  # Iterate backwards through the list.
                child = heliostat_catalogs_list[i]
                if (
                    child.id == mappings.WEATHER_COLLECTION_ID
                    or child.id == mappings.TOWER_FILE_NAME
                ):
                    heliostat_catalogs_list.pop(i)
        else:
            # Find the catalogs for each desired heliostat.
            log.info("Loading catalogs for desired heliostats. ")
            heliostat_catalogs_list = [
                self.get_catalog(
                    href=mappings.HELIOSTAT_CATALOG_URL % (heliostat, heliostat)
                )
                for heliostat in heliostats
            ]

        # Log warning if now collection keys provided.
        if collections is None:
            log.warning(
                "No collections selected - downloading data for all collections!"
            )
            get_calibration = True
            get_deflectometry = True
            get_properties = True
        # Check if collection keys provided are acceptable.
        else:
            allowed_values = {
                mappings.SAVE_DEFLECTOMETRY.lower(),
                mappings.SAVE_CALIBRATION.lower(),
                mappings.SAVE_PROPERTIES.lower(),
            }
            for item in collections:
                if item not in allowed_values:
                    raise ValueError(
                        f"The heliostat collection must be one of: `deflectometry, calibration, "
                        f"properties`! The key {item} is not accepted!"
                    )
            # Set boolean flags based on the presence of each allowed value in collections.
            get_calibration = mappings.SAVE_CALIBRATION.lower() in collections
            get_deflectometry = mappings.SAVE_DEFLECTOMETRY.lower() in collections
            get_properties = mappings.SAVE_PROPERTIES.lower() in collections

        # Log warning if now filtered calibration keys provided.
        if get_calibration and filtered_calibration_keys is None:
            log.warning(
                "No calibration filters provided - downloading all calibration data, i.e. raw, cropped, flux, centered"
                "flux and calibration properties!"
            )
        # Check if keys provided to the filtered_calibration_key dictionary are acceptable
        elif get_calibration and filtered_calibration_keys is not None:
            accepted_keys = [
                mappings.CALIBRATION_RAW_IMAGE_KEY,
                mappings.CALIBRATION_CROPPED_IMAGE_KEY,
                mappings.CALIBRATION_FLUX_IMAGE_KEY,
                mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
                mappings.CALIBRATION_PROPERTIES_KEY,
            ]
            for key in filtered_calibration_keys:
                if key not in accepted_keys:
                    raise ValueError(
                        f"The filtered calibration keys can only be one or more of: `raw_image, cropped_image, "
                        f"flux_image, flux_centered_image, calibration_properties'! The key {key} is not accepted!"
                    )

        # Error if only a start or end date is provided, but not both.
        if (start_date and not end_date) or (end_date and not start_date):
            raise ValueError("Please provide both start date and end date, or neither.")

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
                    start_date,
                    end_date,
                    filtered_calibration_keys,
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
                    start_date,
                    end_date,
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
                    start_date,
                    end_date,
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
        data_sources: Optional[list[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> None:
        """
        Get weather data.

        Parameters
        ----------
        data_sources : list[str], optional
            List of weather sources to include. Must be from: `DWD, Jülich`. If no source is provided data form all
            sources is downloaded (Default is None).
        start_date : datetime, optional
            Optional start date to filter the weather data.
        end_date : datetime, optional
            Optional end date to filter the weather data.
        """
        if data_sources is None:
            include_juelich = True
            include_dwd = True
            data_sources = ["Jülich", "DWD"]
        else:
            allowed_values = {"Jülich", "DWD"}
            for item in data_sources:
                if item not in allowed_values:
                    raise ValueError(
                        f"The weather source must be one of: `Jülich, DWD! The key {item} is not accepted!"
                    )
            # Set boolean flags based on the presence of each allowed value in collections.
            include_juelich = "Jülich" in data_sources
            include_dwd = "DWD" in data_sources

        weather_collection = pystac.Collection.from_file(
            href=mappings.WEATHER_COLLECTION_URL
        )

        assert isinstance(data_sources, list)
        download_message = f"Downloading {' and '.join(data_sources)} weather data"

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
