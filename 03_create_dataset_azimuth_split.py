#"id","FieldId","HeliostatId","CameraId","CalibrationTargetId","System","Version","Axis1MotorPosition","Axis2MotorPosition","ImageOffsetX","ImageOffsetY","TargetOffsetE","TargetOffsetN","TargetOffsetU","TrackingOffsetE","TrackingOffsetU","SunPosE","SunPosN","SunPosU","LastScore","GeometryData","IsDeleted","CreatedAt","UpdatedAt"


#TODO  Histogramm Sonnenposition Targetposition, Zeit , Heliostatpostion X,Y und Farbkodierung mit Datenpunkte zweite Farbkodierung für "Nicht bewertbar", 
#TODO Azimuth Split, Monat Split, KNN SPlit, Temporärer Split

import pandas as pd
import torch as th
#from torchvision import transforms
import numpy as np
#import tqdm
from PIL import Image
import os
import matplotlib.pyplot as plt

filter="morning_evening"
choose_specific_heliostat = True

def num_to_name(helID):
    """Returns the name of a heliostat based on its ID"""
    str_ = str(helID)
    name = chr(ord('A') + int(str_[0]) - 1)
    name += chr(ord('A') + int(str_[1:3]) - 1)
    name += str_[3:]
    return name


# CSV laden
pathDF = 'data/DatenHeliOS/calib_data.csv'
df = pd.read_csv(pathDF)
df = df.set_index('id') #setzt df id zu Bild index

if choose_specific_heliostat == True:
    # Find the HeliostatID with the most entries
    most_common_helID = df['HeliostatId'].value_counts().idxmax()
    print(most_common_helID)

    # Filter the DataFrame for the most common HeliostatID
    df = df[df['HeliostatId'] == most_common_helID]
    print(df)




if filter=="morning_evening":
    # Convert 'CreatedAt' column to datetime
    df['CreatedAt'] = pd.to_datetime(df['CreatedAt'])
    # Filter data taken between 00:01 am and 11:59 am
    df_filtered_train = df[(df['CreatedAt'].dt.hour >= 0) & (df['CreatedAt'].dt.hour < 12)]
    df_filtered_test = df[(df['CreatedAt'].dt.hour >= 12) & (df['CreatedAt'].dt.hour <= 23)]
else:
    print("No filter applied.")


# Function to calculate azimuth and elevation
def calculate_az_el(df):
    E = np.array(df['SunPosE'])
    N = -np.array(df['SunPosN'])
    U = np.array(df['SunPosU'])
    Az_deg = np.degrees(np.arctan2(E, N))
    El_deg = np.degrees(np.arctan2(U, np.sqrt(E**2 + N**2)))
    return Az_deg, El_deg

# Calculate azimuth and elevation for train and test sets
Az_train, El_train = calculate_az_el(df_filtered_train)
Az_test, El_test = calculate_az_el(df_filtered_test)

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(Az_train, El_train, color='blue', label='Train (Morning)', alpha=0.7)
plt.scatter(Az_test, El_test, color='red', label='Test (Evening)', alpha=0.7)
plt.xlabel('Azimuth (degrees)')
plt.ylabel('Elevation (degrees)')
plt.title('Azimuth vs Elevation')
plt.legend()
plt.grid(True)
plt.show()
plt.savefig("Azimuth_vs_Elevation.png", dpi=300)



# Alles heliostatIDs auslesen
helIDs = df.loc[:,'HeliostatId'].unique()    
helIDs.sort()


# # die Bilder zu dem jeweiligen Heliostaten bekommst du über die IDs der Datenpunkte
# transform = transforms.ToTensor()
# flux_dir = '/workVERLEIHNIX/mk/Calib2022fluxC'

# # durch alle Heliostaten iterieren und die zugehörigen Datenpunkte laden
# for helID in tqdm(helIDs):
#     heliostatDF = df.loc[(df['HeliostatId']==helID) & (df['IsDeleted']==0)]

#     # Sonnenpositionen auslesen und in Az und El umrechnen (musst mal schauen, ob du die gleiche Definition von Az nehmen willst)
#     E = np.array(heliostatDF.loc[:,'SunPosE'])
#     N = -np.array(heliostatDF.loc[:,'SunPosN'])
#     U = np.array(heliostatDF.loc[:,'SunPosU'])
#     Az_deg = np.degrees(np.arctan2(E, N))
#     El_deg = np.degrees(np.arctan2(U, np.sqrt(E**2 + N**2)))
#     Az_deg = np.where(Az_deg > 180, Az_deg - 360, Az_deg)

#     # Heliostat-Position auslesen
#     name = num_to_name(helID)
#     hp = df.loc[(df['InternalName'] == name)]
#     hel_pos = np.array([hp.iloc[0].at['x'],hp.iloc[0].at['y'],hp.iloc[0].at['z']])
#     hel_pos[2]-=87



# ids = heliostatDF.index.values.tolist()



