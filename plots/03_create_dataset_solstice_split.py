import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.patches as mpatches
import paint.util.paint_mappings as mappings
# Define mapping constants for our splitting.


class SolsticeDatasetSplitter:
    @staticmethod
    def get_nearest_solstice_distance(timestamp: pd.Timestamp, season: str) -> float:
        """
        Calculate the distances to the nearest December 21 and June 21.

        Parameters
        ----------
        timestamp : pd.Timestamp
            The current timestamp considered.
        season : str
            Which solstice to consider: "summer" or "winter".

        Returns
        -------
        float
            The time distance to the nearest solstice in seconds.
        """
        day = 21  # Solstice day of month
        if season == "summer":
            month = 6  # Summer solstice month
        elif season == "winter":
            month = 12  # Winter solstice month
        else:
            raise ValueError(f"Season {season} must be either summer or winter.")
        year = timestamp.year
        current_solstice = pd.Timestamp(year=year, month=month, day=day, hour=12)
        next_solstice = pd.Timestamp(year=year + 1, month=month, day=day, hour=12)
        previous_solstice = pd.Timestamp(year=year - 1, month=month, day=day, hour=12)

        return min(
            abs((timestamp - current_solstice).total_seconds()),
            abs((timestamp - next_solstice).total_seconds()),
            abs((timestamp - previous_solstice).total_seconds()),
        )

    def split_data(self, df: pd.DataFrame, split_name: str, train_head: int, validation_head: int) -> pd.Series:
        """
        Split the data according to the solstice distance and return a column of split labels.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to split.
        split_name : str
            The name of the new column that will store split labels.
        train_head : int
            The number of entries (starting at the top after sorting by winter distance)
            to mark as training.
        validation_head : int
            The number of entries (starting at the top after sorting by summer distance)
            to mark as validation.

        Returns
        -------
        pd.Series
            A series with the split label for each row.
        """
        # Ensure that the created-at column is a datetime.
        df[mappings.CREATED_AT] = pd.to_datetime(df[mappings.CREATED_AT])

        # Calculate distances to the winter and summer solstices.
        df[mappings.DECEMBER_DISTANCE] = df[mappings.CREATED_AT].apply(
            lambda x: self.get_nearest_solstice_distance(timestamp=x, season=mappings.WINTER_SEASON)
        )
        df[mappings.JUNE_DISTANCE] = df[mappings.CREATED_AT].apply(
            lambda x: self.get_nearest_solstice_distance(timestamp=x, season=mappings.SUMMER_SEASON)
        )

        # Initialize all rows as 'test'.
        df[split_name] = mappings.TEST_INDEX

        # For training, sort by distance to winter solstice (and then by timestamp)
        df_sorted_winter = df.sort_values(by=[mappings.DECEMBER_DISTANCE, mappings.CREATED_AT])
        train_indices = df_sorted_winter.head(train_head).index

        # For validation, sort by distance to summer solstice (and then by timestamp)
        df_sorted_summer = df.sort_values(by=[mappings.JUNE_DISTANCE, mappings.CREATED_AT])
        validation_indices = df_sorted_summer.head(validation_head).index

        # Assign the split labels.
        df.loc[train_indices, split_name] = mappings.TRAIN_INDEX
        df.loc[validation_indices, split_name] = mappings.VALIDATION_INDEX


        return df[split_name]

