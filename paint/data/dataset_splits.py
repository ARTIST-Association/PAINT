from pathlib import Path
from typing import Union

import pandas as pd

import paint.util.paint_mappings as mappings


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

        print("HI")
