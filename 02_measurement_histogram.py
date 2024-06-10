#"id","FieldId","HeliostatId","CameraId","CalibrationTargetId","System","Version","Axis1MotorPosition","Axis2MotorPosition","ImageOffsetX","ImageOffsetY","TargetOffsetE","TargetOffsetN","TargetOffsetU","TrackingOffsetE","TrackingOffsetU","SunPosE","SunPosN","SunPosU","LastScore","GeometryData","IsDeleted","CreatedAt","UpdatedAt"

#TODO Gesamtheit der Verläufe SunPOsition Motorposition einfügen

import pandas as pd
import torch as th
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np
from Dataset_Paper.utils import num_to_name, calculate_az_el


# load Measurement CSV
meausrement_path = 'data/DatenHeliOS/calib_data.csv'
df_measurements = pd.read_csv(meausrement_path)
df_measurements = df_measurements.set_index('id') #setzt df id zu Bild index
# Convert 'CreatedAt' to datetime
df_measurements['CreatedAt'] = pd.to_datetime(df_measurements['CreatedAt'])

# Extract month and hour
df_measurements['Month'] = df_measurements['CreatedAt'].dt.month
df_measurements['Hour'] = df_measurements['CreatedAt'].dt.hour

columns_of_interest = ["Axis1MotorPosition","Axis2MotorPosition","ImageOffsetX","ImageOffsetY","TargetOffsetE",
                       "TargetOffsetN","TargetOffsetU","SunPosE","SunPosN","SunPosU", "Month", "Hour"]
plt.figure(figsize=(16, 10))
for i, column in enumerate(columns_of_interest, 1):
    bins = 20  # Default value
    if column == "Month":
        bins = 12
    elif column == "Hour":
        bins = 14
    print(column, bins)
    plt.subplot(4, 4, i)
    plt.hist(df_measurements[column], bins=bins, color='skyblue', edgecolor='black')
    plt.title(column)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    if column == "Month":
        plt.xticks(np.arange(1, 13))  # Set x-axis ticks from 1 to 12 for Month histogram


plt.tight_layout()
plt.show()
plt.savefig("02_Measurement_Histogram.png", dpi=300)