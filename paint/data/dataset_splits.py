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
    metadata : pd.DataFrame
        Metadata used to generate the dataset splits.
    output_dir : pathlib.Path
        Output directory for saving the dataset splits.
    remove_unused_data : bool
        Whether unused metadata should be removed or not.

    Methods
    -------
    get_dataset_splits()
        Get the dataset splits and save them to a CSV file.
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
            Whether extra metadata should be removed from the resulting dataset splits (Default: `True`).
        """
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(
                f"Input file containing metadata does not exist at {input_file}"
            )
        self.metadata = pd.read_csv(input_file, index_col=mappings.SAVE_ID_INDEX)
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
        Get the splits for the azimuth-based splitting method.

        For a single heliostat, the ``training_size`` indices with the smallest azimuth values are selected for the
        training split, while the ``validation_size`` indices with the largest values are selected for the validation
        split. The remaining indices are assigned to the test split.

        This ensures that indices with very different azimuth values are considered in the train and validation samples,
        i.e., the train and validation splits should contain very different samples. This difference leads to a high
        level of difficulty and should guarantee that the trained calibration method is robust.

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
        Get the splits for the solstice-based splitting method.

        For a single heliostat, the ``training_size`` indices closest to the winter solstice are selected for the
        training split, while the ``validation_size`` indices closest to the summer solstice are selected for the
        validation split. The remaining indices are assigned to the test split.

        This ensures that indices from very different seasons, i.e. different conditions, are considered in training and
        validation, i.e., the train and validation splits should contain very different samples. This difference leads to
        a high level of difficulty and should guarantee that the trained calibration method is robust.

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

    def _get_kmeans_splits(
        self, heliostat_data: pd.DataFrame, training_size: int, validation_size: int
    ) -> pd.DataFrame:
        """
        Get splits using a KMeans clustering based method.

          - validation_size samples for validation,
          - validation_size samples for testing, and
          - training_size samples for training.

        The clustering is used for stratification. For validation, one candidate is drawn from
        each cluster. For test, we attempt to select one candidate per cluster that is different from
        the validation candidate; if a cluster has only one sample, then the missing test candidate is
        filled from the overall pool.
        All remaining data points (i.e. those not used for validation or test) are candidates for training.

        Parameters
        ----------
        heliostat_data : pd.DataFrame
            Data for a single heliostat.
        training_size : int
            Desired number of training samples.
        validation_size : int
            Desired number of validation samples (and also test samples).

        Returns
        -------
        pd.DataFrame
            DataFrame with splits assigned in the column specified by `mappings.SPLIT_KEY`.
            The returned DataFrame contains exactly training_size + 2*validation_size rows.

        Raises
        ------
        ValueError
            If the overall number of data points is insufficient.
        """
        from sklearn.cluster import KMeans

        # Use the chosen features.
        features = heliostat_data[[mappings.AZIMUTH, mappings.ELEVATION]].to_numpy()
        # Cluster into exactly validation_size clusters.
        kmeans = KMeans(n_clusters=validation_size, random_state=42)
        cluster_labels = kmeans.fit_predict(features)
        heliostat_data = heliostat_data.copy()
        heliostat_data["cluster_label"] = cluster_labels

        import random

        random.seed(42)

        # For each cluster, choose one candidate for validation.
        validation_candidates = {}
        # For test, try to choose one candidate per cluster that is not the validation candidate.
        test_candidates = {}

        for label, group in heliostat_data.groupby("cluster_label"):
            group_indices = list(group.index)
            # For validation, if possible, choose one candidate.
            if group_indices:
                val_candidate = random.choice(group_indices)
                validation_candidates[label] = val_candidate
            # For test, if the cluster has at least 2 samples, choose one candidate different from the validation one.
            if len(group_indices) >= 2:
                available = [
                    idx for idx in group_indices if idx != validation_candidates[label]
                ]
                test_candidate = random.choice(available)
                test_candidates[label] = test_candidate

        # If some cluster did not yield a test candidate (because it had only one point),
        # fill the missing test candidate(s) from the overall pool (excluding any already used for validation or test).
        all_indices = set(heliostat_data.index)
        already_used = set(validation_candidates.values()) | set(
            test_candidates.values()
        )
        missing_count = validation_size - len(test_candidates)
        if missing_count > 0:
            candidate_pool = list(all_indices - already_used)
            random.shuffle(candidate_pool)
            for i in range(missing_count):
                # Use a pseudo-cluster label "extra_i" for these extra assignments.
                test_candidates[f"extra_{i}"] = candidate_pool[i]

        # At this point, we have exactly validation_size validation candidates and exactly validation_size test candidates.
        final_validation_indices = list(validation_candidates.values())
        final_test_indices = list(test_candidates.values())

        # Training candidates are all points not used in validation or test.
        used_for_val_test = set(final_validation_indices) | set(final_test_indices)
        training_pool = list(all_indices - used_for_val_test)
        random.shuffle(training_pool)
        final_training_indices = training_pool[:training_size]

        # Compile final indices.
        final_indices = (
            final_validation_indices + final_test_indices + final_training_indices
        )

        # Assign splits using the mappings.
        heliostat_data[mappings.SPLIT_KEY] = ""
        heliostat_data.loc[
            final_validation_indices, mappings.SPLIT_KEY
        ] = mappings.VALIDATION_INDEX
        heliostat_data.loc[final_test_indices, mappings.SPLIT_KEY] = mappings.TEST_INDEX
        heliostat_data.loc[
            final_training_indices, mappings.SPLIT_KEY
        ] = mappings.TRAIN_INDEX

        # Return only the selected rows and drop the helper column.
        result = heliostat_data.loc[final_indices].copy()
        result = result.drop(columns=["cluster_label"])
        return result

    def _get_knn_splits(
        self,
        heliostat_data: pd.DataFrame,
        validation_size: int,
        training_size: int,
        n_neighbors: int = 3,
    ) -> pd.DataFrame:
        """
        Get splits using a k-nearest neighbors (KNN) based method.

        For each data point in the given heliostat's data, the average distance to its n_neighbors
        closest points (excluding itself) is computed. Then, the splits are assigned as follows:

        - **Validation:** The first `validation_size` data points from the sorted order (by descending average distance)
          are assigned to validation.
        - **Test:** The next `validation_size` data points in the sorted order are assigned to test.
        - **Training:** The last `training_size` data points (with the smallest average distances) are assigned to training.
        - All other data points are discarded.

        This requires that the total number of data points is at least:

            total_required = training_size + 2 * validation_size

        Parameters
        ----------
        heliostat_data : pd.DataFrame
            Data for a single heliostat.
        validation_size : int
            Number of data points to assign to the validation set.
        training_size : int
            Number of data points to assign to the training set.
        n_neighbors : int, optional
            Number of nearest neighbors to consider when computing the average distance (default is 3).

        Returns
        -------
        pd.DataFrame
            A dataframe containing only the selected data points with their assigned split in the
            column specified by `mappings.SPLIT_KEY`.

        Raises
        ------
        ValueError
            If there are not enough data points to compute the KNN metric or to assign the requested
            number of samples.
        """
        from sklearn.neighbors import NearestNeighbors

        # Use azimuth and elevation as features.
        features = heliostat_data[[mappings.AZIMUTH, mappings.ELEVATION]].to_numpy()
        nbrs = NearestNeighbors(n_neighbors=n_neighbors + 1).fit(features)
        distances, _ = nbrs.kneighbors(features)
        # Exclude the zero self-distance and compute the average over the n_neighbors.
        avg_distance = distances[:, 1:].mean(axis=1)

        heliostat_data = heliostat_data.copy()
        heliostat_data["knn_avg_distance"] = avg_distance

        # Sort data by average distance in descending order.
        sorted_df = heliostat_data.sort_values(by="knn_avg_distance", ascending=False)

        # Select splits:
        # 1. Validation: first validation_size rows.
        validation_indices = sorted_df.iloc[:validation_size].index
        # 2. Test: next validation_size rows.
        test_indices = sorted_df.iloc[validation_size : 2 * validation_size].index
        # 3. Training: last training_size rows (lowest average distances).
        training_indices = sorted_df.iloc[2 * validation_size : training_size + 2 * validation_size].index

        # Assign split labels.
        heliostat_data[mappings.SPLIT_KEY] = ""
        heliostat_data.loc[
            validation_indices, mappings.SPLIT_KEY
        ] = mappings.VALIDATION_INDEX
        heliostat_data.loc[test_indices, mappings.SPLIT_KEY] = mappings.TEST_INDEX
        heliostat_data.loc[training_indices, mappings.SPLIT_KEY] = mappings.TRAIN_INDEX

        # Gather only the selected data points.
        selected_indices = (
            list(validation_indices) + list(test_indices) + list(training_indices)
        )
        selected_data = heliostat_data.loc[selected_indices].copy()

        # Remove the helper column.
        selected_data = selected_data.drop(columns=["knn_avg_distance"])

        return selected_data

    def get_dataset_splits(
        self, split_type: str, training_size: int, validation_size: int
    ) -> pd.DataFrame:
        """
        Get dataset splits and save splits as a CSV file.

        This function determines the dataset splits and creates a dataframe containing information about these splits.
        This data frame is returned, optionally with extra metadata. Additionally, the splits without metadata are
        saved as a CSV file.

        This function supports the following split types:
        - ``azimuth``: The azimuth of the sun is used to calculate the splits. Specifically, the images with the
        smallest azimuth values are used for training, the images with the largest azimuth values are used for
        validation, and the remaining images for testing.
        - ``solstice``: The distance from the winter and summer solstice is used to calculate the splits. Specifically,
        the images closest to the winter solstice are used for training, the images closest to the summer solstice for
        validation, and the remaining images for testing.

        Parameters
        ----------
        split_type : str
            Type of split to be performed. Currently, ``azimuth`` and ``solstice`` split types are available.
        training_size : int
            Size of the training split.
        validation_size : int
            Size of the validation split.
        """
        allowed_split_types = [
            mappings.AZIMUTH_SPLIT,
            mappings.SOLSTICE_SPLIT,
            mappings.KMEANS_SPLIT,
            mappings.KNN_SPLIT,
        ]
        if split_type not in allowed_split_types:
            raise ValueError(
                f"The split type must be one of {', '.join(allowed_split_types)}."
                f"The selected split type {split_type} is not supported!"
            )
            
        # Calculate the minimum number of possible images as `training_size` + 2 * `validation_size`, since we want at
        # least as many test images as validation images.
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
            f"images, {validation_size} validation images, and at least {validation_size} test images:\n{dropped_heliostats}"
        )
        log.info(dropped_heliostats)

        if len(heliostat_split_data) == 0:
            raise ValueError(
                "There are no heliostats left! Your requirements for training and validation size are too"
                "high. Please retry with a smaller number of required training or validation images!"
            )

        if split_type == mappings.AZIMUTH_SPLIT:
            log.info(
                "Preparing azimuth split...\n"
                f"Training size: {training_size}, validation size: {validation_size}, and test size > {validation_size}"
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
            log.info(
                "Preparing solstice split...\n"
                f"Training size: {training_size}, validation size: {validation_size}, and test size > {validation_size}"
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
        elif split_type == mappings.KMEANS_SPLIT:
            log.info(
                "Preparing KMeans split...\n"
                f"Training size: {training_size}, validation size: {validation_size}"
            )
            heliostat_split_data = heliostat_split_data.groupby(
                mappings.HELIOSTAT_ID, group_keys=False
            ).apply(
                lambda heliostat_data: self._get_kmeans_splits(
                    heliostat_data=heliostat_data,
                    training_size=training_size,
                    validation_size=validation_size,
                )
            )
            log.info("KMeans split complete!")
        elif split_type == mappings.KNN_SPLIT:
            log.info(
                "Preparing KNN split...\n"
                f"Training size: {training_size}, validation size: {validation_size}"
            )
            heliostat_split_data = heliostat_split_data.groupby(
                mappings.HELIOSTAT_ID, group_keys=False
            ).apply(
                lambda heliostat_data: self._get_knn_splits(
                    heliostat_data=heliostat_data,
                    validation_size=validation_size,
                    training_size=training_size,
                )
            )
            log.info("KNN split complete!")

        # Never save the extra metadata in the CSV (this extra data is only needed for plots).
        splits_to_save = heliostat_split_data
        splits_to_save = splits_to_save.drop(
            columns=[mappings.DATETIME, mappings.AZIMUTH, mappings.ELEVATION]
        )
        file_name = (
            self.output_dir
            / f"benchmark_split-{split_type}_train-{training_size}_validation-{validation_size}.csv"
        )
        splits_to_save.to_csv(file_name, index=True)

        # Remove extra metadata columns if desired.
        if self.remove_unused_data:
            heliostat_split_data = heliostat_split_data.drop(
                columns=[mappings.DATETIME, mappings.AZIMUTH, mappings.ELEVATION]
            )

        return heliostat_split_data
