import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

def check_for_empty_sets(grouped):
    # Identify HeliostatIDs empty sets
    empty_train_heliostats = grouped[grouped['train'] == 0].index.tolist()
    empty_test_heliostats = grouped[grouped['test'] == 0].index.tolist()
    empty_validation_heliostats = grouped[grouped['validation'] == 0].index.tolist()
    empty_test_and_validation_heliostats = grouped[
        (grouped['test'] == 0) & (grouped['validation'] == 0)
    ].index.tolist()

    # Output the lists
    print("---------------------")
    print("HeliostatIDs with empty train sets:", len(empty_train_heliostats))
    print("HeliostatIDs with empty test sets:", len(empty_test_heliostats))
    print("HeliostatIDs with empty validation sets:", len(empty_validation_heliostats))
    print("HeliostatIDs with empty test and validation sets:", len(empty_test_and_validation_heliostats))
    print("---------------------")
    return empty_train_heliostats, empty_test_heliostats, empty_validation_heliostats, empty_test_and_validation_heliostats

# Load CSV
pathDF = 'data/DatenHeliOS/calib_data.csv'
df = pd.read_csv(pathDF)
df = df.set_index('id')  # Set df id as index

# Convert 'CreatedAt' column to datetime
df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])

# Apply the function to create the new column
df['DataSet_Azimuth'] = df['CreatedAt'].dt.hour.apply(classify_time_of_day)

# Group by 'HeliostatId' and 'DataSet_Azimuth' and count the occurrences
grouped = df.groupby(['HeliostatId', 'DataSet_Azimuth']).size().unstack(fill_value=0)

# Plot the stacked bar graph
ax = grouped.plot(kind='bar', stacked=True, figsize=(10, 6), 
                           color=['skyblue', 'lightgreen', 'salmon'])

# Customize the plot
plt.title('Count of Train, Test, and Validation Data for Each HeliostatID')
plt.xlabel('HeliostatID')
plt.ylabel('Count')
plt.legend(title='DataSet_Azimuth')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Show the plot
plt.show()
plt.savefig("03_Azimut_Split.png", dpi=300)
