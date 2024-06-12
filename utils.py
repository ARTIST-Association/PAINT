import matplotlib.pyplot as plt
import numpy as np

# Function to calculate azimuth and elevation
def calculate_az_el(df):
    E = np.array(df['SunPosE'])
    N = -np.array(df['SunPosN'])
    U = np.array(df['SunPosU'])
    Az_deg = np.degrees(np.arctan2(E, N))
    El_deg = np.degrees(np.arctan2(U, np.sqrt(E**2 + N**2)))
    return Az_deg, El_deg

def num_to_name(helID):
    """Returns the name of a heliostat based on its ID"""
    str_ = str(helID)
    name = chr(ord('A') + int(str_[0]) - 1)
    name += chr(ord('A') + int(str_[1:3]) - 1)
    name += str_[3:]
    return name


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

    plt.savefig(f"04_Month_Split_{train_split_name}.png", dpi=300)

def plot_scatter_az_el(filtered_df, set_name, file_name):
    colors = {'train': 'blue', 'test': 'red', 'validation': 'green'}
    
    plt.figure(figsize=(10, 6))
    
    for dataset_type in ['train', 'test', 'validation']:
        subset = filtered_df[filtered_df[set_name] == dataset_type]
        plt.scatter(subset['Azimuth'], subset['Elevation'], color=colors[dataset_type], label=dataset_type, alpha=0.6)
    
    plt.xlabel('Azimuth (degrees)')
    plt.ylabel('Elevation (degrees)')
    plt.title('Scatter Plot of Azimuth vs. Elevation for example Heliostat')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig(file_name, dpi=300)