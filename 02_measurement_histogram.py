import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils import calculate_az_el

def create_histogram(df, column, file_name, bins=20, x_ticks=None):
    plt.figure(figsize=(8, 6))
    plt.hist(df[column], bins=bins, color='skyblue', edgecolor='black')
    plt.title(f'Histogram of {column}')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    if x_ticks:
        plt.xticks(ticks=np.arange(len(x_ticks)), labels=x_ticks)
    plt.tight_layout()
    plt.savefig("02_"+file_name, dpi=300)
    plt.close()

    print(f"Saved histogram for {column} as {file_name}")

def create_stacked_bar_chart(df, time_column, file_name, x_labels=None):
    pivot_table = df.pivot_table(index=time_column, columns='Year', aggfunc='size', fill_value=0)
    pivot_table.plot(kind='bar', stacked=True, figsize=(10, 7), colormap='tab10')
    plt.xlabel(time_column)
    plt.ylabel('Count')
    plt.grid(True)
    if x_labels:
        plt.xticks(ticks=np.arange(len(x_labels)), labels=x_labels)
    plt.legend(title='Year')
    plt.tight_layout()
    plt.savefig("02_"+file_name, dpi=300)
    plt.close()
    print(f"Saved stacked bar chart for {time_column} as {file_name}")

# Load Measurement CSV
measurement_path = 'data/DatenHeliOS/calib_data.csv'
df_measurements = pd.read_csv(measurement_path).set_index('id')
df_measurements['CreatedAt'] = pd.to_datetime(df_measurements['CreatedAt'])
df_measurements['Year'] = df_measurements['CreatedAt'].dt.year
df_measurements['Month'], df_measurements['Hour'] = df_measurements['CreatedAt'].dt.month, df_measurements['CreatedAt'].dt.hour

# Calculate Azimuth and Elevation
df_measurements['Azimuth'], df_measurements['Elevation'] = calculate_az_el(df_measurements)

# Columns of interest for histograms excluding SunPosE, SunPosN, SunPosU
columns_of_interest = ["Axis1MotorPosition", "Axis2MotorPosition"]

# Create individual histograms for specified columns
for column in columns_of_interest:
    create_histogram(df_measurements, column, f"Histogram_{column}.pdf")
    create_histogram(df_measurements, column, f"Histogram_{column}.png")

create_stacked_bar_chart(df_measurements, 'Month', 'StackedBar_Month.pdf', x_labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
create_stacked_bar_chart(df_measurements, 'Hour', 'StackedBar_Hour.pdf')

create_stacked_bar_chart(df_measurements, 'Month', 'StackedBar_Month.png', x_labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
create_stacked_bar_chart(df_measurements, 'Hour', 'StackedBar_Hour.png')

plt.figure(figsize=(10, 8))
sns.jointplot(x='Azimuth', y='Elevation', data=df_measurements, kind='hex', color='skyblue')
plt.xlabel('Azimuth')
plt.ylabel('Elevation')
plt.tight_layout()
plt.savefig('02_JointPlot_Azimuth_Elevation.pdf', dpi=300)
plt.savefig('02_JointPlot_Azimuth_Elevation.png', dpi=300)
plt.close()

# Determine the range for centering the joint plot
xlim = (100, 550)
ylim = (200, 500)

# Create joint plot for ImageOffsetX and ImageOffsetY with adjusted parameters
plt.figure(figsize=(10, 8))
sns.jointplot(x='ImageOffsetX', y='ImageOffsetY', data=df_measurements, kind='hex', palette='skyblue', gridsize=200, cmap='Blues', xlim=xlim, ylim=ylim)
plt.xlabel('ImageOffsetX')
plt.ylabel('ImageOffsetY')
plt.tight_layout()
plt.savefig('02_JointPlot_ImageOffsetX_ImageOffsetY.pdf', dpi=300)
plt.savefig('02_JointPlot_ImageOffsetX_ImageOffsetY.png', dpi=300)
plt.close()