import json
import logging
import pathlib
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock
from typing import Any

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
        output_dir: str | pathlib.Path,
        chunk_size: int = 1024 * 1024,
    ) -> None:
        """
        Initialize the STAC client.

        Parameters
        ----------
        output_dir : str | pathlib.Path
            Output directory for saving the downloaded data.
        chunk_size : int
            Chunk size used for download (Default: 1024 * 1024).
        """
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size

    @staticmethod
    def load_checkpoint(path: pathlib.Path) -> dict[str, Any]:
        """
        Load checkpoint to resume the download from the point it stopped.

        Parameters
        ----------
        path : pathlib.Path
            The path to the checkpoint.

        Returns
        -------
        dict[str, Any]
            The checkpoint data.
        """
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_checkpoint(path: pathlib.Path, data: dict[str, Any]) -> None:
        """
        Save data to the download checkpoint.

        Parameters
        ----------
        path : pathlib.Path
            The path to the checkpoint.
        data : dict[str, Any]
            The data to save in the checkpoint.
        """
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def mark_done(checkpoint_data: dict[str, Any], catalog_id: str) -> None:
        """
        Mark specific heliostat catalog as downloaded for the checkpoint.

        Parameters
        ----------
        checkpoint_data : dict[str, Any]
            The checkpoint data.
        catalog_id : str
            The catalog ID to be marked.
        """
        checkpoint_data[catalog_id][mappings.CHECKPOINT_DONE] = True

    @staticmethod
    def mark_metadata_done(
        checkpoint_data: dict[str, Any], heliostat_id: str, collection: str
    ) -> None:
        """
        Mark specific heliostat catalog as downloaded for the checkpoint.

        Parameters
        ----------
        checkpoint_data : dict[str, Any]
            The checkpoint data.
        heliostat_id : str
            The heliostat ID to be marked.
        collection : str
            The collection to be marked.
        """
        checkpoint_data[heliostat_id][f"{collection}_done"] = True

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
        parent: pystac.catalog.Catalog | pystac.collection.Collection,
        child_id: str,
    ) -> pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection:
        """
        Help to get a child from a STAC catalog or collection.

        Since PySTAC returns ``None`` if a child is not present, it is important we log a warning if this is the case.

        Parameters
        ----------
        parent : pystac.catalog.Catalog | pystac.collection.Collection
            Parent STAC catalog or collection.
        child_id : str
            ID of the child STAC catalog, collection, or item.

        Returns
        -------
        pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection
            Child STAC catalog, collection, or item.
        """
        child = parent.get_child(child_id)
        if child is None:
            log.warning(
                f"The child with ID {child_id} is not available, data for this child cannot be accessed."
            )
        return child

    def download_file(
        self, url: str, file_name: str | pathlib.Path, timeout: int = 60
    ) -> bool:
        """
        Download a file.

        Parameters
        ----------
        url : str
            URL of the file to download.
        file_name : str | pathlib.Path
            File name to be saved.
        timeout : int
            Timeout for downloading the file (Default: 60 seconds).

        Returns
        -------
        bool
            Whether the file was downloaded.
        """
        # Send an HTTP GET request to the specified url to retrieve the file.
        # Download the file in chunks (`stream=True`) instead of loading the entire file into memory.
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            # Open the file in binary write mode and download the content.
            with open(file_name, "wb") as file:
                downloaded_length = 0
                # Iterate over chunks of data in the response and write each chunk of data to file until the download
                # is complete.
                for data in response.iter_content(chunk_size=self.chunk_size):
                    file.write(data)
                    downloaded_length += len(data)
            return True
        except requests.RequestException as e:
            log.error(f"Failed to download the file from {url}. Error: {e}")
            return False
        except IOError as e:
            log.error(f"File operation failed for {file_name}. Error: {e}")
            return False

    def _process_single_heliostat_item(
        self,
        item: pystac.item.Item,
        start_date: datetime | None,
        end_date: datetime | None,
        filtered_calibration_keys: list[str] | None,
        collection_id: str,
        heliostat_catalog_id: str,
        save_folder: str,
        pbar: tqdm,
        for_dataset: bool = False,
        timeout: int = 60,
    ) -> bool:
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
        timeout : int
            Timeout for downloading the heliostat item (Default: 60 seconds).

        Returns
        -------
        bool
            Whether the heliostat item was downloaded successfully.
        """
        # Assume download will be successful
        success = True
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
                return False

        if (
            filtered_calibration_keys is not None
            and mappings.SAVE_CALIBRATION.lower() in collection_id.split("-")
        ):
            # Only process the calibration keys if provided.
            for key, asset in item.assets.items():
                if key in filtered_calibration_keys:
                    if not self._download_heliostat_asset(
                        asset,
                        heliostat_catalog_id,
                        save_folder,
                        for_dataset,
                        timeout=timeout,
                    ):
                        success = False
        else:
            # Process all assets in the item.
            for asset in item.assets.values():
                if not self._download_heliostat_asset(
                    asset,
                    heliostat_catalog_id,
                    save_folder,
                    for_dataset,
                    timeout=timeout,
                ):
                    success = False
        pbar.update(1)
        return success

    def _process_heliostat_items(
        self,
        items: list[pystac.item.Item],
        start_date: datetime | None,
        end_date: datetime | None,
        filtered_calibration_keys: list[str] | None,
        collection_id: str,
        heliostat_catalog_id: str,
        save_folder: str,
        for_dataset: bool = False,
        timeout: int = 60,
        num_parallel_workers: int = 10,
        results_timeout: int = 300,
    ) -> bool:
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
        timeout : int
            Timeout for downloading the heliostat item (Default: 60 seconds).
        num_parallel_workers : int
            Number of parallel workers for downloading heliostat data (Default: 10).
        results_timeout : int
            Timeout for collecting results from multiple threads (Default: 300 seconds).

        Returns
        -------
        bool
            Whether all heliostat items were downloaded successfully.
        """
        all_successful = True

        with tqdm(
            total=len(items),
            desc=f"Processing Items in Heliostat {heliostat_catalog_id}",
            unit="Item",
        ) as pbar:
            with ThreadPoolExecutor(max_workers=num_parallel_workers) as executor:
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
                        timeout,
                    )
                    for item in items
                ]

                for future in as_completed(futures):
                    try:
                        item_success = future.result(timeout=results_timeout)
                        if not item_success:
                            all_successful = False
                    except Exception as e:
                        log.error(f"Error processing heliostat item: {e}")
                        all_successful = False
        return all_successful

    def _download_heliostat_asset(
        self,
        asset: pystac.asset.Asset,
        heliostat_catalog_id: str,
        save_folder: str,
        for_dataset: bool = False,
        timeout: int = 60,
    ) -> bool:
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
        timeout : int
            Timeout for downloading assets (Default: 60 seconds).

        Returns
        -------
        bool
            Whether the asset was successfully downloaded.
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
        return self.download_file(url, file_name, timeout)

    def _download_heliostat_data(
        self,
        heliostat_catalog: pystac.catalog.Catalog,
        collection_id: str,
        save_folder: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        filtered_calibration_keys: list[str] | None = None,
        for_dataset: bool = False,
        timeout: int = 60,
        num_parallel_workers: int = 10,
        results_timeout: int = 300,
    ) -> bool:
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
        timeout : int
            Timeout for downloading heliostat data (Default: 60 seconds).
        num_parallel_workers : int
            Number of parallel workers for downloading heliostat data (Default: 10).
        results_timeout : int
            Timeout for collecting results from multiple threads (Default: 300 seconds).

        Returns
        -------
        bool
            Whether all heliostat items were downloaded successfully.
        """
        child = self.get_child(parent=heliostat_catalog, child_id=collection_id)
        if child is None:
            log.warning(
                f"No data downloaded for {collection_id} in {heliostat_catalog.id}!"
            )
            # In this case no data is to be found, so it should still be marked as done
            return True

        items = child.get_items()

        # Log if data is filtered by date.
        if start_date and end_date:
            log.info(
                f"Downloading data between {start_date.strftime(mappings.TIME_FORMAT)} and {end_date.strftime(mappings.TIME_FORMAT)}"
            )

        # Call the helper function to process and download items.
        return self._process_heliostat_items(
            list(items),
            start_date,
            end_date,
            filtered_calibration_keys,
            collection_id,
            heliostat_catalog.id,
            save_folder,
            for_dataset,
            timeout,
            num_parallel_workers,
            results_timeout,
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
        heliostats: list[str] | None = None,
        collections: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        filtered_calibration_keys: list[str] | None = None,
        for_dataset: bool = False,
        resume_download: bool = True,
        timeout: int = 60,
        num_parallel_workers: int = 10,
        results_timeout: int = 300,
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
        resume_download : bool
            Whether to use a checkpoint to resume downloading data in case it is interrupted (Default: ``True``).
        timeout : int
            Timeout for downloading heliostat data (Default: 60 seconds).
        num_parallel_workers : int
            Number of parallel workers for downloading heliostat data (Default: 10).
        results_timeout : int
            Timeout for collecting results from multiple threads (Default: 300 seconds).
        """
        # Define checkpoint data structure.
        checkpoint_data: dict[str, Any] = {}
        checkpoint_path = self.output_dir / mappings.CHECKPOINT_NAME
        # Check if checkpoint data exists when resuming download.
        if resume_download:
            checkpoint_data = self.load_checkpoint(checkpoint_path)

        # Load heliostats for first time setup or if the resume download flag is ``false``.
        if not checkpoint_data:
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

            if resume_download:
                checkpoint_data = {
                    cat.id: {
                        mappings.CHECKPOINT_HREF: cat.get_self_href(),
                        mappings.CHECKPOINT_DONE: False,
                    }
                    for cat in heliostat_catalogs_list
                }
                self.save_checkpoint(checkpoint_path, checkpoint_data)
        # Resume download.
        else:
            log.info("Resuming download from checkpoint!")
            heliostat_catalogs_list = [
                pystac.Catalog.from_file(entry[mappings.CHECKPOINT_HREF])
                for entry in checkpoint_data.values()
                if not entry[mappings.CHECKPOINT_DONE]
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
            success = False

            # Download calibration data.
            if get_calibration:
                calibration_id = (
                    mappings.CALIBRATION_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                success &= self._download_heliostat_data(
                    heliostat_catalog,
                    calibration_id,
                    mappings.SAVE_CALIBRATION,
                    start_date,
                    end_date,
                    filtered_calibration_keys,
                    for_dataset,
                    timeout=timeout,
                    num_parallel_workers=num_parallel_workers,
                    results_timeout=results_timeout,
                )

            # Download deflectometry data.
            if get_deflectometry:
                deflectometry_id = (
                    mappings.DEFLECTOMETRY_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                success &= self._download_heliostat_data(
                    heliostat_catalog,
                    deflectometry_id,
                    mappings.SAVE_DEFLECTOMETRY,
                    start_date,
                    end_date,
                    timeout=timeout,
                    num_parallel_workers=num_parallel_workers,
                    results_timeout=results_timeout,
                )

            # Download properties data.
            if get_properties:
                properties_id = (
                    mappings.HELIOSTAT_PROPERTIES_COLLECTION_ID
                    % heliostat_catalog.id.split("-")[0]
                )
                success &= self._download_heliostat_data(
                    heliostat_catalog,
                    properties_id,
                    mappings.SAVE_PROPERTIES,
                    start_date,
                    end_date,
                    timeout=timeout,
                    num_parallel_workers=num_parallel_workers,
                    results_timeout=results_timeout,
                )

            if resume_download:
                if success:
                    self.mark_done(checkpoint_data, catalog_id=heliostat_catalog.id)
                self.save_checkpoint(checkpoint_path, checkpoint_data)

        # Clean up checkpoint if all catalogs are done.
        if resume_download:
            all_done = all(
                entry[mappings.CHECKPOINT_DONE] for entry in checkpoint_data.values()
            )
            if all_done and checkpoint_path.exists():
                checkpoint_path.unlink()
                log.info("All downloads complete. Checkpoint file removed.")

    def _download_weather_assets(
        self,
        weather_item: pystac.item.Item,
        include_juelich: bool,
        include_dwd: bool,
        timeout: int = 60,
    ) -> bool:
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
        timeout : int
            Timeout for downloading assets (Default: 60 seconds).

        Returns
        -------
        bool
            Whether the download was successful.
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
            return True  # If item does not match filters, skip.

        all_successful = True

        # Download the assets.
        for asset in weather_item.assets.values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / mappings.SAVE_WEATHER / file_end
            file_name.parent.mkdir(parents=True, exist_ok=True)
            if not self.download_file(url=url, file_name=file_name, timeout=timeout):
                all_successful = False

        return all_successful

    def get_weather_data(
        self,
        data_sources: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        timeout: int = 60,
        resume_download: bool = True,
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
        timeout : int
            Timeout for downloading data (Default: 60 seconds).
        resume_download : bool
            Whether to use a checkpoint to resume downloading data in case it is interrupted (Default: ``True``).
        """
        checkpoint_path = (
            self.output_dir / mappings.SAVE_WEATHER / mappings.WEATHER_CHECKPOINT_NAME
        )
        all_successful = True
        checkpoint_data = set()
        if checkpoint_path.exists():
            with open(checkpoint_path, "r") as f:
                checkpoint_data = set(json.load(f))
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
                item_id = weather_item.id
                if resume_download:
                    if item_id in checkpoint_data:
                        log.info(
                            f"Skipping already downloaded item with the ID: {item_id}"
                        )
                        continue
                item_start_time = weather_item.properties["start_datetime"]
                item_end_time = weather_item.properties["end_datetime"]
                if (
                    datetime.strptime(item_start_time, mappings.TIME_FORMAT)
                    >= start_date
                    and datetime.strptime(item_end_time, mappings.TIME_FORMAT)
                    <= end_date
                ):
                    success = self._download_weather_assets(
                        weather_item,
                        include_juelich,
                        include_dwd,
                        timeout=timeout,
                    )
                    if resume_download:
                        if success:
                            checkpoint_data.add(item_id)
                        else:
                            all_successful = False
                        with open(checkpoint_path, "w") as f:
                            json.dump(list(checkpoint_data), f, indent=2)
        # Handle error with start and end date.
        elif start_date or end_date:
            raise ValueError("Please provide both start date and end date, or neither.")
        else:
            log.info(f"{download_message} for all available times!")
            # Download the weather data.
            for weather_item in weather_collection.get_items():
                item_id = weather_item.id
                if resume_download:
                    if item_id in checkpoint_data:
                        log.info(
                            f"Skipping already downloaded item with the ID: {item_id}"
                        )
                        continue
                success = self._download_weather_assets(
                    weather_item,
                    include_juelich,
                    include_dwd,
                    timeout=timeout,
                )
                if resume_download:
                    if success:
                        checkpoint_data.add(item_id)
                    else:
                        all_successful = False
                    with open(checkpoint_path, "w") as f:
                        json.dump(list(checkpoint_data), f, indent=2)
        if resume_download:
            if all_successful:
                checkpoint_path.unlink()
                log.info("Finished downloading all weather data, checkpoint removed.")
            else:
                log.warning(
                    "Some weather data failed to download; checkpoint retained for resume."
                )

    def get_tower_measurements(self, timeout: int = 60) -> None:
        """
        Download tower measurements.

        Parameters
        ----------
        timeout : int
            Timeout for downloading measurements.
        """
        log.info("Downloading the tower measurements!")
        item = pystac.Item.from_file(href=mappings.TOWER_STAC_URL)
        for asset in item.get_assets().values():
            url = asset.href
            file_end = asset.href.split("/")[-1]
            file_name = self.output_dir / file_end
            _ = self.download_file(url=url, file_name=file_name, timeout=timeout)

    def _process_child_metadata(
        self,
        child: pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection,
        base_id: str,
    ) -> list[dict[str, Any]]:
        """
        Extract metadata from a heliostat catalog child.

        Parameters
        ----------
        child : pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection
            Child catalog to extract metadata from.
        base_id : str
            Base ID used to define the heliostat collection being accessed.

        Returns
        -------
        list[dict]
            List of extracted metadata dictionaries.
        """
        # Skip non-heliostat catalogs
        if (
            child.id == mappings.WEATHER_COLLECTION_ID
            or child.id == mappings.TOWER_FILE_NAME
        ):
            return []

        heliostat_id = child.id.split("-")[0]

        # Try loading the actual collection (e.g., calibration, deflectometry, etc.)
        heliostat_collection = self.get_child(
            child,
            child_id=base_id % heliostat_id,
        )

        if heliostat_collection is None:
            return []

        extracted_data = []

        for item in heliostat_collection.get_items():
            # Calibration-specific metadata format
            if (
                heliostat_collection.id.split("-")[1]
                == mappings.SAVE_CALIBRATION.lower()
            ):
                coords = item.geometry.get("coordinates")

                extracted_data.append(
                    {
                        mappings.HELIOSTAT_ID: heliostat_id,
                        mappings.AZIMUTH: item.properties.get("view:sun_azimuth"),
                        mappings.ELEVATION: item.properties.get("view:sun_elevation"),
                        f"{mappings.LOWER_LEFT}_{mappings.LATITUDE_KEY}": coords[0][0],
                        f"{mappings.LOWER_LEFT}_{mappings.LONGITUDE_KEY}": coords[0][1],
                        f"{mappings.LOWER_LEFT}_{mappings.ELEVATION}": coords[0][2],
                        f"{mappings.UPPER_LEFT}_{mappings.LATITUDE_KEY}": coords[1][0],
                        f"{mappings.UPPER_LEFT}_{mappings.LONGITUDE_KEY}": coords[1][1],
                        f"{mappings.UPPER_LEFT}_{mappings.ELEVATION}": coords[1][2],
                        f"{mappings.UPPER_RIGHT}_{mappings.LATITUDE_KEY}": coords[2][0],
                        f"{mappings.UPPER_RIGHT}_{mappings.LONGITUDE_KEY}": coords[2][
                            1
                        ],
                        f"{mappings.UPPER_RIGHT}_{mappings.ELEVATION}": coords[2][2],
                        f"{mappings.LOWER_RIGHT}_{mappings.LATITUDE_KEY}": coords[3][0],
                        f"{mappings.LOWER_RIGHT}_{mappings.LONGITUDE_KEY}": coords[3][
                            1
                        ],
                        f"{mappings.LOWER_RIGHT}_{mappings.ELEVATION}": coords[3][2],
                        mappings.DATETIME: item.datetime,
                        "item_id": item.id,
                    }
                )

            # Deflectometry / Properties metadata format
            elif (
                heliostat_collection.id.split("-")[1]
                == mappings.SAVE_DEFLECTOMETRY.lower()
                or heliostat_collection.id.split("-")[2]
                == mappings.SAVE_PROPERTIES.lower()
            ):
                coords = item.geometry.get("coordinates")

                extracted_data.append(
                    {
                        mappings.HELIOSTAT_ID: heliostat_id,
                        mappings.LATITUDE_KEY: coords[0],
                        mappings.LONGITUDE_KEY: coords[1],
                        mappings.ELEVATION: coords[2],
                        mappings.DATETIME: item.datetime,
                        "item_id": item.id,
                    }
                )

            else:
                raise ValueError(
                    f"The collection {heliostat_collection.id} is not valid."
                )

        return extracted_data

    def _process_metadata_with_checkpoint(
        self,
        child: pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection,
        collection: str,
        id_base: str,
        checkpoint: dict[str, Any],
        checkpoint_path: pathlib.Path,
        checkpoint_lock: Lock,
        temp_dir: pathlib.Path,
        pbar: tqdm,
    ) -> bool:
        """
        Process metadata with checkpoint capabilities.

        Parameters
        ----------
        child : pystac.catalog.Catalog | pystac.item.Item | pystac.collection.Collection
            Child being processed.
        collection : str
            Collection being processed.
        checkpoint : dict[str, Any]
            The checkpoint data.
        checkpoint_path : pathlib.Path
            The checkpoint path.
        checkpoint_lock : Lock
            The checkpoint lock to avoid threading problems.
        temp_dir : pathlib.Path
            The path to a temporary directory used to save metadata before combining at the end.
        pbar : tqdm
            Progress bar.

        Returns
        -------
        bool
            Whether the metadata was successfully processed.
        """
        heliostat_id = child.id

        if checkpoint[heliostat_id].get(f"{collection}_done", False):
            log.info(f"Skipping {heliostat_id} (already done for {collection})")
            pbar.update(1)
            return True

        try:
            data = self._process_child_metadata(
                child=child,
                base_id=id_base,
            )

            if data:
                df = pd.DataFrame(data).set_index("item_id")
                df.index.name = mappings.SAVE_ID_INDEX
                out_file = temp_dir / f"{heliostat_id}.csv"
                df.to_csv(out_file)

            with checkpoint_lock:
                self.mark_metadata_done(checkpoint, heliostat_id, collection)
                self.save_checkpoint(checkpoint_path, checkpoint)
                return True

        except Exception as e:
            log.error(f"Error processing {heliostat_id}: {e}")
            return False
        finally:
            pbar.update(1)

    def get_heliostat_metadata(
        self,
        heliostats: list[str] | None = None,
        collections: list[str] | None = None,
        resume_download: bool = True,
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
        resume_download : bool
            Whether to use a checkpoint to resume downloading data in case it is interrupted (Default: ``True``).
        """
        # Create location for saving
        save_path = self.output_dir / "metadata"
        save_path.mkdir(parents=True, exist_ok=True)
        all_successful = True
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

        checkpoint_path = (
            self.output_dir / "metadata" / mappings.METADATA_CHECKPOINT_NAME
        )
        checkpoint = self.load_checkpoint(checkpoint_path) if resume_download else {}
        checkpoint_lock = Lock()
        # Load or build catalog HREF map
        if resume_download and checkpoint:
            log.info("Resuming download from checkpoint.")
            all_children = [
                self.get_catalog(href=data[mappings.CHECKPOINT_HREF])
                for key, data in checkpoint.items()
                if isinstance(data, dict) and "href" in data
            ]
            save_description = checkpoint["save_description"]
        else:
            if heliostats is None:
                root = self.get_catalog(href=mappings.CATALOGUE_URL)
                log.info("Loading all children in root catalog - please be patient!")
                all_children = list(root.get_children())
                for i in range(
                    len(all_children) - 1, -1, -1
                ):  # Iterate backwards through the list.
                    child = all_children[i]
                    if (
                        child.id == mappings.WEATHER_COLLECTION_ID
                        or child.id == mappings.TOWER_FILE_NAME
                    ):
                        all_children.pop(i)
            else:
                # Find the catalogs for each desired heliostat.
                log.info("Loading catalogs for desired heliostats.")
                all_children = [
                    self.get_catalog(
                        href=mappings.HELIOSTAT_CATALOG_URL % (heliostat, heliostat)
                    )
                    for heliostat in heliostats
                ]
            save_description = (
                "all_heliostats"
                if heliostats is None
                else f"selected_heliostats_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            if resume_download:
                for child in all_children:
                    if child.id not in (
                        mappings.WEATHER_COLLECTION_ID,
                        mappings.TOWER_FILE_NAME,
                    ):
                        checkpoint[child.id] = {
                            mappings.CHECKPOINT_HREF: child.get_self_href()
                        }
                if "save_description" not in checkpoint:
                    checkpoint["save_description"] = save_description
            self.save_checkpoint(checkpoint_path, checkpoint)

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

            temp_dir = self.output_dir / "metadata" / "temp" / collection
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Use tqdm to track progress.
            with tqdm(
                desc="Processing Heliostat Catalogs",
                unit=" catalog",
                total=len(all_children),
            ) as pbar:
                # Run parallel download
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            self._process_metadata_with_checkpoint,
                            child,
                            collection,
                            id_base,
                            checkpoint,
                            checkpoint_path,
                            checkpoint_lock,
                            temp_dir,
                            pbar,
                        )
                        for child in all_children
                    ]
                    for f in futures:
                        result = f.result()
                        if not result:
                            all_successful = False

            # Concatenate all temporary files into final dataframe
            log.info(f"Combining metadata for collection: {collection}")
            csv_files = sorted(temp_dir.glob("*.csv"))
            if csv_files:
                dfs = [
                    pd.read_csv(f).set_index(mappings.SAVE_ID_INDEX) for f in csv_files
                ]
                final_df = pd.concat(dfs)
                output_file = (
                    self.output_dir
                    / "metadata"
                    / f"{collection}_metadata_{save_description}.csv"
                )
                final_df.to_csv(output_file)
                log.info(f"Saved final metadata for {collection} to: {output_file}")
            else:
                log.warning(f"No metadata files created for collection '{collection}'.")

            shutil.rmtree(temp_dir)

        if resume_download and checkpoint_path.exists():
            if all_successful:
                checkpoint_path.unlink()
                temp_parent = save_path / "temp"
                shutil.rmtree(temp_parent)
                log.info("All metadata downloaded. Checkpoint file removed.")
            else:
                log.warning(
                    "Some metadata failed to download; checkpoint retained for resume."
                )

    @staticmethod
    def _check_filtered_calibration_keys(
        filtered_calibration_keys: list[str] | None = None,
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
        filtered_calibration_keys: list[str] | None = None,
        benchmark_split: str | None = None,
        pbar: tqdm | None = None,
        verbose: bool = True,
        timeout: int = 60,
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
        timeout : int
            Timeout for downloading calibration item (Default: 60 seconds).
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
                    f"No data downloaded for item {item_id} from {heliostat_id}!"
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
                _ = self.download_file(url, file_name, timeout=timeout)
        if pbar is not None:
            pbar.update(1)

    def get_multiple_calibration_items_by_id(
        self,
        heliostat_items_dict: dict[str, list[int] | None],
        filtered_calibration_keys: list[str] | None = None,
        timeout: int = 60,
        num_parallel_workers: int = 10,
        results_timeout: int = 300,
    ) -> None:
        """
        Download multiple calibration items for multiple heliostats.

        Parameters
        ----------
        heliostat_items_dict : dict[str, list[int] | None]
            A dictionary mapping heliostat IDs to lists of item IDs to be downloaded. If the list of item IDs is ``None``,
            all items for that heliostat will be downloaded.
        filtered_calibration_keys : list[str]
            List of keys to filter the calibration data. These keys must be one of: ``raw_image``, ``cropped_image``,
            ``flux_image``, ``flux_centered_image``, ``calibration_properties``. If no list is provided, all calibration
            data is downloaded (Default: ``None``).
        timeout : int
            Timeout for downloading individual items in a split.
        num_parallel_workers : int
            Number of parallel workers for downloading data (Default: 10).
        results_timeout : int
            Timeout for collecting results from multiple threads (Default: 300 seconds).
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
                    with ThreadPoolExecutor(
                        max_workers=num_parallel_workers
                    ) as executor:
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
                                timeout=timeout,
                            )
                            for item in all_items
                        ]
                        # Wait for all tasks to complete.
                        for future in as_completed(futures):
                            try:
                                future.result(timeout=results_timeout)
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
                        timeout=timeout,
                    )
