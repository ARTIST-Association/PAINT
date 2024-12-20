#!/usr/bin/env python

import argparse
import json
from pathlib import Path
from typing import Tuple, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.patches import Rectangle

import paint.util.paint_mappings as mappings
from plot_utils import decimal_to_dms


class HeliostatPositionPlot:
    """
    Load information on heliostat position and plot this information.

    Attributes
    ----------
    position_df : pd.DataFrame
        The heliostats' positions.
    count_df : pd.DataFrame
        The heliostats' counts.
    deflectometry_df : pd.DataFrame
        The heliostats' deflectometry data.
    output_path : Path
        The output path indicating where to save the plot.
    file_name : str
        The file name used to save the plot.

    Methods
    -------
    load_data()
        Load the data required for the plot.
    _calculate_tower_dimensions()
        Calculate the dimensions for a tower.
    plot_heliostat_positions()
        Plot the heliostat positions and save this plot as PDF or PNG.
    """

    def __init__(
        self,
        path_to_positions: Union[str, Path],
        path_to_measurements: Union[str, Path],
        path_to_deflectometry: Union[str, Path],
        path_to_tower_properties: Union[str, Path],
        output_path: Union[str, Path],
        file_name: str = "heliostat_positions",
        save_as_pdf: bool = True,
    ) -> None:
        """
        Initialize the heliostat position plot object.

        Parameters
        ----------
        path_to_positions : Union[str, Path]
            The path to load the heliostat position data from.
        path_to_measurements : Union[str, Path]
            The path to load the heliostat measurement data from.
        path_to_deflectometry : Union[str, Path]
            The path to load the deflectometry data from.
        path_to_tower_properties : Union[str, Path]
            The path to load the tower properties data from.
        output_path : Union[str, Path]
            The output path indicating where to save the plot.
        file_name : str
            The file name used to save the plot.
        save_as_pdf : bool
            Whether to save the plot as a PDF or not.
        """
        self.load_data(
            path_to_positions=Path(path_to_positions),
            path_to_measurements=Path(path_to_measurements),
            path_to_deflectometry=Path(path_to_deflectometry),
            path_to_tower_properties=Path(path_to_tower_properties),
        )
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.file_name = file_name + (".pdf" if save_as_pdf else ".png")

    def load_data(
        self,
        path_to_positions: Path,
        path_to_measurements: Path,
        path_to_deflectometry: Path,
        path_to_tower_properties: Path,
    ) -> None:
        """
        Load the data and save as instance attributes.

        Parameters
        ----------
        path_to_positions : Path
            Path to the heliostat position data.
        path_to_measurements : Path
            Path to the heliostat measurement data.
        path_to_deflectometry : Path
            Path to the deflectometry data.
        path_to_tower_properties : Path
            Path to the tower properties JSON file.
        """
        df_positions = pd.read_csv(path_to_positions, header=0)
        df_positions.set_index(mappings.HELIOSTAT_ID, inplace=True)
        self.position_df = df_positions[mappings.HELIOSTAT_POSITIONS]

        df_measurements = pd.read_csv(path_to_measurements)
        df_measurements.set_index(mappings.ID_INDEX, inplace=True)
        self.count_df = df_measurements[mappings.HELIOSTAT_ID].value_counts()

        df_deflectometry = pd.read_csv(path_to_deflectometry)
        df_deflectometry.set_index(mappings.HELIOSTAT_ID, inplace=True)
        self.deflectometry_df = df_deflectometry
        self.deflectometry_heliostats = df_deflectometry.index.unique()

        with open(path_to_tower_properties, "r") as f:
            self.tower_data = json.load(f)

        self.juelich_tower = self._calculate_tower_dimensions(
            self.tower_data["solar_tower_juelich_upper"]["coordinates"]
        )
        self.multi_focus_tower = self._calculate_tower_dimensions(
            self.tower_data["multi_focus_tower"]["coordinates"]
        )

        self.merged_df = pd.merge(
            self.position_df,
            self.count_df,
            left_index=True,
            right_index=True,
        )

        self.lat_ref = decimal_to_dms(
            self.merged_df["latitude"].mean(), is_latitude=True
        )
        self.lon_ref = decimal_to_dms(
            self.merged_df["longitude"].mean(), is_latitude=False
        )
        self.lat_ref_main = " ".join(self.lat_ref.split()[:3]) + " N"
        self.lon_ref_main = " ".join(self.lon_ref.split()[:3]) + " E"

    @staticmethod
    def _calculate_tower_dimensions(coordinates: dict) -> dict:
        """
        Calculate the width, height, and position for a tower.

        Parameters
        ----------
        coordinates : dict
            The coordinates of the tower.

        Returns
        -------
        dict
            Dictionary containing the calculated dimensions and position.
        """
        center = coordinates["center"]
        upper_left = coordinates["upper_left"]
        upper_right = coordinates["upper_right"]

        width = abs(upper_right[1] - upper_left[1])
        height = 2 * abs(center[0] - upper_left[0])

        return {
            "center": center,
            "upper_left": upper_left,
            "upper_right": upper_right,
            "width": width,
            "height": height,
        }

    def plot_heliostat_positions(self) -> None:
        """
        Generate the heliostat position plot.
        """
        plt.figure(figsize=(10, 6))

        scatter = plt.scatter(
            self.merged_df["longitude"],
            self.merged_df["latitude"],
            c=self.merged_df["count"],
            cmap="coolwarm",
            alpha=0.7,
        )
        plt.colorbar(scatter, label="# Measurements")
        plt.grid(True)

        ax = plt.gca()

        juelich = self.juelich_tower
        ax.add_patch(
            Rectangle(
                (juelich["upper_left"][1], juelich["center"][0] - juelich["height"] / 2),
                juelich["width"],
                juelich["height"],
                linewidth=8,
                edgecolor="black",
                facecolor="none",
                label="Jülich Tower",
            )
        )

        multi_focus = self.multi_focus_tower
        ax.add_patch(
            Rectangle(
                (
                    multi_focus["upper_left"][1],
                    multi_focus["center"][0] - multi_focus["height"] / 2,
                ),
                multi_focus["width"],
                multi_focus["height"],
                linewidth=8,
                edgecolor="darkgrey",
                facecolor="none",
                label="Multi-Focus Tower",
            )
        )

        highlighted_df = self.merged_df[
            self.merged_df.index.isin(self.deflectometry_heliostats)
        ]
        plt.plot(
            highlighted_df["longitude"],
            highlighted_df["latitude"],
            "o",
            markerfacecolor="none",
            markeredgecolor="red",
            markersize=6.5,
            label="Deflectometry Available",
        )

        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda y, _: f"{int((abs(y) % 1) * 3600)}''")
        )
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{int((abs(x) % 1) * 3600)}''")
        )
        plt.xlabel(f"Longitude ({self.lon_ref_main})")
        plt.ylabel(f"Latitude ({self.lat_ref_main})")
        plt.legend(loc="lower left")
        plt.tight_layout()
        plt.savefig(self.output_path / self.file_name, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path_to_positions",
        type=str,
        default="/workVERLEIHNIX/share/PAINT/metadata/properties_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_measurements",
        type=str,
        default="/workVERLEIHNIX/share/PAINT/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_deflectometry",
        type=str,
        default="/workVERLEIHNIX/share/PAINT/metadata/deflectometry_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_tower_properties",
        type=str,
        default="/workVERLEIHNIX/share/PAINT/WRI1030197-tower-measurements.json",
    )
    parser.add_argument("--output_path", type=str, default="plots/saved_plots")
    parser.add_argument("--file_name", type=str, default="01_heliostat_positions")
    parser.add_argument("--save_as_pdf", action="store_true", default=True)
    args = parser.parse_args()

    plotter = HeliostatPositionPlot(
        path_to_positions=args.path_to_positions,
        path_to_measurements=args.path_to_measurements,
        path_to_deflectometry=args.path_to_deflectometry,
        path_to_tower_properties=args.path_to_tower_properties,
        output_path=args.output_path,
        file_name=args.file_name,
        save_as_pdf=args.save_as_pdf,
    )
    plotter.plot_heliostat_positions()
