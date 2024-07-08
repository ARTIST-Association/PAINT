#!/usr/bin/env python

import argparse
from pathlib import Path
from typing import List, Union

import pandas as pd
from general_plotting_functions import (
    mark_insufficient_data_as_nan,
    plot_stacked_bar_chart_with_inset,
)
from matplotlib import pyplot as plt

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import calculate_azimuth_and_elevation


class DatasetMonthSplit:
    """
    Create monthly splits of the dataset.

    Attributes
    ----------
    measurements_df : pd.DataFrame
        The measured data.
    output_path : Union[Path, str]
        The path to the output directory to save the plots.
    number_of_train_samples : List[int]
        The number of samples used for training.
    number_of_validation_samples : List[int]
        The number of samples used for validation.
    file_name : str
        The file name to save the plot.

    Methods
    -------
    load_data()
        Load the data and include additional features.
    classify_date_split()
        Classify the data according to the date split.
    plot_month_split()
        Plot the month split.
    """

    def __init__(
        self,
        path_to_measurements: Union[Path, str],
        output_path: Union[str, Path],
        number_of_train_samples: List[int],
        number_of_validation_samples: int,
        default_example_heliostat: int = 11447,
        file_name: str = "03_combined_plots",
        save_as_pdf: bool = True,
    ) -> None:
        """
        Initialize the hour dataset splitter.

        Parameters
        ----------
        path_to_measurements : Union[Path, str]
            The path to the measurement data.
        output_path : Union[Path, str]
            The path to the output directory to save the plots.
        number_of_train_samples : List[int]
            The number of samples used for training.
        number_of_validation_samples : List[int]
            The number of samples used for validation.
        file_name : str
            The file name to save the plot.
        save_as_pdf : bool
            Indicates if the output should be saved as PDF (Default: True).
        """
        self.measurements_df = self.load_data(Path(path_to_measurements))
        self.output_path = Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        self.number_of_train_samples = number_of_train_samples
        self.number_of_validation_samples = number_of_validation_samples
        self.default_example_heliostat = default_example_heliostat
        if save_as_pdf:
            self.file_name = file_name + ".pdf"
        else:
            self.file_name = file_name + ".png"

    @staticmethod
    def load_data(path_to_measurements: Path) -> pd.DataFrame:
        """
        Load the data and include additional features.

        Parameters
        ----------
        path_to_measurements : Path
            The path to the measurement data.

        Returns
        -------
        pd.DataFrame
            The loaded data with additional time features.
        """
        df = pd.read_csv(path_to_measurements).set_index(
            mappings.ID_INDEX
        )  # Set df id as index
        df[mappings.CREATED_AT] = pd.to_datetime(df[mappings.CREATED_AT])
        df[mappings.AZIMUTH], df[mappings.ELEVATION] = calculate_azimuth_and_elevation(
            df
        )  # Calculate Azimuth and Elevation from Sun Vector
        return df

    @staticmethod
    def nearest_solstice_distance(
        timestamp: pd.Timestamp, month: int, day: int
    ) -> float:
        """
        Calculate the distances to the nearest December 21 and June 21.

        Parameters
        ----------
        timestamp : pd.Timestamp
            The current time step considered
        month : int
            The month to compare.
        day : int
            The day to compare.

        Returns
        -------
        float
            The time distance to the nearest solstice in seconds.
        """
        year = timestamp.year
        current_year_solstice = pd.Timestamp(year=year, month=month, day=day, hour=12)
        next_year_solstice = pd.Timestamp(year=year + 1, month=month, day=day, hour=12)
        prev_year_solstice = pd.Timestamp(year=year - 1, month=month, day=day, hour=12)

        return min(
            abs((timestamp - current_year_solstice).total_seconds()),
            abs((timestamp - next_year_solstice).total_seconds()),
            abs((timestamp - prev_year_solstice).total_seconds()),
        )

    def classify_date_split(
        self, df: pd.DataFrame, split_name: str, train_head: int, validation_head: int
    ) -> pd.DataFrame:
        """
        Classify the data according to the date.

        Parameters
        ----------
        df : pd.DataFrame
            The data frame to classify.
        split_name : str
            The name of the split.
        train_head : int
            The head values to consider in the training data.
        validation_head:
            The head values to consider in the validation data.

        Returns
        -------
        pd.DataFrame
            The data classified according to the date.
        """
        # Helper function to calculate distance to nearest Dec 21 and Jun 21

        # Calculate distances
        df[mappings.DECEMBER_DISTANCE] = df[mappings.CREATED_AT].apply(
            lambda x: self.nearest_solstice_distance(x, 12, 21)
        )
        df[mappings.JUNE_DISTANCE] = df[mappings.CREATED_AT].apply(
            lambda x: self.nearest_solstice_distance(x, 6, 21)
        )

        # Sort by distance
        df = df.sort_values(by=[mappings.DECEMBER_DISTANCE, mappings.CREATED_AT])
        train_indices = df.head(train_head).index

        df = df.sort_values(by=[mappings.JUNE_DISTANCE, mappings.CREATED_AT])
        validation_indices = df.head(validation_head).index

        # Assign split labels
        df[split_name] = mappings.TEST_INDEX
        df.loc[train_indices, split_name] = mappings.TRAIN_INDEX
        df.loc[validation_indices, split_name] = mappings.VALIDATION_INDEX

        return df[split_name]

    def plot_month_split(self):
        """Plot the month split."""
        for i, n in enumerate(self.number_of_train_samples):
            self.measurements_df[
                f"{mappings.DATA_SET_AZIMUTH}_{n}"
            ] = self.measurements_df.groupby(
                mappings.HELIOSTAT_ID, group_keys=False
            ).apply(
                lambda x: self.classify_date_split(
                    x,
                    f"{mappings.DATA_SET_AZIMUTH}_{n}",
                    n,
                    self.number_of_validation_samples,
                )
            )
            df = mark_insufficient_data_as_nan(
                self.measurements_df,
                f"{mappings.DATA_SET_AZIMUTH}_{n}",
                n,
                self.number_of_validation_samples,
            )
            split_counts_by_heliostat = (
                df.dropna(subset=[f"{mappings.DATA_SET_AZIMUTH}_{n}"])
                .groupby([mappings.HELIOSTAT_ID, f"{mappings.DATA_SET_AZIMUTH}_{n}"])
                .size()
                .unstack(fill_value=0)
            )
            example_heliostat_df = df[
                df[mappings.HELIOSTAT_ID] == self.default_example_heliostat
            ]  # chosen arbitrary heliostat but with good distribution
            plot_stacked_bar_chart_with_inset(
                split_counts_by_heliostat,
                example_heliostat_df,
                f"{mappings.DATA_SET_AZIMUTH}_{n}",
            )
        plt.tight_layout()
        plt.savefig(self.output_path / self.file_name, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_to_measurements",
        type=str,
        default="data/DatenHeliOS/calib_data.csv",
    )
    parser.add_argument(
        "--output_path", type=str, default=f"{PAINT_ROOT}/plots/saved_plots"
    )
    parser.add_argument("--number_of_train_samples", default=[10, 50, 100])
    parser.add_argument("--number_of_validation_samples", default=30)
    parser.add_argument("--default_example_heliostat", type=int, default=11447)
    parser.add_argument("--file_name", type=str, default="04_combined_plots")
    parser.add_argument("--save_as_pdf", action="store_true", default=True)
    args = parser.parse_args()

    plotter = DatasetMonthSplit(
        path_to_measurements=args.path_to_measurements,
        output_path=args.output_path,
        number_of_train_samples=args.number_of_train_samples,
        number_of_validation_samples=args.number_of_validation_samples,
        default_example_heliostat=args.default_example_heliostat,
        file_name=args.file_name,
        save_as_pdf=args.save_as_pdf,
    )
    plotter.plot_month_split()