def main(
    calibration_data_file,
    training_sizes,
    validation_sizes,
    create_new_datasets,
    output_dir,
    plot_output,
    example_heliostat_id,
):
    # Ensure the output directory exists.
    os.makedirs(output_dir, exist_ok=True)

    splitter = SolsticeDatasetSplitter()

    # (Optional) Create new solstice-based split datasets.
    if create_new_datasets:
        # Load the full calibration data.
        calibration_data = pd.read_csv(calibration_data_file)
        # For each combination of training and validation sizes,
        # create a split and save a CSV with just the Id and split label.
        for train_head in training_sizes:
            for validation_head in validation_sizes:
                split_series = splitter.split_data(
                    calibration_data.copy(),
                    split_name=mappings.SPLIT_KEY,

                    train_head=train_head,
                    validation_head=validation_head,
                )
                split_df = pd.DataFrame({
                    "Id": calibration_data["Id"],
                    "Split": split_series
                })
                file_name = f"{output_dir}/benchmark_split-solstice_train-{train_head}_validation-{validation_head}.csv"
                split_df.to_csv(file_name, index=False)
                print(f"Saved split dataset to {file_name}")

    # Build a list of file paths for plotting.
    file_paths = []
    for train_head in training_sizes:
        for validation_head in validation_sizes:
            file_name = f"{output_dir}/benchmark_split-solstice_train-{train_head}_validation-{validation_head}.csv"
            file_paths.append(file_name)

    # Define shared colors for each split.
    colors = mappings.TRAIN_TEST_VAL_COLORS


    # Create a subplot for each dataset.
    num_files = len(file_paths)
    fig, axes = plt.subplots(1, num_files, figsize=(18, 6), sharey=True)
    if num_files == 1:
        axes = [axes]

    for i, file_path in enumerate(file_paths):
        # Load the full calibration data and merge the split info by Id.
        calibration_data = pd.read_csv(calibration_data_file)
        # Load the split information.
        split_data = pd.read_csv(file_path, usecols=[mappings.ID_INDEX, mappings.SPLIT_KEY])
        calibration_data[mappings.SPLIT_KEY] = calibration_data[mappings.ID_INDEX].map(
            split_data.set_index(mappings.ID_INDEX)[mappings.SPLIT_KEY]
        )



        # Group by HeliostatId and Split to count the number of entries.
        split_counts = (
            calibration_data.groupby([mappings.HELIOSTAT_ID, mappings.SPLIT_KEY])
            .size()
            .unstack(fill_value=0)
        )
        split_counts["Total"] = split_counts.sum(axis=1)
        split_counts = split_counts.sort_values(by="Total", ascending=False).drop(columns=["Total"])

        # Reorder columns so that train, test, then validation are shown.
        split_counts = split_counts.reindex(columns=[mappings.TRAIN_INDEX, mappings.TEST_INDEX, mappings.VALIDATION_INDEX], fill_value=0)


        # Replace HeliostatId with sequential numbers.
        num_heliostats = len(split_counts)
        split_counts.index = range(num_heliostats)

        # Plot as a stacked bar plot.
        bar_colors = [colors.get(split, "gray") for split in split_counts.columns]
        split_counts.plot(kind="bar", stacked=True, ax=axes[i], legend=False, color=bar_colors)

        axes[i].set_xlabel("ID", fontsize=12)
        if i == 0:
            axes[i].set_ylabel("Count", fontsize=12)
        axes[i].tick_params(axis="x", rotation=45)
        ticks = list(range(0, num_heliostats, 200))
        axes[i].set_xticks(ticks)

        # Extract training and validation info from the file name.
        parts = file_path.split("_")
        try:
            train_indicator = next(part for part in parts if part.startswith("train"))
            val_indicator = next(part for part in parts if part.startswith("validation")).split(".")[0]
        except (IndexError, StopIteration):
            train_indicator = file_path
            val_indicator = ""
        axes[i].set_title(f"Solstice Split: {train_indicator}, {val_indicator}", fontsize=14)

        # --- Add an inset plot for the example heliostat ---
        example_heliostat_df = calibration_data[calibration_data[mappings.HELIOSTAT_ID] == example_heliostat_id]

        inset_ax = inset_axes(
            axes[i],
            width="50%",
            height="50%",
            loc="upper right",
            bbox_to_anchor=(0, -0.05, 1, 1),
            bbox_transform=axes[i].transAxes,
        )
        for split, color in colors.items():
            subset = example_heliostat_df[example_heliostat_df[mappings.SPLIT_KEY] == split]
            if not subset.empty:
                inset_ax.scatter(subset[mappings.AZIMUTH], subset[mappings.ELEVATION], color=color, alpha=0.5)
        inset_ax.set_title(f"Heliostat {example_heliostat_id}", fontsize=10, pad=-5)
        inset_ax.set_xlabel("Azimuth", fontsize=8)
        inset_ax.set_ylabel("Elevation", fontsize=8)
        inset_ax.tick_params(axis="both", labelsize=8)

    # Create a single legend on the first subplot.
    legend_handles = [mpatches.Patch(color=colors[split], label=split.capitalize()) for split in colors]
    axes[0].legend(handles=legend_handles, loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(plot_output, dpi=300)
    plt.close()
    print(f"Plot saved to {plot_output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot dataset split distributions with insets for an example heliostat "
                    "using solstice-based splitting."
    )
    parser.add_argument(
        "--calibration_data_file",
        type=str,
        default="PATH/TO/calibration_metadata_all_heliostats.csv",
        help="Path to the calibration metadata CSV file.",
    )
    parser.add_argument(
        "--training_sizes",
        type=int,
        nargs="+",
        default=[10, 50, 100],
        help="List of training head sizes to use.",
    )
    parser.add_argument(
        "--validation_sizes",
        type=int,
        nargs="+",
        default=[30],
        help="List of validation head sizes to use.",
    )
    parser.add_argument(
        "--create_new_datasets",
        action="store_true",
        help="Flag to create new solstice-based split datasets if needed.",
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
        default="plots/saved_plots/03_solstice_split.pdf",
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
        training_sizes=args.training_sizes,
        validation_sizes=args.validation_sizes,
        create_new_datasets=args.create_new_datasets,
        output_dir=args.output_dir,
        plot_output=args.plot_output,
        example_heliostat_id=args.example_heliostat_id,
    )
