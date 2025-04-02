import argparse
import json
from pathlib import Path
from typing import Any, Dict, Union

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import paint.util.paint_mappings as mappings
from paint.data.dataset_splits import DatasetSplitter
from paint.util import set_logger_config

# Logger for the dataset splitter
set_logger_config()


def main(
    calibration_metadata_file: str,
    split_types: list[str],
    training_sizes: list[int],
    validation_sizes: list[int],
    create_new_datasets: bool,
    output_dir: Union[str, Path],
    plot_output: Union[str, Path],
    example_heliostat_id: str,
) -> None:
    """
    Plot dataset split distributions using calibration metadata.

    Parameters
    ----------
    calibration_metadata_file : str
        Path to the calibration metadata CSV file containing the calibration information.
    split_types : list[str]
        List of split types to use (e.g. 'azimuth', 'solstice').
    training_sizes : list[int]
        List of training sizes to use.
    validation_sizes : list[int]
        List of validation sizes to use.
    create_new_datasets : bool
        Whether to (re)create the dataset splits.
    output_dir : str
        Directory to store the generated datasets.
    plot_output : str
        Directory to save the plot files (one file per split type).
    example_heliostat_id : str
        Heliostat ID to highlight in the inset plots.

    Raises
    ------
    FileNotFoundError
        If the calibration metadata file does not exist.
    ValueError
        If training/validation sizes are inconsistent with dataset constraints.
    """
    # Create a DatasetSplitter instance.
    # Use remove_unused_data=False to preserve extra columns (e.g. azimuth, elevation) needed for plotting.
    calibration_metadata_path = Path(calibration_metadata_file)
    if not calibration_metadata_path.exists():
        raise FileNotFoundError(
            f"Calibration metadata file '{calibration_metadata_file}' not found."
        )

    splitter = DatasetSplitter(
        input_file=calibration_metadata_file,
        output_dir=output_dir,
        remove_unused_data=False,
    )

    # Optionally create/recreate the dataset splits.
    if create_new_datasets:
        for training_size in training_sizes:
            for _ in validation_sizes:
                for split_type in split_types:
                    splitter.get_dataset_splits(
                        split_type=split_type,
                        training_size=training_size,
                        validation_size=validation_sizes[
                            0
                        ],  # each call must satisfy the minimum images per heliostat.
                    )

    # Read the full calibration metadata once.
    calibration_data = pd.read_csv(calibration_metadata_file)

    # Ensure that the plot_output directory exists.
    plot_output_path = Path(plot_output)
    plot_output_path.mkdir(parents=True, exist_ok=True)

    # For each split type, create a separate plot file.
    for split_type in split_types:
        # For the current split type, gather the split data for each combination of training and validation sizes.
        # We use a dictionary keyed by (training_size, validation_size)
        current_split_data = {}
        for training_size in training_sizes:
            for validation_size in validation_sizes:
                split_df = splitter.get_dataset_splits(
                    split_type=split_type,
                    training_size=training_size,
                    validation_size=validation_size,
                )
                current_split_data[(training_size, validation_size)] = split_df

        # Determine grid dimensions for subplots.
        # Here we use rows = number of validation sizes and columns = number of training sizes.
        ncols = len(training_sizes)
        nrows = len(validation_sizes)
        num_plots = ncols * nrows

        fig, axes = plt.subplots(
            nrows=nrows, ncols=ncols, figsize=(6 * ncols, 5 * nrows), sharey=True
        )

        # Flatten axes so that we can iterate uniformly.
        if num_plots == 1:
            axes = [axes]
        else:
            axes = np.array(axes).flatten()

        # For each combination, create a subplot.
        for ax, ((training_size, validation_size), split_df) in zip(
            axes, current_split_data.items()
        ):
            # Merge the split info into the full calibration data.
            split_df_reset = (
                split_df.reset_index()
            )  # bring the ID (index) back as a column
            merged_data = pd.merge(
                calibration_data,
                split_df_reset[[mappings.ID_INDEX, mappings.SPLIT_KEY]],
                on=mappings.ID_INDEX,
                how="left",
            )

            # Group by heliostat and split to count occurrences.
            split_counts = (
                merged_data.groupby([mappings.HELIOSTAT_ID, mappings.SPLIT_KEY])
                .size()
                .unstack(fill_value=0)
            )
            # Add total counts for sorting and then drop the helper column.
            split_counts[mappings.TOTAL_INDEX] = split_counts.sum(axis=1)
            split_counts = split_counts.sort_values(
                by=mappings.TOTAL_INDEX, ascending=False
            ).drop(columns=[mappings.TOTAL_INDEX])
            # Reorder columns: train, then test, then validation.
            split_counts = split_counts.reindex(
                columns=[
                    mappings.TRAIN_INDEX,
                    mappings.TEST_INDEX,
                    mappings.VALIDATION_INDEX,
                ],
                fill_value=0,
            )

            # Replace the heliostat IDs with sequential numbers (for plotting purposes).
            num_heliostats = len(split_counts)
            split_counts.index = range(num_heliostats)

            # Determine the bar colors using the shared mapping.
            colors = mappings.TRAIN_TEST_VAL_COLORS
            bar_colors = [colors.get(split, "gray") for split in split_counts.columns]

            # Plot the stacked bar plot.
            split_counts.plot(
                kind="bar", stacked=True, ax=ax, legend=False, color=bar_colors
            )
            # Change the x-axis label as requested.
            ax.set_xlabel("Heliostats sorted by # measurements", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.tick_params(axis="x", rotation=45)
            ticks = list(range(0, num_heliostats, 200))
            ax.set_xticks(ticks)

            # Set y-axis limits for KNN and KMEANS split types.
            if split_type in [mappings.KMEANS_SPLIT, mappings.KNN_SPLIT]:
                ax.set_ylim(0, 500)

            # Set subplot title indicating the training and validation sizes.
            ax.set_title(f"Train {training_size} / Val {validation_size}", fontsize=12)

            # ---- Add an inset for the example heliostat ----
            example_heliostat_df = merged_data[
                merged_data[mappings.HELIOSTAT_ID] == example_heliostat_id
            ]
            inset_ax = inset_axes(
                ax,
                width="50%",
                height="50%",
                loc="upper right",
                bbox_to_anchor=(0, -0.05, 1, 1),
                bbox_transform=ax.transAxes,
            )
            for split, color in colors.items():
                subset = example_heliostat_df[
                    example_heliostat_df[mappings.SPLIT_KEY] == split
                ]
                if not subset.empty:
                    inset_ax.scatter(
                        subset[mappings.AZIMUTH],
                        subset[mappings.ELEVATION],
                        color=color,
                        alpha=0.5,
                    )
            inset_ax.set_title(f"Heliostat {example_heliostat_id}", fontsize=8, pad=-5)
            inset_ax.set_xlabel("Azimuth", fontsize=8)
            inset_ax.set_ylabel("Elevation", fontsize=8)
            inset_ax.tick_params(axis="both", labelsize=8)

        # Create a common legend (placed in the upper left of the first subplot).
        legend_handles = [
            mpatches.Patch(color=colors[split], label=split.capitalize())
            for split in colors
        ]
        axes[0].legend(handles=legend_handles, loc="upper left", fontsize=10)

        plt.tight_layout()
        
        # Save the figure as "02_<split_type>_split.pdf"
        file_name = plot_output_path / f"02_{split_type}_split.pdf"
        plt.savefig(file_name, dpi=300)
        plt.close(fig)
        print(f"Saved plot for split type '{split_type}' to {file_name}")


def load_config(json_path: Path) -> Dict[str, Any]:
    """
    Load a Json config.

    Parameters
    ----------
    json_path : pathlib.Path
        Path to the JSON config file to load.

    Returns
    -------
    Dict[str, Any]
        A python object containing the loaded JSON config.
    """
    if json_path.exists():
        with json_path.open() as f:
            return json.load(f)
    return {}


if __name__ == "__main__":
    # Check if the config file exists and load it.
    config_file = Path("plots/plot_paths.json")
    config = load_config(config_file)

    # Set defaults using values from the JSON if available.
    default_calibration_file = config.get(
        "path_to_measurements", "PATH/TO/calibration_metadata_all_heliostats.csv"
    )
    default_plot_output = config.get("output_path", "PATH/TO/OUTPUT/PLOTS")

    parser = argparse.ArgumentParser(
        description="Plot dataset split distributions with insets for an example heliostat."
    )
    parser.add_argument(
        "--calibration_metadata_file",
        type=str,
        default=default_calibration_file,
        help="Path to the calibration metadata CSV file.",
    )
    parser.add_argument(
        "--split_types",
        type=str,
        nargs="+",
        default=[
            mappings.AZIMUTH_SPLIT,
            mappings.SOLSTICE_SPLIT,
            mappings.KMEANS_SPLIT,
            mappings.KNN_SPLIT,
        ],
        help="List of split types to use (e.g. azimuth, solstice).",
    )
    parser.add_argument(
        "--training_sizes",
        type=int,
        nargs="+",
        default=[10, 50, 100],
        help="List of training sizes to use.",
    )
    parser.add_argument(
        "--validation_sizes",
        type=int,
        nargs="+",
        default=[30],
        help="List of validation sizes to use.",
    )
    parser.add_argument(
        "--create_new_datasets",
        action="store_true",
        help="Flag to (re)create new datasets if needed.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data",
        help="Directory to store the generated datasets.",
    )
    parser.add_argument(
        "--plot_output",
        type=str,
        default=default_plot_output,
        help="Directory to save the plot files (one file per split type).",
    )
    parser.add_argument(
        "--example_heliostat_id",
        type=str,
        default="AA23",
        help="Heliostat ID to show in every inset.",
    )
    args = parser.parse_args()

    main(**vars(args))
