import logging
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Union

import pandas as pd
import pystac
import requests
from tqdm import tqdm

import paint.util.paint_mappings as mappings

log = logging.getLogger(__name__)  # Logger for the STAC client
"""A logger for the STAC client."""


class StacClient:
    """
    Client to browse STAC files and download data.

    Attributes
    ----------
    output_dir : pathlib.Path
        Output directory for saving the downloaded data.
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
    get_heliostat_data()
        Get data for one or more heliostats.
    get_weather_data()
        Get weather data from DWD and/or Jülich.
    get_tower_measurements()
        Get the tower measurements data.
    get_heliostat_metadata()
        Download metadata for desired heliostats.
    get_single_calibration_item_by_id()
        Get a single calibration item given an item ID.
    get_multiple_calibration_items_by_id()
        Get multiple calibration items given a dictionary of heliostat IDs and calibration IDs.
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
            Output directory for saving the downloaded data.
        chunk_size : int
            Chunk size used for download (Default: 1024 * 1024).
        """
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size

    @staticmethod
    def get_catalog(href: str) -> pystac.catalog.Catalog:
        """
        Help to load a STAC catalog.

        Since PySTAC does not check if the URL exists before attempting to download a catalog, we catch any errors raised
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
                    f"The desired catalog with the URL '{href}' does not exist (404 error)!"
                )
            else:
                # Raise the original exception for all other errors.
                raise

    @staticmethod
    def get_child(
        parent: Union[pystac.catalog.Catalog, pystac.collection.Collection],
        child_id: str,
    ) -> Union[pystac.catalog.Catalog, pystac.collection.Collection, pystac.item.Item]:
        """
        Help to get a child from a STAC catalog or collection.

        Since PySTAC returns ``None`` if a child is not present, it is important we log a warning if this is the case.

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
                f"The child with ID {child_id} is not available, data for this child cannot be accessed."
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
        # Send an HTTP GET request to the specified url to retrieve the file.
        # Download the file in chunks (`stream=True`) instead of loading the entire file into memory.
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            # Open the file in binary write mode and download the content.
            with open(file_name, "wb") as file:
                downloaded_length = 0
                # Iterate over chunks of data in the response and write each chunk of data to file until the download
                # is complete.
                for data in response.iter_content(chunk_size=self.chunk_size):
                    file.write(data)
                    downloaded_length += len(data)
        except requests.RequestException as e:
            log.error(f"Failed to download the file from {url}. Error: {e}")
        except IOError as e:
            log.error(f"File operation failed for {file_name}. Error: {e}")

    def _process_single_heliostat_item(
        self,
        item: pystac.item.Item,
        start_date: Union[datetime, None],
        end_date: Union[datetime, None],
        filtered_calibration_keys: Union[list[str], None],
        collection_id: str,
        heliostat_catalog_id: str,
        save_folder: str,
        pbar: tqdm,
        for_dataset: bool = False,
    ) -> None:
        """
        Process a single heliostat item.

        Parameters
        ----------
        item : pystac.item.Item
            Item to be processed.
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default: ``None``).
        end_date : datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default: ``None``).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        collection_id : str
            ID of the collection to download.
        heliostat_catalog_id : str
            ID of the considered heliostat catalog.
        save_folder : str
            Name of the folder to save the collection items in.
        pbar : tqdm
            Progress bar.
        for_dataset : bool
            Whether to save all items in one folder for a dataset (Default: ``False``).
        """
        item_time = item.properties["datetime"]
        if start_date and end_date:
            # If start and end dates are provided, filter based on them.
            if not (
                start_date
                <= datetime.strptime(item_time, mappings.TIME_FORMAT)
                <= end_date
            ):
                log.debug(f"No data found between {start_date} and {end_date}!")
                pbar.update(1)
                return

        if (
            filtered_calibration_keys is not None
            and mappings.SAVE_CALIBRATION.lower() in collection_id.split("-")
        ):
            # Only process the calibration keys if provided.
            for key, asset in item.assets.items():
                if key in filtered_calibration_keys:
                    self._download_heliostat_asset(
                        asset, heliostat_catalog_id, save_folder, for_dataset
                    )
        else:
            # Process all assets in the item.
            for asset in item.assets.values():
                self._download_heliostat_asset(
                    asset, heliostat_catalog_id, save_folder, for_dataset
                )
        pbar.update(1)

    def _process_heliostat_items(
        self,
        items: list[pystac.item.Item],
        start_date: Union[datetime, None],
        end_date: Union[datetime, None],
        filtered_calibration_keys: Union[list[str], None],
        collection_id: str,
        heliostat_catalog_id: str,
        save_folder: str,
        for_dataset: bool = False,
    ) -> None:
        """
        Process and download items, either with or without date filtering and calibration key filtering.

        Parameters
        ----------
        items : list[pystac.item.Item]
            List of items to be processed.
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default: ``None``).
        end_date : datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default: ``None``).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        collection_id : str
            ID of the collection to download.
        heliostat_catalog_id : str
            ID of the considered heliostat catalog.
        save_folder : str
            Name of the folder to save the collection items in.
        for_dataset : bool
            Whether to save all items in one folder for a dataset (Default: ``False``).
        """
        with tqdm(
            total=len(items),
            desc=f"Processing Items in Heliostat {heliostat_catalog_id}",
            unit="Item",
        ) as pbar:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        self._process_single_heliostat_item,
                        item,
                        start_date,
                        end_date,
                        filtered_calibration_keys,
                        collection_id,
                        heliostat_catalog_id,
                        save_folder,
                        pbar,
                        for_dataset,
                    )
                    for item in items
                ]

            for future in as_completed(futures):
                try:
                    future.result()  # Wait for each future to complete
                except Exception as e:
                    log.error(f"Error processing heliostat item: {e}")

    def _download_heliostat_asset(
        self,
        asset: pystac.asset.Asset,
        heliostat_catalog_id: str,
        save_folder: str,
        for_dataset: bool = False,
    ) -> None:
        """
        Download the asset from the provided URL and save it to the selected location.

        Parameters
        ----------
        asset : pystac.asset.Asset
            STAC asset to be downloaded and saved.
        heliostat_catalog_id : str
            ID of the considered heliostat catalog.
        save_folder : str
            Name of the folder to save the asset in.
        for_dataset : bool
            Whether to save all items in one folder for a dataset (Default: ``False``).
        """
        url = asset.href
        file_end = url.split("/")[-1]
        if for_dataset:
            file_name = self.output_dir / file_end
        else:
            file_name = (
                self.output_dir
                / heliostat_catalog_id.split("-")[0]
                / save_folder
                / file_end
            )
        file_name.parent.mkdir(parents=True, exist_ok=True)
        self.download_file(url, file_name)

    def _download_heliostat_data(
        self,
        heliostat_catalog: pystac.catalog.Catalog,
        collection_id: str,
        save_folder: str,
        start_date: Union[datetime, None] = None,
        end_date: Union[datetime, None] = None,
        filtered_calibration_keys: Union[list[str], None] = None,
        for_dataset: bool = False,
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
            is downloaded (Default: ``None``).
        end_date : datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default: ``None``).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        for_dataset : bool
            Whether to save all items in one folder for a dataset (Default: ``False``).
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
        self._process_heliostat_items(
            list(items),
            start_date,
            end_date,
            filtered_calibration_keys,
            collection_id,
            heliostat_catalog.id,
            save_folder,
            for_dataset,
        )

    @staticmethod
    def _check_collection_keys(collections: list[str]) -> None:
        """
        Check whether provided collection keys are valid.

        Parameters
        ----------
        collections : list[str]
            Collection(s) for which (meta)data should be downloaded.

        Raises
        ------
        ValueError
            When a listed collection value is invalid.
        """
        allowed_values = {
            mappings.SAVE_DEFLECTOMETRY.lower(),
            mappings.SAVE_CALIBRATION.lower(),
            mappings.SAVE_PROPERTIES.lower(),
        }
        for item in collections:
            if item not in allowed_values:
                raise ValueError(
                    f"The heliostat collection must be one of: `deflectometry`, `calibration`, "
                    f"`properties`! The key `{item}` is not accepted!"
                )

    def get_heliostat_data(
        self,
        heliostats: Union[list[str], None] = None,
        collections: Union[list[str], None] = None,
        start_date: Union[datetime, None] = None,
        end_date: Union[datetime, None] = None,
        filtered_calibration_keys: Union[list[str], None] = None,
        for_dataset: bool = False,
    ) -> None:
        """
        Download data for one or more heliostats.

        Parameters
        ----------
        heliostats : list[str], optional
            Optional list of heliostats whose data should be downloaded, if `None` data for all heliostats is
            downloaded (Default: ``None``).
        collections : list[str], optional
            List of collections to be downloaded. These collections must be one of: ``calibration``, ``deflectometry``,
            ``properties``. If no list is provided, all collections are downloaded (Default: ``None``).
        start_date : datetime, optional
            Optional start date to filter the heliostat data. If no start date is provided, data for all time periods
            is downloaded (Default: ``None``).
        end_date : datetime, optional
            Optional end date to filter the heliostat data. If no end date is provided, data for all time periods
            is downloaded (Default: ``None``).
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        for_dataset : bool
            Whether to save all items in one folder for a dataset (Default: ``False``).
        """
        # Check if keys provided to the filtered_calibration_key dictionary are acceptable.
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

        # Log warning if no collection keys provided.
        if collections is None:
            log.warning(
                "No collections selected - downloading data for all collections!"
            )
            get_calibration = True
            get_deflectometry = True
            get_properties = True
        # Check if collection keys provided are acceptable.
        else:
            self._check_collection_keys(collections)
            # Set boolean flags based on the presence of each allowed value in collections.
            get_calibration = mappings.SAVE_CALIBRATION.lower() in collections
            get_deflectometry = mappings.SAVE_DEFLECTOMETRY.lower() in collections
            get_properties = mappings.SAVE_PROPERTIES.lower() in collections

        # Log warning if no filtered calibration keys provided.
        if get_calibration and filtered_calibration_keys is None:
            log.warning(
                "No calibration filters provided - downloading all calibration data, i.e. raw, cropped, flux, centered"
                "flux, and calibration properties!"
            )
        # Check if keys provided to the `filtered_calibration_key` dictionary are acceptable.
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
                        f"The filtered calibration keys can only be one or more of: `raw_image`, `cropped_image`, "
                        f"`flux_image`, `flux_centered_image`, `calibration_properties`'! The key `{key}` is not "
                        f"accepted!"
                    )

        # Error if only a start or end date is provided, but not both.
        if (start_date and not end_date) or (end_date and not start_date):
            raise ValueError("Please provide both start date and end date, or neither.")
        if start_date and end_date and start_date > end_date:
            raise ValueError("The start date must be before the end date.")

        # Download the data for each heliostat.
        for heliostat_catalog in heliostat_catalogs_list:
            log.info(f"Processing heliostat catalog {heliostat_catalog.id}")

            # Download calibration data.
            if get_calibration:
                calibration_id = (
                    mappings.CALIBRATION_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                self._download_heliostat_data(
                    heliostat_catalog,
                    calibration_id,
                    mappings.SAVE_CALIBRATION,
                    start_date,
                    end_date,
                    filtered_calibration_keys,
                    for_dataset,
                )

            # Download deflectometry data.
            if get_deflectometry:
                deflectometry_id = (
                    mappings.DEFLECTOMETRY_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                self._download_heliostat_data(
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
                self._download_heliostat_data(
                    heliostat_catalog,
                    properties_id,
                    mappings.SAVE_PROPERTIES,
                    start_date,
                    end_date,
                )

    def _download_weather_assets(
        self, weather_item: pystac.item.Item, include_juelich: bool, include_dwd: bool
    ) -> None:
        """
        Download weather assets for Jülich and/or DWD depending on flags.

        Parameters
        ----------
        weather_item : pystac.item.Item
            Weather item containing assets.
        include_juelich : bool
            Whether to include Jülich data.
        include_dwd : bool
            Whether to include DWD data.
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
            return  # If item does not match filters, skip.

        # Download the assets.
        for asset in weather_item.assets.values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / mappings.SAVE_WEATHER / file_end
            file_name.parent.mkdir(parents=True, exist_ok=True)
            self.download_file(url=url, file_name=file_name)

    def get_weather_data(
        self,
        data_sources: Union[list[str], None] = None,
        start_date: Union[datetime, None] = None,
        end_date: Union[datetime, None] = None,
    ) -> None:
        """
        Get weather data.

        Parameters
        ----------
        data_sources : list[str], optional
            List of weather sources to include. Must be from: ``DWD``, ``Jülich``. If no source is provided, data from
            all sources is downloaded (Default: ``None``).
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
                        f"The weather source must be one of: `Jülich`, `DWD`! The key `{item}` is not accepted!"
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
            if start_date > end_date:
                raise ValueError("The start date must be before the end date.")
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
                    self._download_weather_assets(
                        weather_item, include_juelich, include_dwd
                    )
        # Handle error with start and end date.
        elif start_date or end_date:
            raise ValueError("Please provide both start date and end date, or neither.")
        else:
            log.info(f"{download_message} for all available times!")
            # Download the weather data.
            for weather_item in weather_collection.get_items():
                self._download_weather_assets(
                    weather_item, include_juelich, include_dwd
                )

    def get_tower_measurements(self) -> None:
        """Download tower measurements."""
        log.info("Downloading the tower measurements!")
        item = pystac.Item.from_file(href=mappings.TOWER_STAC_URL)
        for asset in item.get_assets().values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / file_end
            self.download_file(url=url, file_name=file_name)

    def _process_child_metadata(
        self,
        child: Union[
            pystac.catalog.Catalog, pystac.item.Item, pystac.collection.Collection
        ],
        base_id: str,
        data: list[Any],
        pbar: tqdm,
    ) -> None:
        """
        Extract metadata from children in a catalog.

        Parameters
        ----------
        child : Union[pystac.item.Item, pystac.collection.Collection, pystac.catalog.Catalog]
            Child used for metadata extraction.
        base_id : str
            Base ID used to define the heliostat collection being accessed.
        data : list[Any]
            Combined list to save all data.
        pbar : tqdm
            Progress bar.
        """
        # Skip non-heliostat catalogs.
        if (
            child.id == mappings.WEATHER_COLLECTION_ID
            or child.id == mappings.TOWER_FILE_NAME
        ):
            return

        # Load the collection.
        heliostat_collection = self.get_child(
            child,
            child_id=base_id % child.id.split("-")[0],
        )

        # Return `None` if the collection does not exist.
        if heliostat_collection is None:
            return

        # Collect data for each item.
        for item in heliostat_collection.get_items():
            # Metadata for calibration items is different.
            if (
                heliostat_collection.id.split("-")[1]
                == mappings.SAVE_CALIBRATION.lower()
            ):
                data.append(
                    {
                        mappings.HELIOSTAT_ID: child.id.split("-")[0],
                        mappings.AZIMUTH: item.properties.get("view:sun_azimuth"),
                        mappings.ELEVATION: item.properties.get("view:sun_elevation"),
                        f"{mappings.LOWER_LEFT}_{mappings.LATITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[0][0],
                        f"{mappings.LOWER_LEFT}_{mappings.LONGITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[0][1],
                        f"{mappings.LOWER_LEFT}_{mappings.ELEVATION}": item.geometry.get(
                            "coordinates"
                        )[0][2],
                        f"{mappings.UPPER_LEFT}_{mappings.LATITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[1][0],
                        f"{mappings.UPPER_LEFT}_{mappings.LONGITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[1][1],
                        f"{mappings.UPPER_LEFT}_{mappings.ELEVATION}": item.geometry.get(
                            "coordinates"
                        )[1][2],
                        f"{mappings.UPPER_RIGHT}_{mappings.LATITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[2][0],
                        f"{mappings.UPPER_RIGHT}_{mappings.LONGITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[2][1],
                        f"{mappings.UPPER_RIGHT}_{mappings.ELEVATION}": item.geometry.get(
                            "coordinates"
                        )[2][2],
                        f"{mappings.LOWER_RIGHT}_{mappings.LATITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[3][0],
                        f"{mappings.LOWER_RIGHT}_{mappings.LONGITUDE_KEY}": item.geometry.get(
                            "coordinates"
                        )[3][1],
                        f"{mappings.LOWER_RIGHT}_{mappings.ELEVATION}": item.geometry.get(
                            "coordinates"
                        )[3][2],
                        mappings.DATETIME: item.datetime,
                        "item_id": item.id,
                    }
                )
            # Metadata for properties and deflectometry items is identical.
            elif (
                heliostat_collection.id.split("-")[1]
                == mappings.SAVE_DEFLECTOMETRY.lower()
                or heliostat_collection.id.split("-")[2]
                == mappings.SAVE_PROPERTIES.lower()
            ):
                data.append(
                    {
                        mappings.HELIOSTAT_ID: child.id.split("-")[0],
                        mappings.LATITUDE_KEY: item.geometry.get("coordinates")[0],
                        mappings.LONGITUDE_KEY: item.geometry.get("coordinates")[1],
                        mappings.ELEVATION: item.geometry.get("coordinates")[2],
                        mappings.DATETIME: item.datetime,
                        "item_id": item.id,
                    }
                )
            else:
                raise ValueError(
                    f"The collection {heliostat_collection.id.split('-')[0]} is not valid"
                )
        pbar.update(1)

    def get_heliostat_metadata(
        self,
        heliostats: Union[list[str], None] = None,
        collections: Union[list[str], None] = None,
    ) -> None:
        """
        Download metadata for desired heliostats.

        Parameters
        ----------
        heliostats : list[str], optional
            Heliostats for which the metadata should be downloaded. If no list is provided, the metadata for all
            heliostats is downloaded (Default: ``None``).
        collections : list[str], optional
            Collection for which metadata should be downloaded. If no list is provided, the metadata for all
            collections is downloaded (Default: ``None``).
        """
        # Log warning if no collection keys provided.
        if collections is None:
            log.warning(
                "No collections selected - downloading data for all collections!"
            )
            collections = [
                mappings.SAVE_DEFLECTOMETRY.lower(),
                mappings.SAVE_CALIBRATION.lower(),
                mappings.SAVE_PROPERTIES.lower(),
            ]
        # Check if collection keys provided are acceptable.
        else:
            self._check_collection_keys(collections)
        if heliostats is None:
            save_description = "all_heliostats"
            root = self.get_catalog(href=mappings.CATALOGUE_URL)
            log.info("Loading all children in root catalog - please be patient!")
            all_children = list(
                root.get_children()
            )  # Convert generator to list to save time later.
        else:
            # Find the catalogs for each desired heliostat.
            log.info("Loading catalogs for desired heliostats.")
            all_children = [
                self.get_catalog(
                    href=mappings.HELIOSTAT_CATALOG_URL % (heliostat, heliostat)
                )
                for heliostat in heliostats
            ]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_description = f"selected_heliostats_{timestamp}"

        for collection in collections:
            log.info(f"Downloading metadata for the {collection} collection!")
            log.info(
                f"Generating metadata dataframe for {len(all_children)} heliostat catalogs!"
            )
            if len(all_children) > 200 and collection == "calibration":
                log.info(
                    "This process will take a while, so now would be a good time to grab a coffee!"
                )
            if collection == mappings.SAVE_CALIBRATION.lower():
                id_base = mappings.CALIBRATION_COLLECTION_ID
            elif collection == mappings.SAVE_DEFLECTOMETRY.lower():
                id_base = mappings.DEFLECTOMETRY_COLLECTION_ID
            elif collection == mappings.SAVE_PROPERTIES.lower():
                id_base = mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID
            else:
                raise ValueError(
                    f"Considered collection must be one of `{mappings.SAVE_DEFLECTOMETRY.lower()}, "
                    f"{mappings.SAVE_CALIBRATION.lower()}, {mappings.SAVE_PROPERTIES.lower()}`! The collection"
                    f"{collection} is not recognised!"
                )

            # Empty list to store metadata.
            data: list[Any] = []

            # Use tqdm to track progress.
            with tqdm(
                desc="Processing Heliostat Catalogs",
                unit=" catalog",
                total=len(all_children),
            ) as pbar:
                # Process children in parallel.
                with ThreadPoolExecutor() as executor:
                    executor.map(
                        lambda child: self._process_child_metadata(
                            child=child,
                            base_id=id_base,
                            data=data,
                            pbar=pbar,
                        ),
                        all_children,
                        chunksize=100,
                    )

            # Check that some data has been downloaded:
            if data:
                # Create DataFrame from collected data.
                metadata_df = pd.DataFrame(data).set_index("item_id")
                metadata_df.index.name = mappings.SAVE_ID_INDEX
                save_location = (
                    self.output_dir
                    / "metadata"
                    / f"{collection}_metadata_{save_description}.csv"
                )
                save_location.parent.mkdir(parents=True, exist_ok=True)
                metadata_df.to_csv(save_location)
            else:
                log.error(
                    f"There was no metadata available for {collection=} and heliostats \n {heliostats=}"
                )

    @staticmethod
    def _check_filtered_calibration_keys(
        filtered_calibration_keys: Union[list[str], None] = None,
    ) -> list[str]:
        """
        Check that the filtered calibration keys are acceptable.

        Parameters
        ----------
        filtered_calibration_keys : list[str], optional
            List of keys to filter the calibration data.

        Returns
        -------
        list[str]
            The accepted filtered calibration keys.

        Raises
        ------
        ValueError
            When invalid calibration keys are provided.
        """
        accepted_keys = [
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
        ]
        if filtered_calibration_keys is None:
            filtered_calibration_keys = accepted_keys
        else:
            for key in filtered_calibration_keys:
                if key not in accepted_keys:
                    raise ValueError(
                        f"The filtered calibration keys can only be one or more of: `raw_image`, `cropped_image`, "
                        f"`flux_image`, `flux_centered_image`, `calibration_properties`'! The key `{key}` is not "
                        f"accepted!"
                    )
        return filtered_calibration_keys

    def get_single_calibration_item_by_id(
        self,
        heliostat_id: str,
        item_id: int,
        filtered_calibration_keys: Union[list[str], None] = None,
        benchmark_split: Union[str, None] = None,
        pbar: Union[tqdm, None] = None,
        verbose: bool = True,
    ) -> None:
        """
        Download a specific calibration item from a specific heliostat given the calibration item ID.

        Parameters
        ----------
        heliostat_id : str
            ID of the considered heliostat.
        item_id : int
            ID of the item to be downloaded.
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        benchmark_split : str, optional
            Benchmark split that this item is being downloaded for. If ``None``, the heliostat
            will be downloaded according to the ``PAINT`` default structure (Default: ``None``).
        pbar : tqdm, optional
            Progress bar, optional (Default: ``None``).
        verbose : bool
            Whether log messages should be printed (Default: ``True``).
        """
        # Include error handling for invalid item ID.
        # This error function does not return a value error, but merely logs the error. This will enable code calling
        # this function mulitiple times to continue running if one incorrect ID is present.
        filtered_calibration_keys = self._check_filtered_calibration_keys(
            filtered_calibration_keys
        )
        try:
            href = mappings.CALIBRATION_ITEM_URL % (heliostat_id, item_id)
            item = pystac.Item.from_file(href=href)
        except pystac.STACError as e:
            if verbose:
                log.error(
                    f"Failed to load STAC item from {href}. Error: {e}\n"
                    "No data downloaded for item {item_id} from {heliostat_id}!"
                )
            return
        except Exception as e:
            if verbose:
                log.error(
                    f"Unexpected error while accessing STAC item: {e}\n"
                    f"No data downloaded for item {item_id} from {heliostat_id}!"
                )
            return
        if verbose:
            log.info(
                f"Downloading calibration item {item_id} for heliostat {heliostat_id}!"
            )
        for key, asset in item.assets.items():
            if key in filtered_calibration_keys:
                url = asset.href
                file_end = url.split("/")[-1]
                if benchmark_split is not None:
                    file_name = self.output_dir / benchmark_split / file_end
                else:
                    file_name = (
                        self.output_dir
                        / heliostat_id
                        / mappings.SAVE_CALIBRATION
                        / file_end
                    )
                file_name.parent.mkdir(parents=True, exist_ok=True)
                self.download_file(url, file_name)
        if pbar is not None:
            pbar.update(1)

    def get_multiple_calibration_items_by_id(
        self,
        heliostat_items_dict: dict[str, Union[list[int], None]],
        filtered_calibration_keys: Union[list[str], None] = None,
    ) -> None:
        """
        Download multiple calibration items for multiple heliostats.

        Parameters
        ----------
        heliostat_items_dict : dict[str, Union[list[int], None]]
            A dictionary mapping heliostat IDs to lists of item IDs to be downloaded. If the list of item IDs is ``None``,
            all items for that heliostat will be downloaded.
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        """
        filtered_calibration_keys = self._check_filtered_calibration_keys(
            filtered_calibration_keys
        )
        for heliostat_id, item_ids in heliostat_items_dict.items():
            if item_ids is None:
                log.info(
                    f"No specific calibration items provided for heliostat {heliostat_id}. Downloading all calibration "
                    f"items."
                )
                # Get the collection for the given heliostat.
                calibration_collection_href = mappings.CALIBRATION_COLLECTION_URL % (
                    heliostat_id,
                    heliostat_id,
                )
                calibration_collection = pystac.Collection.from_file(
                    href=calibration_collection_href
                )
                # Find all items in that heliostat and download each item.
                all_items = list(calibration_collection.get_items())
                with tqdm(
                    total=len(all_items),
                    desc=f"Downloading Calibration Items in {heliostat_id}",
                    unit="Item",
                ) as pbar:
                    with ThreadPoolExecutor() as executor:
                        # Create a list of future objects.
                        futures = [
                            executor.submit(
                                self.get_single_calibration_item_by_id,
                                heliostat_id=heliostat_id,
                                item_id=int(item.id),
                                filtered_calibration_keys=filtered_calibration_keys,
                                benchmark_split=None,
                                pbar=pbar,
                                verbose=False,
                            )
                            for item in all_items
                        ]
                        # Wait for all tasks to complete.
                        for future in as_completed(futures):
                            try:
                                future.result()
                            except Exception as e:
                                # Handle exceptions from individual tasks.
                                log.error(f"Error in thread execution: {e}")
            else:
                # Only download selected items.
                for item_id in item_ids:
                    self.get_single_calibration_item_by_id(
                        heliostat_id=heliostat_id,
                        item_id=item_id,
                        filtered_calibration_keys=filtered_calibration_keys,
                    )
