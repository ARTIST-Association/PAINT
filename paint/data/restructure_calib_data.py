import pandas as pd
from paint.util.utils import num_to_name
measurement_path = 'data/DatenHeliOS/calib_data.csv'
df_measurements = pd.read_csv(measurement_path)
df_measurements = df_measurements.set_index('id') # Set df id as index
# Get all existing heliostat IDs and their entry counts
heliostat_counts = df_measurements['HeliostatId'].value_counts()
# Replace HeliostatId with heliostat names in heliostat_counts dataframe
heliostat_counts.index = heliostat_counts.index.map(num_to_name)

#remove unneeded columns
#Field ID always 1, Camera ID always 0 , 
# System always "HeliOS", Version always 1, 
# LastScore and GeometryData are fitted, 
# UpdatedAt same time as CreatedAt
df_measurements = df_measurements.drop(columns=['FieldId', 'CameraId', "System","Version", "LastScore", "GeometryData", "UpdatedAt"])

#TODO: Add column for Calibration Image and and Target
