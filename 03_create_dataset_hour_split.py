import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from utils import calculate_az_el


# Function to classify time of day
def classify_azimuth_split(df, split_name, head, tail):
    df = df.sort_values(
        by=["Azimuth", "CreatedAt"]
    )  # Ensure sorted by azimuth and timestamp
    train_indices = df.head(head).index
    validation_indices = df.tail(tail).index
    df[split_name] = "test"  # Default to 'test'
    df.loc[train_indices, split_name] = "train"
    df.loc[validation_indices, split_name] = "validation"
    return df[split_name]

def plot_stacked_bar_chart_with_inset(
    grouped_df, example_heliostat_df, train_split_name
):
    """
    Compute the total measurements for each HeliostatID and plot a stacked bar chart with inset scatter plot.

    Parameters:
    - grouped_df: DataFrame containing measurements grouped by HeliostatID
    - example_heliostat_df: DataFrame containing example heliostat data
    - train_split_name: Name of the training split

    Returns:
    None
    """
    # Compute the total measurements for each HeliostatID
    grouped_df["Total"] = grouped_df.sum(axis=1)

    # Sort by total measurements for clearer plotting
    grouped_df = grouped_df.sort_values("Total")

    bar_width = 2  # Bar width

    _ , ax = plt.subplots(figsize=(10, 6))  # Create figure and axis objects

    # Plot each layer of the stacked bar chart
    ax.bar(
        grouped_df["Total"],
        grouped_df["train"],
        width=bar_width,
        label="Train",
        color="skyblue",
    )
    ax.bar(
        grouped_df["Total"],
        grouped_df["test"],
        width=bar_width,
        label="Test",
        color="salmon",
        bottom=grouped_df["train"],
    )
    ax.bar(
        grouped_df["Total"],
        grouped_df["validation"],
        width=bar_width,
        label="Validation",
        color="lightgreen",
        bottom=grouped_df["train"] + grouped_df["test"],
    )

    # Customize the plot
    ax.set_xlabel("# Measurements per Heliostat")
    ax.set_ylabel("# Measurements per Heliostat")

    ax.set_xlim(
        0, 610
    )  # Ensure x-axis starts at 0 and ends at the number of heliostats
    ax.set_ylim(
        0, 610
    )  # Ensure y-axis starts at 0 and ends at the number of heliostats

    ax.legend(bbox_to_anchor=(0.5, 0.95), loc="center left", ncol=3)
    # Create an inset for the scatter plot
    ax_inset = inset_axes(
        ax,
        width="95%",
        height="95%",
        bbox_to_anchor=(0.05, 0.45, 0.4, 0.5),
        loc="upper left",
        bbox_transform=ax.transAxes,
    )

    colors = {"train": "blue", "test": "red", "validation": "green"}
    for label, color in colors.items():
        subset = example_heliostat_df[example_heliostat_df[train_split_name] == label]
        ax_inset.scatter(
            subset["Azimuth"], subset["Elevation"], label=label, color=color, alpha=0.5
        )
    ax_inset.set_xlabel("Azimuth")
    ax_inset.set_ylabel("Elevation")
    ax_inset.set_title("Example Heliostat")

    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.savefig(f"03_{train_split_name}.png", dpi=300)
    plt.savefig(f"03_{train_split_name}.pdf", dpi=300)


def update_datasets_to_nan_if_too_small(df, column, n_train, m_validation):
    """
    Update the dataset split to set 'NaN' for heliostats where 'train' set is smaller than n_train
    and 'test' set is smaller than m_validation.

    Parameters:
    df (pd.DataFrame): DataFrame with the dataset split column.
    column (str): Column name to check for 'train' and 'test' entries.
    n_train (int): Minimum number of 'train' entries required for each HeliostatId.
    m_validation (int): Minimum number of 'test' entries required for each HeliostatId.

    Returns:
    pd.DataFrame: Updated DataFrame with adjusted dataset split.
    """
    # Group by HeliostatId and count the number of 'train' and 'test' entries
    counts = df.groupby("HeliostatId")[column].value_counts().unstack(fill_value=0)

    # Identify HeliostatIds with 'train' set smaller than n_train
    insufficient_train_heliostats = counts[counts.get("train", 0) < n_train].index

    # Identify HeliostatIds with 'test' set smaller than m_validation
    insufficient_test_heliostats = counts[counts.get("test", 0) < m_validation].index

    # Combine both sets of insufficient HeliostatIds
    insufficient_heliostats = set(insufficient_train_heliostats).union(
        insufficient_test_heliostats
    )

    # Update the dataset split for those HeliostatIds
    df.loc[df["HeliostatId"].isin(insufficient_heliostats), column] = np.nan

    return df


# Load CSV and prepare columns
pathdf = "data/DatenHeliOS/calib_data.csv"
df = pd.read_csv(pathdf).set_index("id")  # Set df id as index
df["CreatedAt"] = pd.to_datetime(df["CreatedAt"])
df["Azimuth"], df["Elevation"] = calculate_az_el(
    df
)  # Calculate Azimuth and Elevation from Sun Vector

# Apply classification function
n_train = [10, 50, 100]  # number of train samples per HeliostatId
m_validation = 30  # number of validation samples per HeliostatId


for i,n in enumerate(n_train):
    print(n)
    df[f"DataSet_Azimuth_{n}"] = df.groupby("HeliostatId", group_keys=False).apply(
        lambda x: classify_azimuth_split(x, f"DataSet_Azimuth_{n}", n, m_validation)
    )
    df = update_datasets_to_nan_if_too_small(
        df, f"DataSet_Azimuth_{n}", n, m_validation
    )
    split_counts_by_heliostat = (
        df.dropna(subset=[f"DataSet_Azimuth_{n}"])
        .groupby(["HeliostatId", f"DataSet_Azimuth_{n}"])
        .size()
        .unstack(fill_value=0)
    )
    example_heliostat_df = df[
        df["HeliostatId"] == 11447
    ]  # chosen arbitrary heliostat but with good distribution
    plot_stacked_bar_chart_with_inset(
        split_counts_by_heliostat, example_heliostat_df, f"DataSet_Azimuth_{n}"
    )
