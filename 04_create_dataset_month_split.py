import pandas as pd
import numpy as np
from utils import calculate_az_el, plot_stacked_bar_chart, plot_scatter_az_el

# Function to classify time of day
def classify_month(month):
    if 5 <= month <= 6 or 7 <= month <= 8:
        return 'train'
    elif 3 <= month <= 4 or 9 <= month <= 10:
        return 'test'
    elif 1 <= month <= 2 or 11 <= month <= 12:
        return 'validation'
    else:
        raise ValueError('Invalid month')

# Function to check for empty sets
def check_for_empty_sets(grouped):
    empty_sets = {}
    for label in ['train', 'test', 'validation']:
        empty_heliostats = grouped[grouped[label] == 0].index.tolist()
        empty_sets[label] = empty_heliostats
        print(f"HeliostatIDs with empty {label} sets:", len(empty_heliostats))
    print("---------------------")
    return empty_sets

# Function to set DataSet_month to NaN for specific HeliostatIDs
def set_azimuth_to_nan(df, heliostats):
    df.loc[df['HeliostatId'].isin(heliostats), 'DataSet_month'] = np.nan

# Updated function to select earliest N entries for each HeliostatId in the 'train' set
def select_earliest_n_train_entries(df, n):
    # Filter only 'train' entries
    filtered_df_train = df[df['DataSet_month'] == 'train']
    
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


# Load CSV
pathDF = 'data/DatenHeliOS/calib_data.csv'
df = pd.read_csv(pathDF).set_index('id')  # Set df id as index

# Convert 'CreatedAt' column to datetime
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

# Apply the function to create the new column
df['DataSet_month'] = df['CreatedAt'].dt.month.apply(classify_month)

# Calculate Azimuth and Elevation
df['Azimuth'], df['Elevation'] = calculate_az_el(df)

# Group by 'HeliostatId' and 'DataSet_month' and count the occurrences
grouped = df.dropna(subset=['DataSet_month']).groupby(['HeliostatId', 'DataSet_month']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="unfiltered")

# Check for empty sets
empty_sets = check_for_empty_sets(grouped)
# Combine all HeliostatIDs that need DataSet_month set to NaN
heliostats_to_nan = set().union(*empty_sets.values())
df.loc[df['HeliostatId'].isin(heliostats_to_nan), 'DataSet_month'] = np.nan  # Remove empty sets

# Update grouped dataframe after removing empty sets
grouped = df.dropna(subset=['DataSet_month']).groupby(['HeliostatId', 'DataSet_month']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="no_empty_sets")

# Create separate columns for different N
df['DataSet_month_10'] = df['DataSet_month']
df['DataSet_month_50'] = df['DataSet_month']
df['DataSet_month_100'] = df['DataSet_month']

# Select indices of earliest N entries
earliest_10_indices = select_earliest_n_train_entries(df, 10)
earliest_50_indices = select_earliest_n_train_entries(df, 50)
earliest_100_indices = select_earliest_n_train_entries(df, 100)

# Set 'DataSet_month' to NaN for 'train' entries not in the earliest N indices
df.loc[(df['DataSet_month_10'] == 'train') & (~df.index.isin(earliest_10_indices)), 'DataSet_month_10'] = np.nan
df.loc[(df['DataSet_month_50'] == 'train') & (~df.index.isin(earliest_50_indices)), 'DataSet_month_50'] = np.nan
df.loc[(df['DataSet_month_100'] == 'train') & (~df.index.isin(earliest_100_indices)), 'DataSet_month_100'] = np.nan

# Plot updated grouped data, ensuring 'train' set data is present
grouped = df.dropna(subset=['DataSet_month_10']).groupby(['HeliostatId', 'DataSet_month_10']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="10")

grouped = df.dropna(subset=['DataSet_month_50']).groupby(['HeliostatId', 'DataSet_month_50']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="50")

grouped = df.dropna(subset=['DataSet_month_100']).groupby(['HeliostatId', 'DataSet_month_100']).size().unstack(fill_value=0)
plot_stacked_bar_chart(grouped, train_split_name="100")

# Filter for a specific HeliostatID (change 'example_heliostat_id' to your specific ID)
filtered_df = df.dropna(subset=['DataSet_month_50'])
example_heliostat_id = filtered_df['HeliostatId'].iloc[1]  # Get a specific HeliostatId
single_heliostat_df = filtered_df[filtered_df['HeliostatId'] == example_heliostat_id]

# Call the plot function
plot_scatter_az_el(single_heliostat_df, "DataSet_month_50", "04_month_split_example_heliostat.png")

# Save the final dataframe
df.to_csv('04_month_split.csv', header=True)
print(df.head(100))
