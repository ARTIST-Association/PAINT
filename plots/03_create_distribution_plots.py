#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from typing import List, Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from plot_utils import convert_wgs84_coordinates_to_local_enu

import paint.util.paint_mappings as mappings

# Global plot settings
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["DejaVu Sans"]
mpl.rcParams["font.size"] = 12
mpl.rcParams["axes.titlesize"] = 14
mpl.rcParams["axes.labelsize"] = 12
mpl.rcParams["axes.labelweight"] = "bold"
mpl.rcParams["xtick.labelsize"] = 10
mpl.rcParams["ytick.labelsize"] = 10

# Power plant position as tensor
power_plant_position = torch.tensor(
    [mappings.POWER_PLANT_LAT, mappings.POWER_PLANT_LON, mappings.POWER_PLANT_ALT]
)


class ConditionDistributionPlot:
    """
    Plot the sun azimuth/elevation and aim point distributions.

    Attributes
    ----------
    path_to_data_directory : pathlib.Path
        Path to the data directory.
    path_to_metadata : pathlib.Path
        Path to the metadata JSON file.
    output_path : pathlib.Path
        Path where plots will be saved.
    figure_size : tuple[float]
        Size of the figures used for plotting.
    data : pandas.DataFrame
        Loaded condition data for plotting.
    receiver_coordinates : list[torch.Tensor]
        Receiver corner coordinates transformed to local ENU coordinates.
    """

    # Class constants for styling and layout
    L_MARKER_SIZE_STJ: float = 0.5
    L_MARKER_SIZE_MFT: float = 0.5
    T_MARKER_SIZE: float = 0.5
    LABEL_OFFSET: float = 1.0
    HEXBIN_XLIMS: List[float] = [-23.65, 7.68]
    HEXBIN_YLIMS: List[float] = [29, 61]

    def __init__(
        self,
        path_to_data_directory: Union[str, Path],
        path_to_metadata: Union[str, Path],
        output_path: Union[str, Path],
    ) -> None:
        """
        Initialize the ConditionDistributionPlot instance by setting paths.

        Parameters
        ----------
        path_to_data_directory : Union[str,Path]
            Path to the directory containing the condition data files.

        path_to_metadata : Union[str,Path]
            Path to the JSON metadata file with calibration information.

        output_path : Union[str,Path]
            Directory where plots will be saved.
        """
        self.path_to_metadata = Path(path_to_metadata)
        self.path_to_data_directory = Path(path_to_data_directory)
        self.output_path = Path(output_path)

        self.output_path.mkdir(parents=True, exist_ok=True)

        self.figure_size = (4, 4)
        self.data = self._load_data()

        # Precompute receiver corners once
        self.receiver_coordinates = [
            convert_wgs84_coordinates_to_local_enu(
                torch.tensor(coords), power_plant_position
            )
            for coords in mappings.RECEIVER_COORDINATES
        ]

    def _load_data(self) -> pd.DataFrame:
        """Load calibration data and extract focal spot centers in local ENU coordinates for plotting."""
        calibration_data = pd.read_csv(self.path_to_metadata)

        # Create empty columns for extracted centers
        calibration_data["FocalSpotCenterE"] = np.nan
        calibration_data["FocalSpotCenterN"] = np.nan
        calibration_data["FocalSpotCenterU"] = np.nan

        # Prepare a fast lookup for ID to row index
        id_to_index = {
            id_: idx for idx, id_ in calibration_data[mappings.ID_INDEX].items()
        }

        for row in calibration_data[
            [mappings.ID_INDEX, mappings.HELIOSTAT_ID]
        ].itertuples(index=False):
            heliostat_id = row.HeliostatId
            id_ = row.Id
            path = (
                self.path_to_data_directory
                / heliostat_id
                / mappings.SAVE_CALIBRATION
                / f"{id_}{mappings.CALIBRATION_PROPERTIES_IDENTIFIER}"
            )

            try:
                with open(path, "r") as file:
                    calibration_dict = json.load(file)
                    center = torch.tensor(
                        calibration_dict[mappings.FOCAL_SPOT_KEY][mappings.HELIOS_KEY]
                    )
                    center_enu = convert_wgs84_coordinates_to_local_enu(
                        center, power_plant_position
                    )

                    idx = id_to_index[id_]
                    calibration_data.at[idx, "FocalSpotCenterE"] = float(center_enu[0])
                    calibration_data.at[idx, "FocalSpotCenterN"] = float(center_enu[1])
                    calibration_data.at[idx, "FocalSpotCenterU"] = float(center_enu[2])
            except FileNotFoundError:
                print(f"Warning: File {path} not found.")
                continue

        return calibration_data

    def plot_sun_positions(self) -> None:
        """Plot sun azimuth versus elevation."""
        sns.set_context("notebook", rc={"figure.figsize": self.figure_size})

        joint_plot = sns.jointplot(
            data=self.data, x="Azimuth", y="Elevation", kind="hex"
        )
        joint_plot.set_axis_labels("Sun azimuth / degree", "Sun elevation / degree")

        joint_plot.ax_joint.set_axisbelow(False)
        joint_plot.ax_joint.grid(True, zorder=2)
        joint_plot.ax_joint.collections[0].set_zorder(1)

        file_name = "03_sun_position_distribution"
        self._save_plot(joint_plot.fig, file_name)

    def plot_target_offsets(self) -> None:
        """Plot target offset aim points."""
        g = sns.jointplot(
            data=self.data, x="FocalSpotCenterE", y="FocalSpotCenterU", kind="hex"
        )
        g.ax_joint.set_xlabel("Aim point in E / m", fontweight="bold")
        g.ax_joint.set_ylabel("Aim point in U / m", fontweight="bold")

        g.ax_joint.set_xlim(self.HEXBIN_XLIMS)
        g.ax_joint.set_ylim(self.HEXBIN_YLIMS)
        g.ax_joint.invert_xaxis()

        self._draw_target_markers(g.ax_joint)

        g.ax_joint.set_axisbelow(False)
        g.ax_joint.collections[0].set_zorder(1)

        file_name = "03_aim_point_distribution"
        self._save_plot(g.fig, file_name)

    def _draw_target_markers(self, ax: plt.Axes) -> None:
        """Draw L and T shaped markers for targets and the receiver based on paint mappings."""
        stj_upper = mappings.STJ_UPPER_ENU
        stj_lower = mappings.STJ_LOWER_ENU
        mft = mappings.MFT_ENU

        # Draw L and T markers
        self._draw_l_marker(
            ax, stj_upper[0][0], stj_upper[0][2], "UL", self.L_MARKER_SIZE_STJ
        )
        self._draw_l_marker(
            ax, stj_upper[2][0], stj_upper[2][2], "UR", self.L_MARKER_SIZE_STJ
        )
        self._draw_t_marker(
            ax, stj_upper[1][0], stj_upper[1][2], "right", self.L_MARKER_SIZE_STJ
        )
        self._draw_t_marker(
            ax, stj_upper[3][0], stj_upper[3][2], "left", self.L_MARKER_SIZE_STJ
        )
        self._draw_l_marker(
            ax, stj_lower[1][0], stj_lower[1][2], "LL", self.L_MARKER_SIZE_STJ
        )
        self._draw_l_marker(
            ax, stj_lower[3][0], stj_lower[3][2], "LR", self.L_MARKER_SIZE_STJ
        )

        self._draw_l_marker(ax, mft[0][0], mft[0][2], "UL", self.L_MARKER_SIZE_MFT)
        self._draw_l_marker(ax, mft[2][0], mft[2][2], "UR", self.L_MARKER_SIZE_MFT)
        self._draw_l_marker(ax, mft[1][0], mft[1][2], "LL", self.L_MARKER_SIZE_MFT)
        self._draw_l_marker(ax, mft[3][0], mft[3][2], "LR", self.L_MARKER_SIZE_MFT)

        # Draw receiver rectangle
        self._draw_rectangle(ax, self.receiver_coordinates)

        # Add text labels
        offset = self.LABEL_OFFSET
        ax.text(
            0,
            stj_upper[0][2] + offset,
            "STJ upper",
            fontsize=10,
            ha="center",
            va="center",
        )
        ax.text(
            0,
            stj_lower[1][2] - offset,
            "STJ lower",
            fontsize=10,
            ha="center",
            va="center",
        )
        ax.text(
            0,
            self.receiver_coordinates[1][2] + offset,
            "Receiver",
            fontsize=10,
            ha="center",
            va="center",
        )
        x_mft = 0.5 * (mft[0][0] + mft[2][0])
        ax.text(x_mft, mft[0][2] + offset, "MFT", fontsize=10, ha="center", va="center")

    @staticmethod
    def _draw_l_marker(
        ax: plt.Axes,
        x: float,
        z: float,
        orientation: str,
        size: float = 0.4,
        lw: float = 2,
    ) -> None:
        """Draw an L-shaped marker at a given (x, z) position with orientation."""
        if orientation == "UL":
            ax.plot([x, x], [z, z - size], color="k", linewidth=lw, zorder=5)
            ax.plot([x, x - size], [z, z], color="k", linewidth=lw, zorder=5)
        elif orientation == "UR":
            ax.plot([x, x], [z, z - size], color="k", linewidth=lw, zorder=5)
            ax.plot([x, x + size], [z, z], color="k", linewidth=lw, zorder=5)
        elif orientation == "LL":
            ax.plot([x, x], [z, z + size], color="k", linewidth=lw, zorder=5)
            ax.plot([x, x - size], [z, z], color="k", linewidth=lw, zorder=5)
        elif orientation == "LR":
            ax.plot([x, x], [z, z + size], color="k", linewidth=lw, zorder=5)
            ax.plot([x, x + size], [z, z], color="k", linewidth=lw, zorder=5)

    @staticmethod
    def _draw_t_marker(
        ax: plt.Axes,
        x: float,
        z: float,
        orientation: str,
        size: float = 0.3,
        lw: float = 2,
    ) -> None:
        """Draw a T-shaped marker at a given (x, z) position with orientation."""
        if orientation == "left":
            ax.plot([x, x + size], [z, z], color="k", linewidth=lw, zorder=5)
            ax.plot(
                [x, x],
                [z - 0.5 * size, z + 0.5 * size],
                color="k",
                linewidth=lw,
                zorder=5,
            )
        elif orientation == "right":
            ax.plot([x, x - size], [z, z], color="k", linewidth=lw, zorder=5)
            ax.plot(
                [x, x],
                [z - 0.5 * size, z + 0.5 * size],
                color="k",
                linewidth=lw,
                zorder=5,
            )

    def _draw_rectangle(
        self,
        ax: plt.Axes,
        corners: List[torch.Tensor],
        color: str = "k",
        linewidth: float = 1.5,
    ) -> None:
        """Draw a closed rectangle given its corners."""
        x = [corner[0] for corner in corners]
        z = [corner[2] for corner in corners]
        ax.plot(x, z, color=color, linewidth=linewidth)

    def _save_plot(self, fig: plt.Figure, base_name: str) -> None:
        """Save the plot to PNG format."""
        fig.tight_layout()
        fig.savefig(self.output_path / f"{base_name}.pdf", dpi=300, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path_to_data_directory",
        type=str,
        default="/Users/kphipps/Work/Gits/PAINT/download_for_plots",
    )
    parser.add_argument(
        "--path_to_metadata",
        type=str,
        default="/Users/kphipps/Work/Gits/PAINT/metadata/calibration_metadata_all_heliostats.csv",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="plots/saved_plots_new",
    )
    args = parser.parse_args()
    config = vars(args)

    plotter = ConditionDistributionPlot(**config)
    plotter.plot_sun_positions()
    plotter.plot_target_offsets()
