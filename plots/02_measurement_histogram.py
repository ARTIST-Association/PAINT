#!/usr/bin/env python

import argparse
from pathlib import Path
from typing import Union

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import calculate_azimuth_and_elevation


class HistogramMeasurementPlot:
    """
    Load heliostat measurements and plot this as a histogram.

    Attributes
    ----------
    measurements_df : pd.DataFrame
        The measurement data.
    output_path : Union[Path, str]
        The path to the output directory to save the plots.
    columns_to_consider : list[str]
        The columns to include in the histogram plot.
    joint_columns : list[str]
        The columns to consider in the joint histogram plot.
    base_file_name : str
        The base file name used to generate plot names.
    save_as_pdf : bool
        Indicates if the output should be saved as PDF (Default: True).

    Methods
    -------
    load_data()
        Load data and include time features.
    create_histogram()
        Create a single histogram.
    create_stacked_bar_chart()
        Create a stacked bar chart.
    create_and_save_joint_plot()
        Create joint histograms and save in the specified output directory.
    plot_measurement_histograms()
        Plot all histograms and save in the specified output directory.
    """

    def __init__(
        self,
        path_to_measurements: Union[Path, str],
        output_path: Union[str, Path],
        columns_to_consider: list[str],
        joint_columns: list[str],
        base_file_name: str = "02_histograms",
        save_as_pdf: bool = True,
    ) -> None:
        """
        Initialize the histogram measurement plot object.

        Parameters
        ----------
        path_to_measurements : Union[Path, str]
            The path to the measurement data.
        output_path : Union[Path, str]
            The path to the output directory to save the plots.
        columns_to_consider : list[str]
            The columns to include in the histogram plot.
        joint_columns : list[str]
            The columns to consider in the joint histogram plot.
        base_file_name : str
            The base file name used to generate plot names.
        save_as_pdf : bool
            Indicates if the output should be saved as PDF (Default: True).
        """
        self.measurements_df = self.load_data(Path(path_to_measurements))
        self.output_path = Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        self.columns_to_consider = columns_to_consider
        self.joint_columns = joint_columns
        self.base_file_name = base_file_name
        self.save_as_pdf = save_as_pdf

    @staticmethod
    def load_data(path_to_measurements: Path) -> pd.DataFrame:
        """
        Load the data and include additional time features.

        Parameters
        ----------
        path_to_measurements : Path
            The path to the measurement data.

        Returns
        -------
        pd.DataFrame
            The loaded data with additional time features.
        """
        measurements_df = pd.read_csv(path_to_measurements).set_index(mappings.ID_INDEX)
        measurements_df[mappings.CREATED_AT] = pd.to_datetime(
            measurements_df[mappings.CREATED_AT]
        )
        measurements_df[mappings.YEAR] = measurements_df[mappings.CREATED_AT].dt.year
        measurements_df[mappings.MONTH], measurements_df[mappings.HOUR] = (
            measurements_df[mappings.CREATED_AT].dt.month,
            measurements_df[mappings.CREATED_AT].dt.hour,
        )
        # Calculate Azimuth and Elevation
        (
            measurements_df[mappings.AZIMUTH],
            measurements_df[mappings.ELEVATION],
        ) = calculate_azimuth_and_elevation(measurements_df)

        return measurements_df

    @staticmethod
    def create_histogram(
        ax: Axes,
        df: pd.DataFrame,
        column: str,
        bins: int = 20,
        x_ticks: Union[list[str], None] = None,
    ) -> Axes:
        """
        Generate a histogram plot based on a given axis and data.

        Parameters
        ----------
        ax : Axes
            The axis used to plot the histogram.
        df : pd.DataFrame
            The data to plot.
        column : str
            The column from the data to plot.
        bins : int
            The number of bins to use in the histogram (Default: 20).
        x_ticks : list[str], optional
            Labels to use for the x-ticks.

        Returns
        -------
        ax : Axes
            The axes containing the histogram plot.
        """
        ax.hist(df[column], bins=bins, color="skyblue", edgecolor="black")
        ax.set_title(f"Histogram of {column}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        ax.grid(True)
        if x_ticks:
            ax.set_xticks(np.arange(len(x_ticks)))
            ax.set_xticklabels(x_ticks)

        return ax

    @staticmethod
    def create_stacked_bar_chart(
        ax: Axes,
        df: pd.DataFrame,
        time_column: str,
        x_ticks: Union[list[str], None] = None,
    ) -> Axes:
        """
        Generate a stacked bar chart based on given axis and data.

        Parameters
        ----------
        ax : Axes
            The axis used to plot the histogram.
        df : pd.DataFrame
            The data to plot.
        time_column : str
            The time column from the data to use in the plot.
        x_ticks : list[str], optional
            Labels to use for the x-ticks.

        Returns
        -------
        ax : Axes
            The axes containing the stacked bar chart.
        """
        pivot_table = df.pivot_table(
            index=time_column, columns="Year", aggfunc="size", fill_value=0
        )
        pivot_table.plot(
            kind="bar", stacked=True, ax=ax, figsize=(10, 7), colormap="tab10"
        )
        ax.set_xlabel(time_column)
        ax.set_ylabel("Count")
        ax.grid(True)
        if x_ticks:
            ax.set_xticks(np.arange(len(x_ticks)))
            ax.set_xticklabels(x_ticks)
        ax.legend(title="Year")
        return ax

    def create_and_save_joint_plot(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        width: int,
        height: int,
        x_lim: Union[tuple[float, float], None] = None,
        y_lim: Union[tuple[float, float], None] = None,
    ) -> None:
        """
        Generate a joint plot based on two columns in the data.

        Parameters
        ----------
        df : pd.DataFrame
            The data to plot.
        x_column : str
            The column to consider for the x-axis of the plot.
        y_column : str
            The column to consider for the y-axis of the plot.
        width : int
            The width of the figure.
        height : int
            The height of the figure.
        x_lim : Tuple[float, float], optional
            The x-axis limits.
        y_lim : Tuple[float, float], optional
            The y-axis limits.
        """
        grid = sns.jointplot(
            x=x_column,
            y=y_column,
            data=df,
            kind="kde",
            color="skyblue",
            height=12,
            ratio=8,
            xlim=x_lim,
            ylim=y_lim,
            gridsize=100,
        )
        grid.fig.set_figwidth(width)
        grid.fig.set_figheight(height)
        if self.save_as_pdf:
            save_name = self.base_file_name + f"joint_plot_{x_column}_{y_column}.pdf"
        else:
            save_name = self.base_file_name + f"joint_plot_{x_column}_{y_column}.png"
        grid.savefig(self.output_path / save_name, dpi=300)

    def plot_measurement_histograms(self) -> None:
        """Create and save the measurement histogram plots."""
        # Create a main figure with gridspec
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(2, 2, figure=fig)

        # Create individual histograms for specified columns
        for i, column in enumerate(self.columns_to_consider):
            ax = fig.add_subplot(gs[i])
            self.create_histogram(ax=ax, df=self.measurements_df, column=column)
            ax.set_title(f"Histogram of {column}")

        # Create stacked bar charts
        ax_stacked_month = fig.add_subplot(gs[1, 0])
        self.create_stacked_bar_chart(
            ax=ax_stacked_month,
            df=self.measurements_df,
            time_column="Month",
            x_ticks=[
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
        )
        ax_stacked_hour = fig.add_subplot(gs[1, 1])
        self.create_stacked_bar_chart(
            ax=ax_stacked_hour, df=self.measurements_df, time_column=mappings.HOUR
        )

        plt.tight_layout()
        if self.save_as_pdf:
            save_name = self.base_file_name + ".pdf"
        else:
            save_name = self.base_file_name + ".png"

        plt.savefig(self.output_path / save_name, dpi=300)  # Save the combined figure

        # create_joint_plot(self.measurements_df, 'Azimuth', 'Elevation', width=10, height=10)
        self.create_and_save_joint_plot(
            df=self.measurements_df,
            x_column=self.joint_columns[0],
            y_column=self.joint_columns[1],
            width=10,
            height=10,
            x_lim=(-20, 3),
            y_lim=(121, 140),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_to_measurements",
        type=str,
        default=r"/workVERLEIHNIX/share/PAINT/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--output_path", type=str, default=f"{PAINT_ROOT}/plots/saved_plots"
    )
    parser.add_argument(
        "--columns_to_consider", default=["Axis1MotorPosition", "Axis2MotorPosition"]
    )
    parser.add_argument("--joint_columns", default=["TargetOffsetE", "TargetOffsetU"])
    parser.add_argument("--base_file_name", type=str, default="02_histograms")
    parser.add_argument("--save_as_pdf", action="store_true", default=True)
    args = parser.parse_args()

    plotter = HistogramMeasurementPlot(
        path_to_measurements=args.path_to_measurements,
        output_path=args.output_path,
        columns_to_consider=args.columns_to_consider,
        joint_columns=args.joint_columns,
        base_file_name=args.base_file_name,
        save_as_pdf=args.save_as_pdf,
    )
    plotter.plot_measurement_histograms()
