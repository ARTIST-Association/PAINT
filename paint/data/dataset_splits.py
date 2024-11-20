import logging
from pathlib import Path
from typing import Union

import pandas as pd

import paint.util.paint_mappings as mappings

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
        remove_unused_data: bool = True,
    ):
        """
        Initialize the dataset splitter.

        Parameters
        ----------
        input_file : Union[Path, str]
            Path to the input file containing the metadata required to generate the dataset splits.
        output_dir : Union[Path, str]
            Path to the output directory where the dataset splits will be saved.
        remove_unused_data : bool
            Indicating whether extra metadata should be removed from the resulting dataset splits (Default: `True`).
        """
        input_file = Path(input_file)
        assert (
            input_file.exists()
        ), f"Input file containing metadata does not exist at {input_file}"
        self.metadata = pd.read_csv(input_file, index_col=mappings.ID_INDEX)
        self.metadata[mappings.DATETIME] = pd.to_datetime(
            self.metadata[mappings.DATETIME]
        ).dt.tz_localize(None)
        self.metadata = self.metadata.drop(
            columns=[
                "lower_left_latitude",
                "lower_left_longitude",
                "lower_left_Elevation",
                "upper_left_latitude",
                "upper_left_longitude",
                "upper_left_Elevation",
                "upper_right_latitude",
                "upper_right_longitude",
                "upper_right_Elevation",
                "lower_right_latitude",
                "lower_right_longitude",
                "lower_right_Elevation",
            ]
        )
        self.metadata[mappings.SPLIT_KEY] = ""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.remove_unused_data = remove_unused_data

    @staticmethod
    def _get_azimuth_splits(
        heliostat_data: pd.DataFrame, training_size: int, validation_size: int
    ) -> pd.DataFrame:
        """
        Get the splits for the azimuth method.

        Parameters
        ----------
        heliostat_data : pd.DataFrame
            Data for a single heliostat.
        training_size : int
            Size of the training split.
        validation_size : int
            Size of the validation split.

        Returns
        -------
        pd.DataFrame
            Heliostat data including the associated split.
        """
        # Sort data by azimuth and time.
        heliostat_data = heliostat_data.sort_values(
            by=[mappings.AZIMUTH, mappings.DATETIME]
        )
        # Select the indices with the smallest azimuth values for the training split.
        training_indices = heliostat_data.head(training_size).index
        heliostat_data.loc[training_indices, mappings.SPLIT_KEY] = mappings.TRAIN_INDEX

        # Select the indices with the largest azimuth values for the validation split.
        validation_indices = heliostat_data.tail(validation_size).index
        heliostat_data.loc[
            validation_indices, mappings.SPLIT_KEY
        ] = mappings.VALIDATION_INDEX

        # Select the remaining indices for the test split.
        used_indices = training_indices.append(validation_indices)
        test_indices = heliostat_data.index.difference(used_indices)
        heliostat_data.loc[test_indices, mappings.SPLIT_KEY] = mappings.TEST_INDEX
        return heliostat_data

    @staticmethod
    def _get_nearest_solstice_distance(timestamp: pd.Timestamp, season: str) -> float:
        """
        Calculate the distances to the nearest December 21 and June 21.

        Parameters
        ----------
        timestamp : pd.Timestamp
            The current time stamp considered.
        season : str
            Whether to consider summer or winter solstice. Must be either "summer" or "winter".

        Returns
        -------
        float
            The time distance to the nearest solstice in seconds.
        """
        day = 21  # Solstice day of month
        if season == "summer":
            month = 6  # Summer solstice month
        elif season == "winter":
            month = 12  # Winter solstice month
        else:
            raise ValueError(f"Season {season} must be either summer or winter.")
        year = timestamp.year  # Considered year
        current_solstice = pd.Timestamp(year=year, month=month, day=day, hour=12)
        next_solstice = pd.Timestamp(year=year + 1, month=month, day=day, hour=12)
        previous_solstice = pd.Timestamp(year=year - 1, month=month, day=day, hour=12)

        return min(
            abs((timestamp - current_solstice).total_seconds()),
            abs((timestamp - next_solstice).total_seconds()),
            abs((timestamp - previous_solstice).total_seconds()),
        )

    def _get_solstice_splits(
        self, heliostat_data: pd.DataFrame, training_size: int, validation_size: int
    ) -> pd.DataFrame:
        """
        Get the splits for the solstice method.

        Parameters
        ----------
        heliostat_data : pd.DataFrame
            Data for a single heliostat.
        training_size : int
            Size of the training split.
        validation_size : int
            Size of the validation split.

        Returns
        -------
        pd.DataFrame
            Heliostat data including the associated split.
        """
        # Calculate the distance from the winter solstice for each image.
        heliostat_data[mappings.DISTANCE_WINTER] = heliostat_data[
            mappings.DATETIME
        ].apply(
            lambda x: self._get_nearest_solstice_distance(timestamp=x, season="winter")
        )  # Winter solstice

        # Calculate the distance from the summer solstice for each image.
        heliostat_data[mappings.DISTANCE_SUMMER] = heliostat_data[
            mappings.DATETIME
        ].apply(
            lambda x: self._get_nearest_solstice_distance(timestamp=x, season="summer")
        )  # Summer solstice

        # Select the indices closest to the winter solstice for training purposes.
        heliostat_data = heliostat_data.sort_values(
            by=[mappings.DISTANCE_WINTER, mappings.DATETIME]
        )
        training_indices = heliostat_data.head(training_size).index
        heliostat_data.loc[training_indices, mappings.SPLIT_KEY] = mappings.TRAIN_INDEX

        # Select the indices closest to the summer solstice for training purposes.
        heliostat_data = heliostat_data.sort_values(
            by=[mappings.DISTANCE_SUMMER, mappings.DATETIME]
        )
        validation_indices = heliostat_data.head(validation_size).index
        heliostat_data.loc[
            validation_indices, mappings.SPLIT_KEY
        ] = mappings.VALIDATION_INDEX

        # Select the remaining indices for the test split.
        used_indices = training_indices.append(validation_indices)
        test_indices = heliostat_data.index.difference(used_indices)
        heliostat_data.loc[test_indices, mappings.SPLIT_KEY] = mappings.TEST_INDEX

        # Drop the solstice distances from the dataframe
        heliostat_data = heliostat_data.drop(
            columns=[mappings.DISTANCE_SUMMER, mappings.DISTANCE_WINTER]
        )

        return heliostat_data

    def get_dataset_splits(
        self, split_type: str, training_size: int, validation_size: int
    ) -> pd.DataFrame:
        """
        Get dataset splits and save splits as a CSV file.

        This function determines the dataset splits and creates a data frame containing information about these splits.
        This data frame is returned, optionally with extra metadata. Additionally, the splits without metadata are
        saved as a CSV file.

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

        if split_type == mappings.AZIMUTH_SPLIT:
            log.info("Preparing azimuth split...")
            log.info(
                f"Training Size: {training_size}, Validation Size: {validation_size}, and Test Size > {validation_size}"
            )
            heliostat_split_data = heliostat_split_data.groupby(
                mappings.HELIOSTAT_ID, group_keys=False
            ).apply(
                lambda heliostat_data: self._get_azimuth_splits(
                    heliostat_data=heliostat_data,
                    training_size=training_size,
                    validation_size=validation_size,
                )
            )
            log.info("Azimuth split complete!")
        elif split_type == mappings.SOLSTICE_SPLIT:
            log.info("Preparing solstice split...")
            log.info(
                f"Training Size: {training_size}, Validation Size: {validation_size}, and Test Size > {validation_size}"
            )
            heliostat_split_data = heliostat_split_data.groupby(
                mappings.HELIOSTAT_ID, group_keys=False
            ).apply(
                lambda heliostat_data: self._get_solstice_splits(
                    heliostat_data=heliostat_data,
                    training_size=training_size,
                    validation_size=validation_size,
                )
            )
            log.info("Solstice split complete!")
        else:
            raise ValueError(f"The split type {split_type} is not supported!")

        # Never save the extra metadata in the CSV (this extra data is only needed for plots).
        splits_to_save = heliostat_split_data
        splits_to_save = splits_to_save.drop(
            columns=[mappings.DATETIME, mappings.AZIMUTH, mappings.ELEVATION]
        )
        file_name = (
            self.output_dir
            / f"Benchmark_split-{split_type}_train-{training_size}_validation-{validation_size}.csv"
        )
        splits_to_save.to_csv(file_name, index=True)

        # Remove extra metadata columns if desired.
        if self.remove_unused_data:
            heliostat_split_data = heliostat_split_data.drop(
                columns=[mappings.DATETIME, mappings.AZIMUTH, mappings.ELEVATION]
            )

        return heliostat_split_data
