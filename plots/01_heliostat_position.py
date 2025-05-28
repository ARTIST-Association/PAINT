#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from typing import Dict, Union

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from plot_utils import decimal_to_dms, set_plot_style

import paint.util.paint_mappings as mappings


class HeliostatPositionPlot:
    """
    Load information on heliostat position and plot this information.

    Attributes
    ----------
    position_df : pandas.DataFrame
        The heliostats' positions.
    count_df : pandas.Series
        The count of measurements per heliostat.
    deflectometry_df : pandas.DataFrame
        The deflectometry data for heliostats.
    deflectometry_heliostats : pandas.Index
        The index of heliostats with deflectometry data.
    tower_data : dict
        The tower properties data loaded from JSON.
    juelich_tower : dict
        The calculated dimensions and positions for the Jülich tower.
    multi_focus_tower : dict
        The calculated dimensions and positions for the Multi-Focus tower.
    lat_ref : str
        The reference latitude in DMS format.
    lon_ref : str
        The reference longitude in DMS format.
    lat_ref_main : str
        The main reference latitude in DMS format with 'N' suffix.
    lon_ref_main : str
        The main reference longitude in DMS format with 'E' suffix.
    output_path : pathlib.Path
        The path where the plot will be saved.
    file_name : str
        The name of the output file.
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
            The path to load the heliostat position data.
        path_to_measurements : Union[str, Path]
            The path to load the heliostat measurement data.
        path_to_deflectometry : Union[str, Path]
            The path to load the deflectometry data.
        output_path : Union[str, Path]
            The output path indicating where to save the plot.
        file_name : str
            The file name used to save the plot (Default: "heliostat_positions").
        save_as_pdf : bool
            Whether to save the plot as a PDF or not (Default: True).
        """
        # Set plot style.
        set_plot_style()
        # Load heliostat positions and set the index using the mapping constant.
        try:
            df_positions = pd.read_csv(Path(path_to_positions), header=0)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {path_to_positions}")
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV file is empty: {path_to_positions}")
        df_positions.set_index(mappings.HELIOSTAT_ID, inplace=True)
        # Use the mapping list for the positions columns.
        self.position_df = df_positions[mappings.HELIOSTAT_POSITIONS].copy()

        # Load measurements, set the index, and count the number of measurements per heliostat.
        df_measurements = pd.read_csv(Path(path_to_measurements))
        df_measurements.set_index(mappings.ID_INDEX, inplace=True)
        count_df_temp = df_measurements[mappings.HELIOSTAT_ID].value_counts()
        self.count_df = count_df_temp.reindex(self.position_df.index, fill_value=0)

        # Load deflectometry data and set its index.
        df_deflectometry = pd.read_csv(Path(path_to_deflectometry))
        df_deflectometry.set_index(mappings.HELIOSTAT_ID, inplace=True)
        self.deflectometry_df = df_deflectometry
        self.deflectometry_heliostats = df_deflectometry.index.unique()

        # Load tower properties JSON.
        with Path(path_to_tower_properties).open("r", encoding="utf-8") as f:
            self.tower_data = json.load(f)

        # Use the mapping constants for tower keys:
        self.juelich_tower = self._calculate_tower_dimensions(
            self.tower_data[mappings.STJ_UPPER][mappings.TOWER_COORDINATES_KEY]
        )
        self.multi_focus_tower = self._calculate_tower_dimensions(
            self.tower_data[mappings.MFT][mappings.TOWER_COORDINATES_KEY]
        )

        # Add the measurement count as a new column.
        self.position_df = self.position_df.copy()
        self.position_df["count"] = self.count_df

        # Calculate reference coordinates using the mapped latitude and longitude keys.
        self.lat_ref = decimal_to_dms(
            self.position_df[mappings.LATITUDE_KEY].mean(), is_latitude=True
        )
        self.lon_ref = decimal_to_dms(
            self.position_df[mappings.LONGITUDE_KEY].mean(), is_latitude=False
        )
        self.lat_ref_main = " ".join(self.lat_ref.split()[:3]) + " N"
        self.lon_ref_main = " ".join(self.lon_ref.split()[:3]) + " E"

        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.file_name = file_name + (".pdf" if save_as_pdf else ".png")

    @staticmethod
    def _calculate_tower_dimensions(
        coordinates: Dict[str, list[float]],
    ) -> Dict[str, list[float]]:
        """Calculate the width, height, and position for a tower."""
        center = coordinates[mappings.CENTER]
        upper_left = coordinates[mappings.UPPER_LEFT]
        upper_right = coordinates[mappings.UPPER_RIGHT]

        width = abs(upper_right[1] - upper_left[1])
        height = 2 * abs(center[0] - upper_left[0])

        return {
            mappings.CENTER: center,
            mappings.UPPER_LEFT: upper_left,
            mappings.UPPER_RIGHT: upper_right,
            "width": [width],
            "height": [height],
        }

    def plot_heliostat_positions(self) -> None:
        """Generate the heliostat position plot."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create a custom cmap.
        blues = plt.get_cmap("Blues")
        darker_blues = blues(np.linspace(0.3, 1, 256))
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "ModifiedBlues", darker_blues
        )

        # Plot heliostat positions using the longitude and latitude keys from the mappings.
        scatter = ax.scatter(
            self.position_df[mappings.LONGITUDE_KEY],
            self.position_df[mappings.LATITUDE_KEY],
            c=self.position_df["count"],
            cmap=custom_cmap,
            alpha=0.7,
        )
        fig.colorbar(scatter, label="# Measurements")
        ax.grid(True)

        # Draw tower boundaries as rectangles.
        for tower, color, label in [
            (self.juelich_tower, "black", "Jülich Tower"),
            (self.multi_focus_tower, "darkgrey", "Multi-Focus Tower"),
        ]:
            ax.add_patch(
                Rectangle(
                    (
                        tower[mappings.UPPER_LEFT][1],
                        tower[mappings.CENTER][0] - tower["height"][0] / 2,
                    ),
                    tower["width"][0],
                    tower["height"][0],
                    linewidth=8,
                    edgecolor=color,
                    facecolor="none",
                    label=label,
                )
            )

        # Highlight heliostats that have deflectometry data.
        highlighted_df = self.position_df[
            self.position_df.index.isin(self.deflectometry_heliostats)
        ]
        ax.scatter(
            highlighted_df[mappings.LONGITUDE_KEY],
            highlighted_df[mappings.LATITUDE_KEY],
            facecolors="none",
            edgecolors="red",
            s=50,
            label="Deflectometry Available",
        )

        ax.set_xlabel(f"Longitude ({self.lon_ref_main})")
        ax.set_ylabel(f"Latitude ({self.lat_ref_main})")
        ax.legend(loc="lower left")
        fig.tight_layout()
        fig.savefig(self.output_path / self.file_name, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path_to_positions",
        type=str,
    )
    parser.add_argument(
        "--path_to_measurements",
        type=str,
    )
    parser.add_argument(
        "--path_to_deflectometry",
        type=str,
    )
    parser.add_argument(
        "--path_to_tower_properties",
        type=str,
    )
    parser.add_argument("--output_path", type=str, default="saved_plots")
    parser.add_argument("--file_name", type=str, default="01_heliostat_positions")
    parser.add_argument("--save_as_pdf", action="store_true", default=True)
    args = parser.parse_args()
    config = vars(args)

    plotter = HeliostatPositionPlot(**config)
    plotter.plot_heliostat_positions()
