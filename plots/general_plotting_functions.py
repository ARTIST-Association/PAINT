from typing import Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import paint.util.paint_mappings as mappings


def plot_stacked_bar_chart_with_inset(
    grouped_df: pd.DataFrame,
    example_heliostat_df: pd.DataFrame,
    train_split_name: str,
    number_of_heliostats: int = 610,
    ax: Optional[Axes] = None,
    show_legend: bool = False,
    show_y_label: bool = False,
) -> None:
    """
    Compute the total measurements for each HeliostatID and plot a stacked bar chart with an inset scatter plot.

    Parameters
    ----------
    grouped_df: pd.DataFrame
        The measurement preprocessing from heliostats grouped by the heliostat ID.
    example_heliostat_df : pd.DataFrame
        The example measurements of a single heliostat.
    train_split_name : str
        The name of the training split
    number_of_heliostats : int
        The number of heliostats considered in the plot (default: 610).
    ax: Axes, optional
        Axes object to build the plot on. If None, a new figure will be created.
    show_legend : bool
        Indicates whether to show the legend (default: False)
    show_y_label : bool
        Indicates whether to show the y-axis label (default: False)
    """
    # Compute the total measurements for each HeliostatID
    grouped_df[mappings.TOTAL_INDEX] = grouped_df.sum(axis=1)

    # Sort by total measurements for clearer plotting
    grouped_df = grouped_df.sort_values(mappings.TOTAL_INDEX)

    bar_width = 2  # Bar width

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))  # Create figure and axis objects

    # Plot each layer of the stacked bar chart
    ax.bar(
        grouped_df[mappings.TOTAL_INDEX],
        grouped_df[mappings.TRAIN_INDEX],
        width=bar_width,
        label="Train",
        color="skyblue",
    )
    ax.bar(
        grouped_df[mappings.TOTAL_INDEX],
        grouped_df[mappings.TEST_INDEX],
        width=bar_width,
        label="Test",
        color="salmon",
        bottom=grouped_df[mappings.TRAIN_INDEX],
    )
    ax.bar(
        grouped_df[mappings.TOTAL_INDEX],
        grouped_df[mappings.VALIDATION_INDEX],
        width=bar_width,
        label="Validation",
        color="lightgreen",
        bottom=grouped_df[mappings.TRAIN_INDEX] + grouped_df[mappings.TEST_INDEX],
    )

    # Customize the plot
    ax.set_xlabel("# Measurements per Heliostat")
    ax.set_ylabel("# Measurements per Heliostat")

    ax.set_xlim(
        0, number_of_heliostats
    )  # Ensure x-axis starts at 0 and ends at the number of heliostats
    ax.set_ylim(
        0, number_of_heliostats
    )  # Ensure y-axis starts at 0 and ends at the number of heliostats

    if show_legend:
        ax.legend(bbox_to_anchor=(0.3, 1.05), loc="center left", ncol=3)

    if show_y_label:
        ax.set_ylabel("# Measurements per Heliostat")
    else:
        ax.set_ylabel(None)  # Remove y-label
    # Create an inset for the scatter plot
    ax_inset = inset_axes(
        ax,
        width="95%",
        height="95%",
        bbox_to_anchor=(0.05, 0.45, 0.4, 0.5),
        loc="upper left",
        bbox_transform=ax.transAxes,
    )

    colors = {
        mappings.TRAIN_INDEX: "blue",
        mappings.TEST_INDEX: "red",
        mappings.VALIDATION_INDEX: "green",
    }
    for label, color in colors.items():
        subset = example_heliostat_df[example_heliostat_df[train_split_name] == label]
        ax_inset.scatter(
            subset["Azimuth"], subset["Elevation"], label=label, color=color, alpha=0.5
        )
    ax_inset.set_xlabel("Azimuth")
    ax_inset.set_ylabel("Elevation")
    ax_inset.set_title("Example Heliostat")


def mark_insufficient_data_as_nan(
    df: pd.DataFrame,
    column: str,
    minimum_train_entries: int,
    minimum_test_entries: int,
) -> pd.DataFrame:
    """
    Mark preprocessing splits with insufficient preprocessing as `NaN`.

    This function updates the dataset split to set 'NaN' for heliostats where the 'train' set is smaller than the
    minimum number of required training samples, and the 'test' set is smaller than the minimum number of test samples.

    Parameters
    ----------
    df : pd.DataFrame
        The considered preprocessing that contains the dataset split column.
    column : str
        The column name used to check for 'train' and 'test' entries.
    minimum_train_entries : int
        The minimum number of training entries required for each heliostat ID.
    minimum_test_entries : int
        The minimum number of 'test' entries required for each heliostat ID.

    Returns
    -------
    pd.DataFrame
        Updated preprocessing with adjusted dataset split set to `NaN`.
    """
    # Group by HeliostatId and count the number of 'train' and 'test' entries
    counts = (
        df.groupby(mappings.HELIOSTAT_ID)[column].value_counts().unstack(fill_value=0)
    )

    # Identify HeliostatIds with 'train' set smaller than n_train
    insufficient_train_heliostats = counts[
        counts.get(mappings.TRAIN_INDEX, 0) < minimum_train_entries
    ].index

    # Identify HeliostatIds with 'test' set smaller than m_validation
    insufficient_test_heliostats = counts[
        counts.get(mappings.TEST_INDEX, 0) < minimum_test_entries
    ].index

    # Combine both sets of insufficient HeliostatIds
    insufficient_heliostats = set(insufficient_train_heliostats).union(
        insufficient_test_heliostats
    )

    # Update the dataset split for those HeliostatIds
    df.loc[df[mappings.HELIOSTAT_ID].isin(insufficient_heliostats), column] = np.nan

    return df
