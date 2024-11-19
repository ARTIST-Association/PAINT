import logging
from pathlib import Path
from typing import Union

import pandas as pd

import paint.util.paint_mappings as mappings
from paint.util import set_logger_config

set_logger_config()
log = logging.getLogger(__name__)  # Logger for the dataset splitter


class DatasetSplitter:
    """
    Class to generate the benchmark dataset splits.

    Attributes
    ----------
    #TODO Include attributes

    Methods
    -------
    #TODO Include Methods
    """

    def __init__(
        self,
        input_file: Union[Path, str],
        output_dir: Union[Path, str],
    ):
        """
        Initialize the dataset splitter.

        Parameters
        ----------
        input_file : Union[Path, str]
            Path to the input file containing the metadata required to generate the dataset splits.
        output_dir : Union[Path, str]
            Path to the output directory where the dataset splits will be saved.
        """
        input_file = Path(input_file)
        assert (
            input_file.exists()
        ), f"Input file containing metadata does not exist at {input_file}"
        self.metadata = pd.read_csv(input_file, index_col=mappings.ID_INDEX)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_azimuth_splits(training_size: int, validation_size: int) -> None:
        """
        Get the splits for the azimuth method.

        Parameters
        ----------
        training_size : int
            Size of the training split.
        validation_size : int
            Size of the validation split.
        """
        pass

    def get_dataset_splits(
        self, split_type: str, training_size: int, validation_size: int
    ) -> None:
        """
        Get dataset splits and save them as a CSV file.

        Parameters
        ----------
        split_type : str
            Type of split to be performed.
        training_size : int
            Size of the training split.
        validation_size : int
            Size of the validation split.
        """
        allowed_split_types = [mappings.AZIMUTH_SPLIT, mappings.SOLSTICE_SPLIT]
        if split_type not in allowed_split_types:
            raise ValueError(
                f"The split type must be one of `{mappings.AZIMUTH_SPLIT}, {mappings.SOLSTICE_SPLIT}`. The"
                f"selected split type {split_type} is not supported!"
            )

        # Calculate the minimum number of possible images as training size + 2 * validation size, since we want at least
        # as many test images as validation images.
        minimum_number_of_images = training_size + 2 * validation_size

        # Identify heliostats that do not meet the minimum image requirement.
        heliostat_image_count = self.metadata.groupby(mappings.HELIOSTAT_ID).size()
        dropped_heliostats = heliostat_image_count[
            heliostat_image_count < minimum_number_of_images
        ].index.tolist()

        # Remove the heliostats not meeting the minimum image requirement.
        heliostat_split_data = self.metadata.groupby(mappings.HELIOSTAT_ID).filter(
            lambda x: len(x) >= minimum_number_of_images
        )

        log.info(
            f"The following {len(dropped_heliostats)} heliostats have been dropped for not meeting the requirements of {training_size} training "
            f"images, {validation_size} validation images, and at least {validation_size} test images:"
        )
        log.info(dropped_heliostats)

        for heliostat, heliostat_data in heliostat_split_data.groupby(
            mappings.HELIOSTAT_ID
        ):
            if split_type == mappings.AZIMUTH_SPLIT:
                pass  # TODO: Call azimuth split
            elif split_type == mappings.SOLSTICE_SPLIT:
                pass  # TODO: call solstice split
            else:
                raise ValueError(f"The split type {split_type} is not supported!")
