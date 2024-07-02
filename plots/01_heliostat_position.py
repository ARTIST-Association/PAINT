import pandas as pd
import matplotlib.pyplot as plt
from paint.util.utils import num_to_name
from matplotlib.patches import Rectangle

# Load heliostat position file
path_heliostat_positions = "data/DatenHeliOS/Heliostatpositionen_xyz.xlsx"
df_heliostat_positions = pd.read_excel(path_heliostat_positions, header=0)
df_heliostat_positions.set_index(
    "InternalName", inplace=True
)  # Set "InternalName" as the index
df_heliostat_positions.rename_axis("HeliostatID", inplace=True)  # Rename the index
heliostat_positions = df_heliostat_positions[["x", "y", "z"]]

# Load Measurement CSV
measurement_path = "data/DatenHeliOS/calib_data.csv"
df_measurements = pd.read_csv(measurement_path)
df_measurements = df_measurements.set_index("id")  # Set df id as index
# Get all existing heliostat IDs and their entry counts
heliostat_counts = df_measurements["HeliostatId"].value_counts()
# Replace HeliostatId with heliostat names in heliostat_counts dataframe
heliostat_counts.index = heliostat_counts.index.map(num_to_name)

# Merge positions and counts
merged_df = pd.merge(
    heliostat_positions, heliostat_counts, left_index=True, right_index=True
)

# Load deflectometry availability from file
deflectometry_file_path = "data/DatenHeliOS/deflec_availability.xlsx"
df_deflectometry = pd.read_excel(deflectometry_file_path)

# Set "InternalName" as the index
df_deflectometry.set_index("InternalName", inplace=True)

# Create a list of Internal names where "DeflectometryAvailable" is True
highlighted_heliostats = df_deflectometry.index[
    df_deflectometry["DeflectometryAvailable"] == True
].tolist()

# Add a column to identify highlighted heliostats
merged_df["highlight"] = merged_df.index.isin(highlighted_heliostats)


# Map MeasuredSurface values to colors
def get_color(surface):
    if surface > 95:
        return "green"
    elif surface >= 90:
        return "indigo"
    elif surface < 90:
        return "sienna"


# Add a column for color based on MeasuredSurface
merged_df["color"] = df_deflectometry["MeasuredSurface"].map(get_color)

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(
    merged_df["x"], merged_df["y"], c=merged_df["count"], cmap="coolwarm", alpha=0.7
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
rect = Rectangle((-5, -8), 10, 8, linewidth=2, edgecolor="darkgrey", facecolor="grey")
plt.gca().add_patch(rect)

# Add square at (-17.5, 0)
rect = Rectangle((-22.5, -8), 10, 8, linewidth=2, edgecolor="black", facecolor="grey")
plt.gca().add_patch(rect)

y_min = -8  # Define your desired minimum y-value
y_max = 250
plt.ylim(y_min, y_max)
plt.tight_layout()
plt.legend(title="Accuracy of available\ndeflectometry data:")
plt.show()
plt.savefig("01_heliostat_positions.png", dpi=300)
plt.savefig("01_heliostat_positions.pdf", dpi=300)
