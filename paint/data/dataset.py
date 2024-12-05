import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Self, Union

import cv2
import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from tqdm import tqdm

import paint.util.paint_mappings as mappings
from paint.data import StacClient

log = logging.getLogger(__name__)  # Logger for the STAC client


class PaintCalibrationDataset(Dataset):
    """
    Dataset for PAINT calibration data.

    Attributes
    ----------
    file_identifier : str
        Identifies what type of file to be loaded.
    root_dir : Union[str, Path]
        Directory where the dataset will be stored.
    item_ids : list[int]
        List of item IDs that should be included in the dataset.
    to_tensor : torchvision.transforms.ToTensor
        Transform to convert image to tensor.

    Methods
    -------
    from_benchmark()
        Class method to initialize dataset from a benchmark file.
    """

    def __init__(
        self,
        root_dir: Union[str, Path],
        item_type: str,
        item_ids: Union[list[int], None] = None,
    ) -> None:
        """
        Initialize a PaintCalibrationDataset.

        This dataset contains calibration data from the paint dataset.

        Parameters
        ----------
        root_dir : Union[str, Path]
            Directory where the dataset will be stored.
        item_type : str
            Type of item being loaded, i.e. raw image, cropped image, flux image, flux centered image, or calibration
            properties.
        item_ids : list[int]
            List of item IDs that should be included in the dataset. If no list is provided, all files in that folder
            of the specified type will be loaded.
        """
        self._check_accepted_keys(item_type)
        log.info(f"Initializing a data set for {item_type} calibration items...")
        if item_type in [
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
        ]:
            log.info("Note that this is a dataset containing images!")
        else:
            log.info(
                "Note that this is a dataset containing dictionaries of calibration properties!"
            )
        self.file_identifier = self._map_to_file_identifier(item_type)
        self.root_dir = Path(root_dir)
        if not self.root_dir.exists():
            raise FileNotFoundError(
                "The root directory does not exist - you should download the dataset first!"
            )

        if item_ids is None:
            item_ids = []
            for item in self.root_dir.iterdir():
                if item.is_file() and self.file_identifier in item.name:
                    if self.file_identifier in [
                        mappings.CALIBRATION_RAW_IMAGE_IDENTIFIER,
                        mappings.CALIBRATION_CROPPED_IMAGE_IDENTIFIER,
                        mappings.CALIBRATION_FLUX_IMAGE_IDENTIFIER,
                        mappings.CALIBRATION_FLUX_CENTERED_IMAGE_IDENTIFIER,
                    ]:
                        item_ids.append(int(item.name.split("_")[0]))
                    else:
                        item_ids.append(int(item.name.split("-")[0]))
        self.item_ids = item_ids
        self.to_tensor = transforms.ToTensor()

    def __str__(self) -> str:
        """Generate a user-friendly representation of the dataset."""
        return (
            f"This is a dataset containing calibration items from the PAINT database:\n"
            f"-The root directory is {self.root_dir}\n"
            f"-The file identifier is {self.file_identifier}\n"
            f"-The dataset contains {len(self.item_ids)} items\n"
        )

    @staticmethod
    def _check_accepted_keys(key: str) -> None:
        """
        Check if the considered calibration item type is accepted.

        Parameters
        ----------
        key : str
            Key of the calibration item type to be checked.
        """
        accepted_items = [
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
        ]
        if key not in accepted_items:
            raise ValueError(
                f"The calibration type {key} is not accepted. Please select one of "
                f"{mappings.CALIBRATION_RAW_IMAGE_KEY}, {mappings.CALIBRATION_CROPPED_IMAGE_KEY}, "
                f"{mappings.CALIBRATION_FLUX_IMAGE_KEY}, {mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY}, or "
                f"{mappings.CALIBRATION_PROPERTIES_KEY,}"
            )

    @staticmethod
    def _map_to_file_identifier(key: str) -> str:
        """
        Convert a calibration item type to a calibration file identifier.

        Parameters
        ----------
        key : str
            Key to be mapped.

        Returns
        -------
        str
            Mapped key to the file identifier.
        """
        mapper = {
            mappings.CALIBRATION_RAW_IMAGE_KEY: mappings.CALIBRATION_RAW_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY: mappings.CALIBRATION_CROPPED_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_FLUX_IMAGE_KEY: mappings.CALIBRATION_FLUX_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY: mappings.CALIBRATION_FLUX_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_PROPERTIES_KEY: mappings.CALIBRATION_PROPERTIES_IDENTIFIER,
        }
        return mapper[key]

    @classmethod
    def from_benchmark(
        cls,
        benchmark_file: Union[str, Path],
        root_dir: Union[str, Path],
        item_type: str,
        download: bool = False,
    ) -> tuple[Self, Self, Self]:
        """
        Initialize calibration dataset from a benchmark file.

        This function returns a train, test, and validation dataset given a benchmark.

        Parameters
        ----------
        benchmark_file : Union[str, Path]
            Path to the file containing the benchmark information.
        root_dir : Union[str, Path]
            Directory where the dataset will be stored.
        item_type : str
            Type of item being loaded, i.e. raw image, cropped image, flux image, or calibration properties.
        download : bool
            Whether to download the data (Default is ``False``).

        Returns
        -------
        PaintCalibrationDataset
            Train dataset.
        PaintCalibrationDataset
            Test dataset.
        PaintCalibrationDataset
            Validation dataset.
        """
        root_dir = Path(root_dir)

        # Load the splits data.
        splits = pd.read_csv(benchmark_file)

        # Check whether to download the data or not.
        if download:
            log.info("Downloading the benchmark items...")
            split_ids = cls._download_benchmark_splits(
                splits=splits, root_dir=root_dir, item_type=item_type
            )
        else:
            # Check if the folder exists, if not the data must be downloaded.
            if not root_dir.is_dir():
                log.warning(
                    "The root directory does not exist, the data has not yet been downloaded!\n"
                    "The data will now be downloaded..."
                )
                split_ids = cls._download_benchmark_splits(
                    splits=splits, root_dir=root_dir, item_type=item_type
                )
            # If the data is present, we can load it directly.
            else:
                split_ids = (
                    splits.groupby(mappings.SPLIT_KEY)
                    .apply(lambda x: list(x[mappings.ID_INDEX]))
                    .to_dict()
                )

        # Initialize a train dataset.
        train_dataset = cls(
            root_dir=Path(root_dir) / mappings.TRAIN_INDEX,
            item_ids=split_ids[mappings.TRAIN_INDEX],
            item_type=item_type,
        )

        # Initialize a test dataset.
        test_dataset = cls(
            root_dir=Path(root_dir) / mappings.TEST_INDEX,
            item_ids=split_ids[mappings.TEST_INDEX],
            item_type=item_type,
        )

        # Initialize a validation dataset.
        validation_dataset = cls(
            root_dir=Path(root_dir) / mappings.VALIDATION_INDEX,
            item_ids=split_ids[mappings.VALIDATION_INDEX],
            item_type=item_type,
        )

        return (
            train_dataset,
            test_dataset,
            validation_dataset,
        )

    @staticmethod
    def _download_benchmark_splits(
        splits: pd.DataFrame,
        root_dir: Union[str, Path],
        item_type: str,
    ) -> dict[str, Any]:
        """
        Download the benchmark splits.

        This is a helper function that downloads the data for the benchmark splits. It also returns a dictionary
        containing information about the item IDs present in each split.

        Parameters
        ----------
        splits : pd.DataFrame
            Information on the splits to be downlaoded.
        root_dir : Union[str, Path]
            Directory where the data will be stored.
        item_type : str
            Type of item being downloaded, i.e. raw image, cropped image, flux image, or calibration properties.

        Returns
        -------
        dict[str, Any]
            Information about the item IDs present in each split.
        """
        # Create STAC client.
        client = StacClient(output_dir=root_dir)
        ids_dict = {}
        for split_name, split_data in splits.groupby(mappings.SPLIT_KEY):
            # Save the IDS of the items present in each split.
            ids_dict[str(split_name)] = list(split_data[mappings.ID_INDEX])
            number_items = len(split_data)
            with tqdm(
                total=number_items,
                desc=f"Downloading benchmark data for the {split_name} split",
                unit="Item",
            ) as pbar:
                with ThreadPoolExecutor() as executor:
                    # Create a list of future objects.
                    futures = [
                        executor.submit(
                            client.get_single_calibration_item_by_id,
                            heliostat_id=item[mappings.HELIOSTAT_ID],
                            item_id=item[mappings.ID_INDEX],
                            filtered_calibration_keys=[item_type],
                            benchmark_split=item[mappings.SPLIT_KEY],
                            verbose=False,
                            pbar=pbar,
                        )
                        for _, item in split_data.iterrows()
                    ]
                    # Wait for all tasks to complete.
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            # Handle exceptions from individual tasks.
                            print(f"Error in thread execution: {e}")
        return ids_dict

    def __len__(self) -> int:
        """
        Calculate the length of the dataset.

        Returns
        -------
        int
            Length of the dataset.
        """
        return len(self.item_ids)

    def __getitem__(self, idx: int) -> Union[torch.Tensor, dict[str, Any]]:
        """
        Return the item at position ``idx``.

        Parameters
        ----------
        idx : int
            Index of the item to be retrieved.

        Returns
        -------
        Union[torch.Tensor, dict[str, Any]]
            Either the image as a torch.Tensor or a dict containing the calibration properties, depending on the item
            type selected.
        """
        id_ = self.item_ids[idx]
        file_name = self.root_dir / f"{id_}{self.file_identifier}"
        if self.file_identifier in [
            mappings.CALIBRATION_RAW_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_CROPPED_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_FLUX_IMAGE_IDENTIFIER,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_IDENTIFIER,
        ]:
            item = cv2.imread(str(file_name))
            item = self.to_tensor(item)
        else:
            with open(file_name, "r") as file:
                item = json.load(file)
        return item
