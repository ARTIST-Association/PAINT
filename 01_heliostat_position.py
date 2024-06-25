import pandas as pd
import matplotlib.pyplot as plt
from utils import num_to_name#
from matplotlib.patches import Rectangle

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

deflectometry_available = [
    'AA32_210819', 'AA31_210819', 'AA36_150723', 'AA38_140910', 'AB35_210819', 'AB43_220303', 'AC35_210819', 'AC36_210819', 'AC37_210819', 'AD35_210819',
    'AD36_210819', 'AD37_210819', 'AH36_160407', 'AI21_160510', 'AI43_171122', 'AI44_171122', 'AI45_171122', 'AK30_210909', 'AK31_210909', 'AK32_210909',
    'AK33_210909', 'AK34_210909', 'AK35_210909', 'AK36_210909', 'AK37_210909', 'AN33_220303', 'AN35_220303', 'AO33_210909', 'AO33_220303', 'AO34_220303',
    'AO35_220303', 'AO49_220303', 'AP34_220303', 'AP35_220303', 'AP38_180807', 'AP49_220303', 'AP50_220303', 'AP51_220303', 'AP60_220303', 'AQ25_210909',
    'AQ26_210909', 'AU66_160510', 'AV36_150424', 'AV38_141125', 'AY19_160510', 'AY36_160510', 'AY41_160510', 'AY55_220303', 'AY57_220303', 'AZ43_150428',
    'AZ56_220303', 'BA41_150424', 'BB40_220303', 'BD34_150803', 'BF27_160510', 'BF29_160510', 'BF37_160510', 'BF39_160510', 'BG25_160510', 'BG30_160510',
    'BG34_160510', 'BJ25_190227', 'BJ26_190227', 'BJ27_190227', 'BJ28_190227', 'BJ30_190227', 'BJ31_190227', 'BJ32_190227', 'BJ32_191114', 'BK19_160510',
    'BL31_161005', 'BM23_160808', 'BM25_160808', 'BM27_160808', 'BM29_160808', 'BM31_160808', 'BM33_160808', 'BM35_160808', 'BM35_161011', 'BM37_161005',
    'BM37_161011', 'BM39_160808', 'BM41_160808', 'BM43_160808', 'BM45_160808', 'BM47_160808', 'BM49_160808', 'BM51_160808', 'BM53_160808', 'BM55_160808',
    'BM55_161005', 'BM55_161011', 'BN26_160510', 'BN26_160808', 'BN28_160808', 'BN30_160510', 'BN30_160808', 'BN32_160510', 'BN32_160808', 'BN34_160510',
    'BN34_160808', 'BN36_160808', 'BN38_160510', 'BN38_160808', 'BN40_161005', 'BN40_161011', 'BN42_160808', 'BN46_160808', 'AA28_230907', 'AB26_230907',
    'AB27_230907', 'AB45_230907', 'AY37_150424', 'AC35_210819', 'AL30_150424', 'AL30_150422', 'AL30_150723', 'AM31_150723', 'AL30_160510', 'AM31_160510',
    'AL30_191114', 'AM31_191114', 'AA49_140910', 'AA50_140910', 'AI32_171122', 'AI33_171122', 'AI34_171122', 'AI35_171122', 'AO51_220303', 'AP28_180807',
    'AP29_180807', 'AP30_180807', 'AP31_180807', 'AP32_180807', 'AP61_220303', 'AQ24_210909', 'AQ28_210909', 'AQ30_210909', 'AQ31_210909', 'AQ32_210909',
    'AU65_160510', 'AU68_160510', 'AU69_160510', 'AU71_160510', 'AY37_160510', 'AZ21_160510', 'AZ26_220303', 'AZ27_220303', 'AZ28_220303', 'AZ33_150424',
    'AZ33_150428', 'AZ34_150428', 'BH49_191114', 'BH65_160510'
]
 #TODO load from file


# Strip date from the list and get unique Heliostat IDs
highlighted_heliostats = list(set([h.split('_')[0] for h in deflectometry_available]))

# Add a column to identify highlighted heliostats
merged_df['highlight'] = merged_df.index.isin(highlighted_heliostats)



plt.figure(figsize=(10, 6))
plt.scatter(merged_df['x'], merged_df['y'], c=merged_df['count'], cmap='coolwarm', alpha=0.7)

# Highlight specific heliostats
highlighted = merged_df[merged_df['highlight']]
plt.plot(highlighted['x'], highlighted['y'], 'o', markerfacecolor='none', markeredgecolor='red', markersize=7, label='Highlighted Heliostats')



plt.colorbar(label='# Measurements')
plt.xlabel('East-West distance to tower')
plt.ylabel('North distance to tower')
plt.grid(True)

# Add square at (0, 0)
rect = Rectangle((-5, -8), 10, 8, linewidth=2, edgecolor='darkgrey', facecolor='grey')
plt.gca().add_patch(rect)
y_min = -8  # Define your desired minimum y-value
y_max = 250
plt.ylim(y_min, y_max)
plt.tight_layout()
plt.show()
plt.savefig("01_heliostat_positions.png", dpi=300)
plt.savefig("01_heliostat_positions.pdf", dpi=300)
