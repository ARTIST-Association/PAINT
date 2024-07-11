#!/usr/bin/env python

import argparse
import sys
from pathlib import Path
from typing import Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.utils import heliostat_id_to_heliostat_name


class HeliostatPositionPlot:
    """
    Load information on heliostat position and plot this information.

    Attributes
    ----------
    position_df : pd.DataFrame()
        The positions of the heliostats.
    count_df : pd.DataFrame()
        The counts of the heliostats.
    deflectometry_df : pd.DataFrame()
        The deflectometry data from the heliostats.
    output_path : Path
        The output path indicating where to save the plot.
    file_name : str
        The file name used to save the plot.

    Methods
    -------
    load_data()
        Load the data required for the plot.
    get_colour()
        Helper function to determine the colors for plotting the heliostat positions.
    plot_heliostat_positions()
        Plots the heliostat positions and saves this plot as PDF or PNG.
    """

    def __init__(
        self,
        path_to_positions: Union[str, Path],
        path_to_measurements: Union[str, Path],
        path_to_deflectometry: Union[str, Path],
        output_path: Union[str, Path],
        file_name: str = "heliostat_positions",
        save_as_pdf: bool = True,
    ) -> None:
        """
        Initialize the heliostat position plot object.

        Parameters
        ----------
        path_to_positions : Union[str, Path]
            The path to load the heliostat position data.
        path_to_measurements : Union[str, Path]
            The path to load the heliostat measurement data.
        path_to_deflectometry : Union[str, Path]
            The path to load the deflectometry data.
        output_path : Union[str, Path]
            The output path indicating where to save the plot.
        file_name : str
            The file name used to save the plot (default: "heliostat_positions").
        save_as_pdf : boolean
            Flag indicating whether to save the plot as a PDF or not (default: True).
        """
        self.position_df, self.count_df, self.deflectometry_df = self.load_data(
            path_to_positions=Path(path_to_positions),
            path_to_measurements=Path(path_to_measurements),
            path_to_deflectometry=Path(path_to_deflectometry),
        )
        self.output_path = Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        if save_as_pdf:
            self.file_name = file_name + ".pdf"
        else:
            self.file_name = file_name + ".png"

    @staticmethod
    def load_data(
        path_to_positions: Path, path_to_measurements: Path, path_to_deflectometry: Path
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load the data and return the data frames required to generate the heliostat position plot.

        Parameters
        ----------
        path_to_positions : Path
            The path to load the heliostat position data.
        path_to_measurements : Path
            The path to load the heliostat measurement data.
        path_to_deflectometry : Path
            The path to load the deflectometry data.

        Returns
        -------
        pd.DataFrame
            The positions of the heliostats.
        pd.DataFrame
            The counts of the heliostats.
        pd.DataFrame
            The deflectometry data from the heliostats.
        """
        # Load heliosat positions.
        df_heliostat_positions = pd.read_excel(path_to_positions, header=0)
        df_heliostat_positions.set_index(
            mappings.INTERNAL_NAME_INDEX, inplace=True
        )  # Set "InternalName" as the index
        df_heliostat_positions.rename_axis(
            mappings.HELIOSTAT_ID, inplace=True
        )  # Rename the index
        df_heliostat_positions = df_heliostat_positions[mappings.X_Y_Z_POSITIONS]

        # Load measurements
        df_measurements = pd.read_csv(path_to_measurements)
        df_measurements = df_measurements.set_index(
            mappings.ID_INDEX
        )  # Set df id as index
        # Get all existing heliostat IDs and their entry counts
        heliostat_counts = df_measurements[mappings.HELIOSTAT_ID].value_counts()
        # Replace HeliostatId with heliostat names in heliostat_counts dataframe
        heliostat_counts.index = heliostat_counts.index.map(
            heliostat_id_to_heliostat_name
        )

        # Load deflectometry availability from file
        df_deflectometry = pd.read_excel(path_to_deflectometry)
        df_deflectometry.set_index(
            mappings.INTERNAL_NAME_INDEX, inplace=True
        )  # Set "InternalName" as the index

        return df_heliostat_positions, heliostat_counts, df_deflectometry

    @staticmethod
    def get_color(surface_measurement: float) -> str:
        """
        Determine the color to be used for the plot based on the measured surface values.

        Parameters
        ----------
        surface_measurement : float
            The measured surface value from the deflectometry data.

        Returns
        -------
            The desired color for the plot.
        """
        if surface_measurement > 95:
            return_value = "green"
        elif surface_measurement >= 90:
            return_value = "indigo"
        else:
            return_value = "sienna"
        return return_value

    def plot_heliostat_positions(self):
        """Generate the heliostat position plot."""
        # Merge positions and heliostat counts
        merged_df = pd.merge(
            self.position_df,
            self.count_df,
            left_index=True,
            right_index=True,
        )

        # Create a list of Internal names where "DeflectometryAvailable" is True
        highlighted_heliostats = self.deflectometry_df.index[
            ~self.deflectometry_df[mappings.DEFLECTOMETRY_AVAILABLE].isna()
        ].tolist()

        # Add a column to identify highlighted heliostats
        merged_df["highlight"] = merged_df.index.isin(highlighted_heliostats)

        # Map MeasuredSurface values to colors

        # Add a column for color based on MeasuredSurface
        merged_df["color"] = self.deflectometry_df[mappings.MEASURED_SURFACE].map(
            self.get_color
        )

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(
            merged_df["x"],
            merged_df["y"],
            c=merged_df["count"],
            cmap="coolwarm",
            alpha=0.7,
        )

        # Highlight specific heliostats with colors
        percentage_labels = {
            "green": ">95% accuracy",
            "indigo": "90%-95% accuracy",
            "sienna": "<90% accuracy",
        }
        for color, label in percentage_labels.items():
            subset = merged_df[merged_df["color"] == color]
            plt.plot(
                subset["x"],
                subset["y"],
                "o",
                markerfacecolor="none",
                markeredgecolor=color,
                markersize=7,
                label=label,
            )

        plt.colorbar(label="# Measurements")
        plt.xlabel("East-West distance to tower")
        plt.ylabel("North distance to tower")
        plt.grid(True)

        # Add square at (0, 0)
        rect = Rectangle(
            (-5, -8), 10, 8, linewidth=2, edgecolor="darkgrey", facecolor="grey"
        )
        plt.gca().add_patch(rect)

        # Add square at (-17.5, 0)
        rect = Rectangle(
            (-22.5, -8), 10, 8, linewidth=2, edgecolor="black", facecolor="grey"
        )
        plt.gca().add_patch(rect)

        y_min = -8  # Define your desired minimum y-value
        y_max = 250
        plt.ylim(y_min, y_max)
        plt.tight_layout()
        plt.legend(title="Accuracy of available\ndeflectometry data:")
        plt.savefig(self.output_path / self.file_name, dpi=300)


if __name__ == "__main__":
    sys.argv = ["heliostat_position.py", 
                "--path_to_positions", "data/Heliostatpositionen_xyz.xlsx", 
                "--path_to_measurements", "data/calib_data.csv", 
                "--path_to_deflectometry", "data/deflec_availability.xlsx", 
                "--output_path", "plots/saved_plots", 
                "--file_name", "01_heliostat_positions"]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_to_positions",
        type=str,
        default=f"{PAINT_ROOT}/ExampleDataKIT/Heliostatpositionen_xyz.xlsx",
    )
    parser.add_argument(
        "--path_to_measurements",
        type=str,
        default=f"{PAINT_ROOT}/ExampleDataKIT/dataframe.csv",
    )
    parser.add_argument(
        "--path_to_deflectometry",
        type=str,
        default=f"{PAINT_ROOT}/ExampleDataKIT/deflec_availability.xlsx",
    )
    parser.add_argument(
        "--output_path", type=str, default=f"{PAINT_ROOT}/plots/saved_plots"
    )
    parser.add_argument("--file_name", type=str, default="01_heliostat_positions")
    parser.add_argument("--save_as_pdf", action="store_true", default=True)
    args = parser.parse_args()

    plotter = HeliostatPositionPlot(
        path_to_positions=args.path_to_positions,
        path_to_measurements=args.path_to_measurements,
        path_to_deflectometry=args.path_to_deflectometry,
        output_path=args.output_path,
        file_name=args.file_name,
        save_as_pdf=args.save_as_pdf,
    )
    plotter.plot_heliostat_positions()
