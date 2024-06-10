#"id","FieldId","HeliostatId","CameraId","CalibrationTargetId","System","Version","Axis1MotorPosition","Axis2MotorPosition","ImageOffsetX","ImageOffsetY","TargetOffsetE","TargetOffsetN","TargetOffsetU","TrackingOffsetE","TrackingOffsetU","SunPosE","SunPosN","SunPosU","LastScore","GeometryData","IsDeleted","CreatedAt","UpdatedAt"

#TODO  Histogramm Sonnenposition Targetposition, Zeit , Heliostatpostion X,Y und Farbkodierung mit Datenpunkte zweite Farbkodierung für "Nicht bewertbar", 
#TODO Azimuth Split, Monat Split, KNN SPlit, Temporärer Split

import pandas as pd
import torch as th
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
from Dataset_Paper.utils import num_to_name, calculate_az_el

# load heliostat position file
path_heliostat_positions = 'data/DatenHeliOS/Heliostatpositionen_xyz.xlsx'
df_heliostat_positions = pd.read_excel(path_heliostat_positions, header=0)
df_heliostat_positions.set_index('InternalName', inplace=True)  # Set "InternalName" as the index
df_heliostat_positions.rename_axis('HeliostatID', inplace=True)  # Rename the index
heliostat_positions = df_heliostat_positions[[ 'x', 'y', 'z']]

# load Measurement CSV
meausrement_path = 'data/DatenHeliOS/calib_data.csv'
df_measurements = pd.read_csv(meausrement_path)
df_measurements = df_measurements.set_index('id') #setzt df id zu Bild index
# Get all existing heliostat IDs and their entry counts
heliostat_counts = df_measurements['HeliostatId'].value_counts()
# Replace HeliostatId with heliostat names in heliostat_counts dataframe
heliostat_counts.index = heliostat_counts.index.map(num_to_name)

merged_df = pd.merge(heliostat_positions, heliostat_counts, left_index=True, right_index=True)
merged_df.rename(columns={'HeliostatId': 'counts'}, inplace=True)


print(merged_df)
plt.figure(figsize=(10, 6))
plt.scatter(merged_df['x'], merged_df['y'], c=merged_df['count'], cmap='coolwarm', alpha=0.7)
plt.colorbar(label='Counts')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('Scatter Plot with Counts')
plt.grid(True)
plt.show()
plt.savefig("01_heliostat_positions.png", dpi=300)
