import json
import logging
from pathlib import Path
from typing import Any, Union

import cv2
import torch
from torch.utils.data import Dataset
from torchvision import transforms

import paint.util.paint_mappings as mappings

log = logging.getLogger(__name__)  # Logger for the STAC client


class PaintCalibrationDataset(Dataset):
    """
    Dataset for PAINT calibration data.

    Attributes
    ----------
    TODO: Include attributes.

    Methods
    -------
    TODO: Include Methods.
    """

    def __init__(
        self,
        root_dir: Union[str, Path],
        item_ids: list[int],
        item_type: str,
        split: Union[str, None] = None,
        download: bool = False,
    ):
        """
        Initialize a PaintCalibrationDataset.

        This dataset contains calibration data from the paint dataset.

        Parameters
        ----------
        root_dir : Union[str, Path]
            Directory where the dataset will be stored.
        item_ids : list[int]
            List of item IDs that should be included in the dataset.
        item_type : str
            Type of item being loaded, i.e. raw image, cropped image, flux image, flux centered image, or calibration
            properties.
        split : Union[str, None]
            What type of split is being used (Default is ``None``).
        download : bool
            Whether the dataset should be downloaded or not (Default is``False``).
        """
        accepted_items = [
            mappings.CALIBRATION_RAW_IMAGE_KEY,
            mappings.CALIBRATION_CROPPED_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_IMAGE_KEY,
            mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY,
            mappings.CALIBRATION_PROPERTIES_KEY,
        ]
        if item_type not in accepted_items:
            raise ValueError(
                f"The calibration type {item_type} is not accepted. Please select one of "
                f"{mappings.CALIBRATION_RAW_IMAGE_KEY}, {mappings.CALIBRATION_CROPPED_IMAGE_KEY}, "
                f"{mappings.CALIBRATION_FLUX_IMAGE_KEY}, {mappings.CALIBRATION_FLUX_CENTERED_IMAGE_KEY}, or "
                f"{mappings.CALIBRATION_PROPERTIES_KEY,}"
            )
        self.file_identifier = self._map_to_file_identifier(item_type)
        self.item_ids = item_ids
        self.root_dir = Path(root_dir)
        self.split = split
        self.to_tensor = transforms.ToTensor()

        if download:
            self._download()

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

    def _download(self):
        """Download the dataset if it doesn't exist."""
        # TODO: Implement
        pass

    def __len__(self):
        """Calculate the length of the dataset."""
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
