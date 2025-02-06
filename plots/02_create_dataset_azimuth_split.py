import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from paint.data.dataset_splits import DatasetSplitter
import matplotlib.patches as mpatches


def main(
    calibration_data_file,
    split_types,
    training_sizes,
    validation_sizes,
    create_new_datasets,
    output_dir,
    plot_output,
    example_heliostat_id,
):
    # (Optional) Create new datasets if needed
    if create_new_datasets:
        splitter = DatasetSplitter(
            input_file=calibration_data_file, output_dir=output_dir, remove_unused_data=False
        )
        for training_size in training_sizes:
            for split_type in split_types:
                for validation_size in validation_sizes:
                    splitter.get_dataset_splits(
                        split_type=split_type,
                        training_size=training_size,
                        validation_size=validation_size,
                    )

    # Build a list of dataset file paths based on provided parameters.
    file_paths = []
    for training_size in training_sizes:
        for validation_size in validation_sizes:
            for split_type in split_types:
                file_name = (
                    f"{output_dir}/benchmark_split-{split_type}_train-{training_size}_"
                    f"validation-{validation_size}.csv"
                )
                file_paths.append(file_name)

    # Shared color mapping for splits (used in both the main plot and the inset)
    colors = {"train": "blue", "test": "red", "validation": "green"}

    # Initialize subplots for each dataset file.
    num_files = len(file_paths)
    fig, axes = plt.subplots(1, num_files, figsize=(18, 6), sharey=True)
    if num_files == 1:
        axes = [axes]

    for i, file_path in enumerate(file_paths):
        # Load split information for the current file.
        split_data = pd.read_csv(file_path, usecols=["Id", "Split"])

        # Load the full calibration data and merge the split info by matching on 'Id'.
        calibration_data = pd.read_csv(calibration_data_file)
        calibration_data["Split"] = calibration_data["Id"].map(
            split_data.set_index("Id")["Split"]
        )

        # Group by HeliostatId and Split to count occurrences.
        split_counts = (
            calibration_data.groupby(["HeliostatId", "Split"])
            .size()
            .unstack(fill_value=0)
        )
        split_counts["Total"] = split_counts.sum(axis=1)
        split_counts = split_counts.sort_values(by="Total", ascending=False).drop(
            columns=["Total"]
        )

        # Reorder the columns so that 'train' is first, then 'test', then 'validation'.
        split_counts = split_counts.reindex(columns=["train", "test", "validation"], fill_value=0)

        # Replace the HeliostatId with sequential numbers starting at 0.
        num_heliostats = len(split_counts)
        split_counts.index = range(0, num_heliostats)

        # Determine the bar colors based on the shared mapping (defaulting to 'gray' if unknown).
        bar_colors = [colors.get(split, "gray") for split in split_counts.columns]

        # Plot the counts as a stacked bar plot (with no legend).
        split_counts.plot(kind="bar", stacked=True, ax=axes[i], legend=False, color=bar_colors)

        # Set the x-axis label to "ID" and the y-axis label on the first subplot.
        axes[i].set_xlabel("ID", fontsize=12)
        if i == 0:
            axes[i].set_ylabel("Count", fontsize=12)

        # Rotate x tick labels and show only every 200th tick.
        axes[i].tick_params(axis="x", rotation=45)
        ticks = list(range(0, num_heliostats, 200))
        axes[i].set_xticks(ticks)

        # Extract a training-size indicator from the file name (e.g. 'train-10').
        try:
            train_indicator = file_path.split("_")[2]
        except IndexError:
            train_indicator = file_path
        axes[i].set_title(f"Distribution for {train_indicator}", fontsize=14)

        # ---- Add an inset in the current subplot for the example heliostat ----
        example_heliostat_df = calibration_data[
            calibration_data["HeliostatId"] == example_heliostat_id
        ]

        inset_ax = inset_axes(
            axes[i],
            width="50%",
            height="50%",
            loc="upper right",
            bbox_to_anchor=(0, -0.05, 1, 1),
            bbox_transform=axes[i].transAxes,
        )

        for split, color in colors.items():
            subset = example_heliostat_df[example_heliostat_df["Split"] == split]
            if not subset.empty:
                inset_ax.scatter(subset["Azimuth"], subset["Elevation"], color=color, alpha=0.5)

        inset_ax.set_title(f"Heliostat {example_heliostat_id}", fontsize=10, pad=-5)
        inset_ax.set_xlabel("Azimuth", fontsize=8)
        inset_ax.set_ylabel("Elevation", fontsize=8)
        inset_ax.tick_params(axis="both", labelsize=8)

    # Create a single legend for the splits and add it to the upper left corner of the first subplot.
    legend_handles = [
        mpatches.Patch(color=colors[split], label=split.capitalize()) for split in colors
    ]
    axes[0].legend(handles=legend_handles, loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(plot_output, dpi=300)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot dataset split distributions with insets for an example heliostat."
    )
    parser.add_argument(
        "--calibration_data_file",
        type=str,
        default="PATH/TO/calibration_metadata_all_heliostats.csv",
        help="Path to the calibration metadata CSV file.",
    )
    parser.add_argument(
        "--split_types",
        nargs="+",
        default=["azimuth"],
        help="List of split types to use (e.g., azimuth).",
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
        help="Flag to create new datasets if needed.",
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
        default="plots/saved_plots/02_dataset_split_azimuth.pdf",
        help="File path to save the output plot.",
    )
    parser.add_argument(
        "--example_heliostat_id",
        type=str,
        default="AA23",
        help="Heliostat ID to show in every inset.",
    )
    args = parser.parse_args()

    main(
        calibration_data_file=args.calibration_data_file,
        split_types=args.split_types,
        training_sizes=args.training_sizes,
        validation_sizes=args.validation_sizes,
        create_new_datasets=args.create_new_datasets,
        output_dir=args.output_dir,
        plot_output=args.plot_output,
        example_heliostat_id=args.example_heliostat_id,
    )
