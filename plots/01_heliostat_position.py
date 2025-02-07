#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from typing import Dict

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
    position_df : pandas.DataFrame
        The heliostats' positions.
    count_df : pandas.DataFrame
        The heliostats' counts.

    Methods
    -------
    load_data(path_to_positions, path_to_measurements, ...)
        Loads the required CSV files and extracts necessary data.
    plot_heliostat_positions()
        Plots the heliostat positions with overlays for deflectometry and towers.
    """


    def __init__(
        self,
        path_to_positions: str | Path,
        path_to_measurements: str | Path,
        path_to_deflectometry: str | Path,
        path_to_tower_properties: str | Path,
        output_path: str | Path,
        file_name: str = "heliostat_positions",
        save_as_pdf: bool = True,
    ) -> None:
        """
        Initialize the heliostat position plot object.
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
        """
        # Load heliostat positions and set the index using the mapping constant.
        try:
            df_positions = pd.read_csv(path_to_positions, header=0)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {path_to_positions}")
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV file is empty: {path_to_positions}")
        df_positions.set_index(mappings.HELIOSTAT_ID, inplace=True)
        # Use the mapping list for the positions columns.
        self.position_df = df_positions[mappings.HELIOSTAT_POSITIONS].copy()

        # Load measurements, set the index, and count the number of measurements per heliostat.
        df_measurements = pd.read_csv(path_to_measurements)
        df_measurements.set_index(mappings.ID_INDEX, inplace=True)
        self.count_df = df_measurements[mappings.HELIOSTAT_ID].value_counts()

        # Load deflectometry data and set its index.
        df_deflectometry = pd.read_csv(path_to_deflectometry)
        df_deflectometry.set_index(mappings.HELIOSTAT_ID, inplace=True)
        self.deflectometry_df = df_deflectometry
        self.deflectometry_heliostats = df_deflectometry.index.unique()

        # Load tower properties JSON.
        with path_to_tower_properties.open("r", encoding="utf-8") as f:
            self.tower_data = json.load(f)

        # Use the mapping constants for tower keys:
        self.juelich_tower = self._calculate_tower_dimensions(
            self.tower_data[mappings.STJ_UPPER]["coordinates"]
        )
        self.multi_focus_tower = self._calculate_tower_dimensions(
            self.tower_data[mappings.MFT]["coordinates"]
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

    @staticmethod
    def _calculate_tower_dimensions(coordinates: Dict[str, list[float]]) -> Dict[str, float]:
        """
        Calculate the width, height, and position for a tower.
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
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot heliostat positions using the longitude and latitude keys from the mappings.
        scatter = ax.scatter(
            self.position_df[mappings.LONGITUDE_KEY],
            self.position_df[mappings.LATITUDE_KEY],
            c=self.position_df["count"],
            cmap="coolwarm",
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
                    (tower["upper_left"][1], tower["center"][0] - tower["height"] / 2),
                    tower["width"],
                    tower["height"],
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
        default="PATH/TO/properties_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_measurements",
        type=str,
        default="PATH/TO/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_deflectometry",
        type=str,
        default="PATH/TO/deflectometry_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--path_to_tower_properties",
        type=str,
        default="PATH/TO/WRI1030197-tower-measurements.json",
    )
    parser.add_argument("--output_path", type=str, default="plots/saved_plots")
    parser.add_argument("--file_name", type=str, default="01_heliostat_positions")
    parser.add_argument("--save_as_pdf", action="store_true")
    args = parser.parse_args()

    plotter = HeliostatPositionPlot(**vars(args))
    plotter.plot_heliostat_positions()
