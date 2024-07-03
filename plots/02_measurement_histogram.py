import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from paint.util.utils import calculate_az_el
import matplotlib.gridspec as gridspec

def create_histogram(ax, df, column, bins=20, x_ticks=None):
    ax.hist(df[column], bins=bins, color='skyblue', edgecolor='black')
    ax.set_title(f'Histogram of {column}')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    if x_ticks:
        ax.set_xticks(np.arange(len(x_ticks)))
        ax.set_xticklabels(x_ticks)

    return ax

def create_stacked_bar_chart(ax, df, time_column, x_labels=None):
    pivot_table = df.pivot_table(index=time_column, columns='Year', aggfunc='size', fill_value=0)
    pivot_table.plot(kind='bar', stacked=True, ax=ax, figsize=(10, 7), colormap='tab10')
    ax.set_xlabel(time_column)
    ax.set_ylabel('Count')
    ax.grid(True)
    if x_labels:
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_xticklabels(x_labels)
    ax.legend(title='Year')
    return ax

def create_joint_plot(df, x_column, y_column, width, height, xlim=None, ylim=None):
    grid = sns.jointplot(x=x_column, y=y_column, data=df, kind='kde', color='skyblue', height=12, ratio=8, xlim=xlim, ylim=ylim,gridsize=100)
    grid.fig.set_figwidth(width)
    grid.fig.set_figheight(height)
    grid.savefig(f"02_joint_plot_{x_column}_{y_column}.png", dpi=300)
    grid.savefig(f"02_joint_plot_{x_column}_{y_column}.pdf", dpi=300)
    return ax


# Define your calculate_az_el function here if it's not imported from utils

# Load Measurement CSV
measurement_path = 'data/DatenHeliOS/calib_data.csv'
df_measurements = pd.read_csv(measurement_path).set_index('id')
df_measurements['CreatedAt'] = pd.to_datetime(df_measurements['CreatedAt'])
df_measurements['Year'] = df_measurements['CreatedAt'].dt.year
df_measurements['Month'], df_measurements['Hour'] = df_measurements['CreatedAt'].dt.month, df_measurements['CreatedAt'].dt.hour

# Calculate Azimuth and Elevation
df_measurements['Azimuth'], df_measurements['Elevation'] = calculate_az_el(df_measurements)

# Create a main figure with gridspec
fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(2, 2, figure=fig)

# Create individual histograms for specified columns
for i, column in enumerate(["Axis1MotorPosition", "Axis2MotorPosition"]):
    ax = fig.add_subplot(gs[i])
    create_histogram(ax, df_measurements, column)
    ax.set_title(f'Histogram of {column}')

# Create stacked bar charts
ax_stacked_month = fig.add_subplot(gs[1, 0])
create_stacked_bar_chart(ax_stacked_month, df_measurements, 'Month', x_labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax_stacked_hour = fig.add_subplot(gs[1, 1])
create_stacked_bar_chart(ax_stacked_hour, df_measurements, 'Hour')

plt.tight_layout()
plt.savefig('02_histograms.png')  # Save the combined figure
plt.savefig('02_histograms.pdf')
plt.close

# create_joint_plot(df_measurements, 'Azimuth', 'Elevation', width=10, height=10)
create_joint_plot(df_measurements, 'TargetOffsetE', 'TargetOffsetU', width=10, height=10, xlim=(-20,3), ylim=(121, 140))