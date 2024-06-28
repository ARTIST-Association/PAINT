import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec

# File paths
file_paths = [
    '01_heliostat_positions.png',
    '02_Histogram_Axis1MotorPosition.png',
    '02_Histogram_Axis2MotorPosition.png',
    '02_StackedBar_Hour.png',
    '02_StackedBar_Month.png',
    '02_JointPlot_Azimuth_Elevation.png',
    '02_JointPlot_ImageOffsetX_ImageOffsetY.png'
]

# Load images
images = [mpimg.imread(fp) for fp in file_paths]

# Create a figure
fig = plt.figure(figsize=(20, 20))

# Create a 6x6 GridSpec
gs = gridspec.GridSpec(6, 6, figure=fig)

# Assign images to subplots
# 01_heliostat_positions.png (1. to 2. row, 1. to 4. column)
ax1 = fig.add_subplot(gs[0:2, 0:4])
ax1.imshow(images[0])
ax1.axis('off')

# 02_Histogram_Axis1MotorPosition.png (1. row, 5. column)
ax2 = fig.add_subplot(gs[0, 4])
ax2.imshow(images[1])
ax2.axis('off')

# 02_Histogram_Axis2MotorPosition.png (2. row, 5. column)
ax3 = fig.add_subplot(gs[1, 4])
ax3.imshow(images[2])
ax3.axis('off')

# 02_StackedBar_Hour.png (1. row, 6. column)
ax4 = fig.add_subplot(gs[0, 5])
ax4.imshow(images[3])
ax4.axis('off')

# 02_StackedBar_Month.png (2. row, 6. column)
ax5 = fig.add_subplot(gs[1, 5])
ax5.imshow(images[4])
ax5.axis('off')

# 02_JointPlot_Azimuth_Elevation.png (3. to 4. row, 1. to 4. column)
ax6 = fig.add_subplot(gs[2:4, 0:4])
ax6.imshow(images[5])
ax6.axis('off')

# 02_JointPlot_ImageOffsetX_ImageOffsetY.png (3. to 4. row, 5. to 6. column)
ax7 = fig.add_subplot(gs[2:4, 4:6])
ax7.imshow(images[6])
ax7.axis('off')

# Hide any remaining empty subplots by removing them
# Iterate over all grid cells and remove any that are not assigned
for row in range(6):
    for col in range(6):
        if not gs[row, col].get_gridspec().figure == fig:
            fig.add_subplot(gs[row, col]).axis('off')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.savefig("02_overview_figure.png")
