import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import calculate_az_el, plot_stacked_bar_chart, plot_scatter_az_el

# Function to classify time of day
def classify_time_of_day(hour):
    if 0 <= hour < 12:
        return 'train'
    elif 12 <= hour < 15:
        return 'test'
    elif 15 <= hour <= 23:
        return 'validation'
    else:
        raise ValueError('Invalid hour')

# Function to check for empty sets
def check_for_empty_sets(grouped):
    empty_sets = {}
    for label in ['train', 'test', 'validation']:
        empty_heliostats = grouped[grouped[label] == 0].index.tolist()
        empty_sets[label] = empty_heliostats
        print(f"HeliostatIDs with empty {label} sets:", len(empty_heliostats))
    print("---------------------")
    return empty_sets

# Function to set DataSet_hour to NaN for specific HeliostatIDs
def set_hour_to_nan(df, heliostats):
    df.loc[df['HeliostatId'].isin(heliostats), 'DataSet_hour'] = np.nan

# Updated function to select earliest N entries for each HeliostatId in the 'train' set
def select_earliest_n_train_entries(df, n):
    # Filter only 'train' entries
    filtered_df_train = df[df['DataSet_hour'] == 'train']
    
    # Group by 'HeliostatId' and filter groups with at least n entries
    valid_heliostats = filtered_df_train.groupby('HeliostatId').filter(lambda x: len(x) >= n)['HeliostatId'].unique()
    
    # Select earliest n entries for valid heliostats
    earliest_n_per_heliostat = (
        filtered_df_train[filtered_df_train['HeliostatId'].isin(valid_heliostats)]
        .sort_values(by=['HeliostatId', 'CreatedAt'])
        .groupby('HeliostatId')
        .head(n)
    )

    return earliest_n_per_heliostat.index

def plot_stacked_bar_chart(grouped_df, train_split_name):
    # Filter out heliostats without 'train' data
    grouped_df = grouped_df[grouped_df['train'] > 0]

    bar_positions = np.arange(len(grouped_df))  # Bar positions
    bar_width = 1  # Bar width

    fig, ax = plt.subplots(figsize=(10, 6))  # Create figure and axis objects

    # Plot each layer of the stacked bar chart
    ax.bar(bar_positions, grouped_df['train'], width=bar_width, label='Train', color='skyblue')
    ax.bar(bar_positions, grouped_df['test'], width=bar_width, label='Test', color='salmon', bottom=grouped_df['train'])
    ax.bar(bar_positions, grouped_df['validation'], width=bar_width, label='Validation', color='lightgreen', bottom=grouped_df['train'] + grouped_df['test'])

    # Customize the plot
    ax.set_xlabel('HeliostatIDs')
    ax.set_ylabel('Count')
    ax.set_title('Stacked Bar Plot of Train, Test, and Validation Counts')
    ax.legend()

    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.show()  # Show the plot

    plt.savefig(f"03_hour_split_{train_split_name}.png", dpi=300)

# Load CSV
pathDF = 'data/DatenHeliOS/calib_data.csv'
df = pd.read_csv(pathDF).set_index('id')  # Set df id as index

# Convert 'CreatedAt' column to datetime
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

# Apply the function to create the new column
df['DataSet_hour'] = df['CreatedAt'].dt.hour.apply(classify_time_of_day)

# Calculate Azimuth and Elevation
df['Azimuth'], df['Elevation'] = calculate_az_el(df)

# Group by 'HeliostatId' and 'DataSet_hour' and count the occurrences
grouped = df.dropna(subset=['DataSet_hour']).groupby(['HeliostatId', 'DataSet_hour']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="unfiltered")

# Check for empty sets
empty_sets = check_for_empty_sets(grouped)

# Combine all HeliostatIDs that need DataSet_hour set to NaN
heliostats_to_nan = set().union(*empty_sets.values())
df.loc[df['HeliostatId'].isin(heliostats_to_nan), 'DataSet_hour'] = np.nan  # Remove empty sets

# Update grouped dataframe after removing empty sets
grouped = df.dropna(subset=['DataSet_hour']).groupby(['HeliostatId', 'DataSet_hour']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="no_empty_sets")

# Create separate columns for different N
df['DataSet_hour_10'] = df['DataSet_hour']
df['DataSet_hour_50'] = df['DataSet_hour']
df['DataSet_hour_100'] = df['DataSet_hour']

# Select indices of earliest N entries
earliest_10_indices = select_earliest_n_train_entries(df, 10)
earliest_50_indices = select_earliest_n_train_entries(df, 50)
earliest_100_indices = select_earliest_n_train_entries(df, 100)

# Set 'DataSet_hour' to NaN for 'train' entries not in the earliest N indices
df.loc[(df['DataSet_hour_10'] == 'train') & (~df.index.isin(earliest_10_indices)), 'DataSet_hour_10'] = np.nan
df.loc[(df['DataSet_hour_50'] == 'train') & (~df.index.isin(earliest_50_indices)), 'DataSet_hour_50'] = np.nan
df.loc[(df['DataSet_hour_100'] == 'train') & (~df.index.isin(earliest_100_indices)), 'DataSet_hour_100'] = np.nan

# Plot updated grouped data, ensuring 'train' set data is present
grouped = df.dropna(subset=['DataSet_hour_10']).groupby(['HeliostatId', 'DataSet_hour_10']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="10")

grouped = df.dropna(subset=['DataSet_hour_50']).groupby(['HeliostatId', 'DataSet_hour_50']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="50")

grouped = df.dropna(subset=['DataSet_hour_100']).groupby(['HeliostatId', 'DataSet_hour_100']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="100")

# Filter for a specific HeliostatID (change 'example_heliostat_id' to your specific ID)
filtered_df = df.dropna(subset=['DataSet_hour_50'])
example_heliostat_id = filtered_df['HeliostatId'].iloc[1]  # Get a specific HeliostatId
single_heliostat_df = filtered_df[filtered_df['HeliostatId'] == example_heliostat_id]

# Call the plot function
plot_scatter_az_el(single_heliostat_df, "DataSet_hour", "03_hour_split_example_heliostat.png")

# Save the final dataframe
df.to_csv('03_hour_split.csv', header=True)
print(df.head(100))
