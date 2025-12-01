# Input columns
INTERNAL_NAME_INDEX = "InternalName"
"""Key for the input internal name index."""
ID_INDEX = "Id"
"""Key for the input ID index."""
CALIBRATION_ID_INDEX = "id"
"""Key for the calibration input ID index."""
HELIOSTAT_ID = "HeliostatId"
"""Key for the input heliostat ID index."""
X_Y_Z_POSITIONS = ["x", "y", "z"]
"""Key for the heliostat positions in x, y, z coordinates."""
HELIOSTAT_POSITIONS = ["latitude", "longitude", "Elevation"]
"""Key for the heliostat positions in latitude, longitude, and elevation."""
DEFLECTOMETRY_AVAILABLE = "DeflectometryAvailable"
"""Key indicating if deflectometry data is available."""
DATE_TIME = "DateTime"
"""Key for the input date and time index."""
CREATED_AT = "CreatedAt"
"""Key for the input created at index."""
FILE_CREATED_AT = "FileCreatedAt"
"""Key for the input file created at index."""
UPDATED_AT = "UpdatedAt"
"""Key for the input updated at index."""
YEAR = "Year"
"""Key for the year index."""
MONTH = "Month"
"""Key for the month index."""
HOUR = "Hour"
"""Key for the hour index."""
AZIMUTH = "Azimuth"
"""Key for the azimuth index."""
SUN_AZIMUTH = "sun_azimuth"
"""Key for the sun azimuth index."""
ELEVATION = "Elevation"
"""Key for the elevation index."""
ELEVATION_MIN = "Elevation_min"
"""Key for the min elevation index."""
ELEVATION_MAX = "Elevation_max"
"""Key for the max elevation index."""
SUN_ELEVATION = "sun_elevation"
"""Key for the sun elevation index."""
SYSTEM = "System"
"""Key for the system index."""
CALIBRATION_TARGET = "CalibrationTargetId"
"""Key for the calibration target ID index."""
AXIS1_MOTOR_SAVE = "axis_1_motor_position"
"""Key for the axis 1 motor position index used to save the data."""
AXIS1_MOTOR = "Axis1MotorPosition"
"""Key for the axis 1 motor position index used to load the data."""
AXIS2_MOTOR_SAVE = "axis_2_motor_position"
"""Key for the axis 1 motor position index used to save the data."""
AXIS2_MOTOR = "Axis2MotorPosition"
"""Key for the axis 1 motor position index used to load the data."""
MEASURED_SURFACE = "MeasuredSurface"
"""Key for the measured surface index."""
SUN_POSITION_EAST = "SunPosE"
"""Key for the E sun position index."""
SUN_POSITION_NORTH = "SunPosN"
"""Key for the N sun position index."""
SUN_POSITION_UP = "SunPosU"
"""Key for the U sun position index."""
DATA_SET_AZIMUTH = "DataSet_Azimuth"
"""Key for the data set azimuth index."""
JUNE_DISTANCE = "Jun_Distance"
"""Key for the june distance index."""
DECEMBER_DISTANCE = "Dec_Distance"
"""Key for the december distance index."""
DATETIME = "DateTime"
"""Key for the datetime index."""
SAVE_ID_INDEX = "Id"
"""Key for the ID index used to save data."""

# Dataset
TOTAL_INDEX = "Total"
"""Key for the total index when creating datasets."""
TRAIN_INDEX = "train"
"""Key for the train index when creating datasets."""
TEST_INDEX = "test"
"""Key for the test index when creating datasets."""
VALIDATION_INDEX = "validation"
"""Key for the validation index when creating datasets."""

# STAC
STAC_VERSION = "1.0.0"
"""Mapping for the STAC Version."""
VIEW_EXTENSION = "https://stac-extensions.github.io/view/v1.0.0/schema.json"
"""Mapping for the View STAC Extension."""
PROCESSING_EXTENSION = "https://stac-extensions.github.io/processing/v1.2.0/schema.json"
"""Mapping for the Processing STAC Extension."""
LICENSE = "CDLA-2.0"
"""Mapping for the license used."""
LICENSE_LINK = {
    "rel": "license",
    "href": "https://cdla.dev/permissive-2-0/",
    "type": "text/html",
    "title": "Community Data License Agreement – Permissive – Version 2.0",
}
"""Dictionary containing a link to a description and overview of the CDLA license used."""
PAINT_URL = "https://github.com/ARTIST-Association/PAINT/"
"""Mapping to the PAINT URL."""
DLR = {
    "name": "German Aerospace Center (DLR)",
    "description": "National center for aerospace, energy and transportation research of Germany",
    "roles": ["licensor", "producer", "processor"],
    "url": PAINT_URL,
}
"""Dictionary containing contact information for the DLR."""
KIT = {
    "name": "Karlsruhe Institute of Technology (KIT)",
    "description": "Public research center and university in Karlsruhe, Germany",
    "roles": ["producer", "processor", "host"],
    "url": PAINT_URL,
}
"""Dictionary containing contact information for KIT."""
POWER_PLANT_GPPD_ID = "WRI1030197"
"""Mapping to the power plant global ID."""
POWER_PLANT_ALT = 87.0
"""Mapping to the power plant altitude."""
POWER_PLANT_KEY = "power_plant_properties"
"""Mapping to the power plant properties key."""
ID_KEY = "ID"
"""Mapping to the power plant ID key."""
GK_HEIGHT_BASE = 5642086.619
"""Mapping to the Gauss-Krüger reference for the height base."""
GK_RIGHT_BASE = 2527317.095
"""Mapping to the Gauss-Krüger reference for the right base."""

# Target coordinates
STJ_UPPER_COORDINATES = [
    [50.91339186595943, 6.387886052532388, 126.476],
    [50.91339196507306, 6.387885982262168, 133.684],
    [50.91339211259599, 6.387763286988281, 133.719],
    [50.91339215692524, 6.387763472205384, 126.506],
    [50.91339186595943, 6.387886052532388, 126.476],
]
"""List containing the coordinates of the STJ-Upper target."""
STJ_UPPER_BOUNDING_BOX = [
    50.91339186595943,
    6.387763286988281,
    126.476,
    50.91339215692524,
    6.387886052532388,
    133.719,
]
"""List containing the bounding box for the STJ-Upper target."""
STJ_UPPER_ENU = [
    [4.32, -3.23, 46.70],
    [4.32, -3.23, 39.48],
    [-4.30, -3.23, 46.70],
    [-4.30, -3.23, 39.48],
]
"""List containing the coordinates in ENU format for the STJ-Upper target."""
STJ_LOWER_COORDINATES = [
    [50.913391839040266, 6.38788603808917, 119.268],
    [50.91339186595943, 6.387886052532388, 126.47],
    [50.91339215692524, 6.387763472205384, 126.506],
    [50.9133923375531, 6.387763217765237, 119.279],
    [50.913391839040266, 6.38788603808917, 119.268],
]
"""List containing the coordinates of the STJ-Lower target."""
STJ_LOWER_BOUNDING_BOX = [
    50.913391839040266,
    6.387763217765237,
    119.268,
    50.9133923375531,
    6.387886052532388,
    126.506,
]
"""List containing the bounding box for the STJ-Lower target."""
STJ_LOWER_ENU = [
    [4.33, -3.23, 39.49],
    [4.33, -3.23, 32.27],
    [-4.29, -3.23, 39.49],
    [-4.29, -3.23, 32.27],
]
"""List containing the coordinates in ENU format for the STJ-Lower target."""
MFT_COORDINATES = [
    [50.91339634341573, 6.387612841591359, 135.789],
    [50.91339628900999, 6.387612983329584, 142.175],
    [50.913396616772935, 6.387536032350528, 142.172],
    [50.91339655432386, 6.3875358896401675, 135.783],
    [50.91339634341573, 6.387612841591359, 135.789],
]
"""List containing the coordinates of the MFT target."""
MFT_BOUNDING_BOX = [
    50.91339628900999,
    6.3875358896401675,
    135.783,
    50.913396616772935,
    6.387612983329584,
    142.175,
]
"""List containing the bounding box for the MFT target."""
MFT_ENU = [
    [-14.88, -2.83, 55.17],
    [-14.88, -2.83, 48.78],
    [-20.29, -2.83, 55.17],
    [-20.29, -2.83, 48.78],
]
"""List containing the coordinates in ENU format for the MFT target."""
RECEIVER_COORDINATES = [
    [50.913406544144294, 6.387853925842858, 139.86],
    [50.91342645401072, 6.387854205350705, 144.592],
    [50.91342676647371, 6.387795411983428, 144.593],
    [50.91340664929649, 6.387795301404112, 139.862],
    [50.913406544144294, 6.387853925842858, 139.86],
]
"""List containing the coordinates of the receiver."""
RECEIVER_BOUNDING_BOX = [
    50.913406544144294,
    6.387795301404112,
    139.86,
    50.91342645401072,
    6.387854205350705,
    144.593,
]
"""List containing the bounding box for the receiver target."""

# Target center coordinates
STJ_UPPER_CENTER = (50.91339203683997, 6.387824563513243, 130.09766666666667)
"""Tuple containing the coordinates of the center of the STJ-Upper target."""
STJ_LOWER_CENTER = (50.91339203683997, 6.387824563513243, 122.8815)
"""Tuple containing the coordinates of the center of the STJ-Lower target."""
MFT_CENTER = (50.91339645088695, 6.387574436728054, 138.97975)
"""Tuple containing the coordinates of the center of the MFT target."""
RECEIVER_CENTER = (50.91341660151, 6.387825304776098, 142.22674999999998)
"""Tuple containing the coordinates of the center of the receiver."""


CATALOG = "Catalog"
"""Mapping to a STAC catalog."""
COLLECTION = "Collection"
"""Mapping to a STAC collection."""
FEATURE = "Feature"
"""Mapping to a feature."""

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"
"""Mapping for the time format used in PAINT."""
TIME_FILE_FORMAT = "%Y-%m-%dZ%H-%M-%SZ"
"""Mapping for the time format used in file names."""

MIME_PNG = "image/png"
"""Mapping for the MIME type for PNG."""
MIME_GEOJSON = "application/geo+json"
"""Mapping for the MIME type for GeoJSON."""
MIME_HDF5 = "application/x-hdf5"
"""Mapping for the MIME type for HDF5."""
MIME_PDF = "application/pdf"
"""Mapping for the MIME type for PDF."""

URL_BASE = f"https://paint-database.org/{POWER_PLANT_GPPD_ID}"
"""Mapping for the base URL."""
SAVE_DEFLECTOMETRY = "Deflectometry"
"""Mapping for the location to save deflectometry data."""
SAVE_PROPERTIES = "Properties"
"""Mapping for the location to save properties data."""
SAVE_CALIBRATION = "Calibration"
"""Mapping for the location to save calibration data."""
SAVE_WEATHER = "Weather"
"""Mapping for the location to save weather data."""

CATALOG_ID = f"{POWER_PLANT_GPPD_ID}-catalog"
"""Mapping for the power plant catalog ID."""
CATALOG_FILE = f"{POWER_PLANT_GPPD_ID}-catalog-stac.json"
"""Mapping for the power plant catalog file name."""
CATALOGUE_URL = f"{URL_BASE}/{CATALOG_FILE}"
"""Mapping for the power plant catalog URL."""

HELIOSTAT_CATALOG_ID = "%s-heliostat-catalog"
"""Mapping for a heliostat catalog ID."""
HELIOSTAT_CATALOG_FILE = "%s-heliostat-catalog-stac.json"
"""Mapping for a heliostat catalog file name."""
HELIOSTAT_CATALOG_URL = f"{URL_BASE}/%s/{HELIOSTAT_CATALOG_FILE}"
"""Mapping for a heliostat catalog URL."""

CALIBRATION_COLLECTION_ID = "%s-calibration-collection"
"""Mapping for a calibration collection ID."""
CALIBRATION_COLLECTION_FILE = "%s-calibration-collection-stac.json"
"""Mapping for a calibration collection file name."""
CALIBRATION_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_CALIBRATION}/{CALIBRATION_COLLECTION_FILE}"
)
"""Mapping for a calibration collection URL."""
CALIBRATION_ITEM = "%d-calibration-item-stac.json"
"""Mapping for a calibration item file name."""
CALIBRATION_ITEM_URL = f"{URL_BASE}/%s/{SAVE_CALIBRATION}/{CALIBRATION_ITEM}"
"""Mapping for a calibration item URL."""
CALIBRATION_TARGET_TO_COORDINATES = {
    1: STJ_LOWER_COORDINATES,
    3: MFT_COORDINATES,
    4: STJ_UPPER_COORDINATES,
    5: STJ_UPPER_COORDINATES,
    6: STJ_UPPER_COORDINATES,
    7: STJ_LOWER_COORDINATES,
}
"""Mapping to convert calibration target numbers to coordinates."""
CALIBRATION_TARGET_TO_BOUNDING_BOX = {
    1: STJ_LOWER_BOUNDING_BOX,
    3: MFT_BOUNDING_BOX,
    4: STJ_UPPER_BOUNDING_BOX,
    5: STJ_UPPER_BOUNDING_BOX,
    6: STJ_UPPER_BOUNDING_BOX,
    7: STJ_LOWER_BOUNDING_BOX,
}
"""Mapping to convert calibration target numbers to bounding boxes."""

DEFLECTOMETRY_COLLECTION_ID = "%s-deflectometry-collection"
"""Mapping for a deflectometry collection ID."""
DEFLECTOMETRY_COLLECTION_FILE = "%s-deflectometry-collection-stac.json"
"""Mapping for a deflectometry collection file name."""
DEFLECTOMETRY_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_DEFLECTOMETRY}/{DEFLECTOMETRY_COLLECTION_FILE}"
)
"""Mapping for a deflectometry collection URL."""
DEFLECTOMETRY_ITEM = "%s-%s-deflectometry-item-stac.json"
"""Mapping for a deflectometry item file name."""
DEFLECTOMETRY_ITEM_URL = f"{URL_BASE}/%s/{SAVE_DEFLECTOMETRY}/{DEFLECTOMETRY_ITEM}"
"""Mapping for a deflectometry item URL."""
DEFLECTOMETRY_PDF_NAME = "%s-%s-deflectometry-result.pdf"
"""Mapping for a deflectometry results PDF summary file name."""
DEFLECTOMETRY_INSTRUMENTS = "QDec_2014-101"
"""Mapping for the instruments used in deflectometry measurements."""

HELIOSTAT_PROPERTIES_COLLECTION_ID = "%s-heliostat-properties-collection"
"""Mapping for a heliostat properties collection ID."""
HELIOSTAT_PROPERTIES_COLLECTION_FILE = "%s-heliostat-properties-collection-stac.json"
"""Mapping for a heliostat properties collection file name."""
HELIOSTAT_PROPERTIES_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_PROPERTIES}/{HELIOSTAT_PROPERTIES_COLLECTION_FILE}"
)
"""Mapping for a heliostat properties collection URL."""
HELIOSTAT_PROPERTIES_ITEM = "%s-heliostat-properties-item-stac.json"
"""Mapping for a heliostat properties item file name."""
HELIOSTAT_PROPERTIES_ITEM_URL = (
    f"{URL_BASE}/%s/{SAVE_PROPERTIES}/{HELIOSTAT_PROPERTIES_ITEM}"
)
"""Mapping for a heliostat properties item URL."""
HELIOSTAT_PROPERTIES_SAVE_NAME = "%s-heliostat-properties.json"
"""Mapping for a heliostat properties asset file name."""

WEATHER_COLLECTION_ID = "weather-collection"
"""Mapping for a weather collection ID."""
WEATHER_COLLECTION_FILE = "weather-collection-stac.json"
"""Mapping for a weather collection file name."""
WEATHER_COLLECTION_URL = f"{URL_BASE}/{SAVE_WEATHER}/{WEATHER_COLLECTION_FILE}"
"""Mapping for a weather collection URL."""

# STAC asset keys.
URL_KEY = "url"
"""Key to access URL."""
TITLE_KEY = "title"
"""Key to access title."""
LATITUDE_KEY = "latitude"
"""Key to access latitude."""
LONGITUDE_KEY = "longitude"
"""Key to access longitude."""
LATITUDE_MIN_KEY = "latitude_min"
"""Key to access min latitude."""
LONGITUDE_MIN_KEY = "longitude_min"
"""Key to access min longitude."""
LATITUDE_MAX_KEY = "latitude_max"
"""Key to access max latitude."""
LONGITUDE_MAX_KEY = "longitude_max"
"""Key to access max longitude."""
DEFLECTOMETRY_RAW_KEY = "raw_measurement"
"""Key to access raw measurements."""
DEFLECTOMETRY_FILLED_KEY = "filled_measurement"
"""Key to access filled measurements."""
DEFLECTOMETRY_RESULTS_KEY = "results_summary"
"""Key to access deflectometry results."""
CALIBRATION_RAW_IMAGE_KEY = "raw_image"
"""Key to access raw image."""
CALIBRATION_CROPPED_IMAGE_KEY = "cropped_image"
"""Key to access cropped image."""
CALIBRATION_FLUX_IMAGE_KEY = "flux_image"
"""Key to access flux image."""
CALIBRATION_FLUX_CENTERED_IMAGE_KEY = "flux_centered_image"
"""Key to access flux centered image."""
CALIBRATION_PROPERTIES_KEY = "calibration_properties"
"""Key to access calibration properties."""
FACET_PROPERTIES_KEY = "facet_properties"
"""Key to access facet properties."""
KINEMATIC_PROPERTIES_KEY = "kinematic_properties"
"""Key to access kinematic properties."""
CALIBRATION_PROPERTIES_NAME = "%d-calibration-properties"
"""Key to access calibration properties."""
WEATHER_DATA_KEY = "weather_data"
"""Key to access weather data."""

# Calibration properties
MOTOR_POS_KEY = "motor_position"
"""Key to access motor positions."""
TARGET_NAME_KEY = "target_name"
"""Key to access target name."""
FOCAL_SPOT_KEY = "focal_spot"
"""Key to access focal spot."""
UTIS_KEY = "UTIS"
"""Key to access UTIS field."""
UTIS_URL = "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization"
"""Mapping to the UTIS URL."""
UTIS_MODEL_CHECKPOINT = (
    "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization/"
    "raw/main/trained_models/utis_model_scripted.pt"
)
"""Mapping to the UTIS model checkpoint."""
HELIOS_KEY = "HeliOS"
"""Key to access HeliOS."""
TARGET_OFFSET_E = "TargetOffsetE"
"""Key to access target offset in the east direction."""
TARGET_OFFSET_N = "TargetOffsetN"
"""Key to access target offset in the north direction."""
TARGET_OFFSET_U = "TargetOffsetU"
"""Key to access target offset in the up direction."""
PAINT_REPO_URL = "https://github.com/ARTIST-Association/PAINT"
"""Mapping to the paint repository URL."""
UTIS_X = "ApX"
"""Key to access units in the X direction for UTIS."""
UTIS_Y = "ApY"
"""Key to access units in the Y direction for UTIS."""
UTIS_ELEVATION = "ApZ"
"""Key to access units in the Z direction for UTIS."""

# Convert deflectometry
FACET_KEY = "facet"
"""Key to access facets."""
SURFACE_NORMAL_KEY = "surface_normals"
"""Key to access surface normals."""
SURFACE_POINT_KEY = "surface_points"
"""Key to access surface points."""
DEFLECTOMETRY_SUFFIX = "-deflectometry.h5"
"""Mapping to the deflectometry suffix."""
FACET_PROPERTIES_SUFFIX = "-facet_properties.json"
"""Mapping to the facet properties suffix."""
DEFLECTOMETRY_CREATED_AT = "deflectometry_created_at"
"""Mapping to the deflectometry created at key."""
KINEMATIC_PROPERTIES_SUFFIX = "-kinematic_properties.json"
"""Mapping to the kinematic properties suffix."""

# Combine properties
EAST_KEY = "East"
"""Key for east coordinate."""
NORTH_KEY = "North"
"""Key for north coordinate."""
ALTITUDE_KEY = "Altitude"
"""Key for altitude coordinate."""
FIELD_ID = "FieldId"
"""Key for field ID."""
HELIOSTAT_SIZE = "Heliostat Size"
"""Key for heliostat size."""
KINEMATIC_KEY = "kinematic"
"""Key for kinematic."""
HEIGHT_ABOVE_GROUND = "HeightAboveGround"
"""Key for height above ground."""

# DWD KEYS
DWD_STATION_ID = "StationID"
"""Mapping for the station ID in the DWD data."""
DWD_STATION_NAME = "StationName"
"""Mapping for the station name in the DWD data."""
DWD_START = "start"
"""Mapping for the start point in time in the DWD data."""
DWD_END = "end"
"""Mapping for the end point in time in the DWD data."""
DWD_STAC_NAME = "dwd-weather-item-stac"
"""Mapping for the DWD data stac item file name."""
DWD_STAC_URL = f"{URL_BASE}/{SAVE_WEATHER}/{DWD_STAC_NAME}"
"""Mapping for the DWD data stac item URL."""

# Juelich weather keys
JUELICH_START = "start"
"""Mapping for the start point in time in the Jülich weather data."""
JUELICH_END = "end"
"""Mapping for the end point in time in the Jülich weather data."""
JUELICH_FILE_NAME = "%s-juelich-weather"
"""Mapping for a Jülich weather data file name."""
JUELICH_STAC_NAME = "%s-juelich-weather-item-stac"
"""Mapping for a Jülich weather data STAC item file name."""
JUELICH_STAC_URL = f"{URL_BASE}/{SAVE_WEATHER}/{JUELICH_STAC_NAME}"
"""Mapping for a Jülich weather data STAC item URL."""
JUELICH_WEATHER_LAT = 50.916518
"""Mapping for the Jülich weather station latitude."""
JUELICH_WEATHER_LON = 6.387409
"""Mapping for the Jülich weather station longitude."""
JUELICH_WEATHER_ALTITUDE = 89
"""Mapping for the Jülich weather station altitude."""
DATE_TIME_INDEX = "DateTimeIndex"
"""Mapping for the Jülich weather station data date time index."""

# Tower measurement keys
STJ_UPPER = "solar_tower_juelich_upper"
"""Mapping for Jülich solar tower upper name."""
STJ_LOWER = "solar_tower_juelich_lower"
"""Mapping for Jülich solar tower lower name."""
MFT = "multi_focus_tower"
"""Mapping for multi focus tower name."""
CENTER = "center"
"""Mapping for the center point for target coordinates."""
RECEIVER = "receiver"
"""Mapping for the receiver name."""
UPPER_RIGHT = "upper_right"
"""Mapping for the upper right for target coordinates."""
UPPER_MIDDLE = "upper_middle"
"""Mapping for the upper middle for target coordinates."""
UPPER_LEFT = "upper_left"
"""Mapping for the upper left for target coordinates."""
LOWER_RIGHT = "lower_right"
"""Mapping for the lower right for target coordinates."""
LOWER_MIDDLE = "lower_middle"
"""Mapping for the lower middle for target coordinates."""
LOWER_LEFT = "lower_left"
"""Mapping for the lower left for target coordinates."""
RECEIVER_OUTER_UPPER_RIGHT = "receiver_outer_upper_right"
"""Mapping for the receiver outer upper right coordinate."""
RECEIVER_OUTER_LOWER_RIGHT = "receiver_outer_lower_right"
"""Mapping for the receiver outer lower right coordinate."""
RECEIVER_OUTER_LOWER_LEFT = "receiver_outer_lower_left"
"""Mapping for the receiver outer lower left coordinate."""
RECEIVER_OUTER_UPPER_LEFT = "receiver_outer_upper_left"
"""Mapping for the receiver outer upper left coordinate."""
RECEIVER_INNER_UPPER_RIGHT = "receiver_inner_upper_right"
"""Mapping for the receiver inner upper right coordinate."""
RECEIVER_INNER_LOWER_RIGHT = "receiver_inner_lower_right"
"""Mapping for the receiver inner lower right coordinate."""
RECEIVER_INNER_LOWER_LEFT = "receiver_inner_lower_left"
"""Mapping for the receiver inner lower left coordinate."""
RECEIVER_INNER_UPPER_LEFT = "receiver_inner_upper_left"
"""Mapping for the receiver inner upper left coordinate."""
TOWER_START_DATETIME = "2013-02-25"
"""Mapping for the start date for tower measurements."""
TOWER_END_DATETIME = "2020-10-07"
"""Mapping for the end date for tower measurements."""
TOWER_KEY = "measurements"
"""Mapping for tower measurements key."""
TOWER_FILE_NAME = f"{POWER_PLANT_GPPD_ID}-tower-measurements"
"""Mapping for the tower measurements file name."""
TOWER_STAC_NAME = f"{POWER_PLANT_GPPD_ID}-tower-measurements-item-stac"
"""Mapping for the tower measurements STAC name."""
TOWER_STAC_URL = f"{URL_BASE}/{TOWER_STAC_NAME}.json"
"""Mapping for the tower measurements STAC URL."""
TOWER_NORMAL_VECTOR = (0, 1, 0)
"""Mapping for the tower targets normal vectors."""
RECEIVER_NORMAL_VECTOR = (0.0, 0.90630779, -0.42261826)
"""Mapping for the receiver normal vector."""
TOWER_NORMAL_VECTOR_KEY = "normal_vector"
"""Key for the tower normal vector."""
TOWER_COORDINATES_KEY = "coordinates"
"""Key for the tower coordinates."""
TOWER_TYPE_KEY = "type"
"""Key for the target type."""
PLANAR_KEY = "planar"
"""Key for a planar target type."""
CONVEX_CYLINDER_KEY = "convex_cylinder"
"""Key for a convex cylinder target type."""

CALIBRATION_TARGET_TO_NAME = {
    1: STJ_LOWER,
    3: MFT,
    4: STJ_UPPER,
    5: STJ_UPPER,
    6: STJ_UPPER,
    7: STJ_LOWER,
}
"""Mapping from target numbers to target names."""

# Cropper mappings
DESTINATION_SIZE = (3072, 1728)
"""Mapping for the destination size for the cropper."""
INITIAL_HEIGHT = 250
"""Mapping for the initial height for the cropper."""
HEIGHT_OFFSET = 1250
"""Mapping for the height offset for the cropper."""
INITIAL_WIDTH = 450
"""Mapping for the initial width for the cropper."""
WIDTH_OFFSET = 2222
"""Mapping for the width offset for the cropper."""
MARKERS_FOLDER = "markers"
"""Mapping for the folder containing the markers used for matching for the cropper."""

# Renovation mappings
RENOVATION_ERROR = "renovation_error"
"""Mapping for renovation error."""
RENOVATION_PROPERTIES_KEY = "renovation"
"""Key for the renovation properties"""
NO_RENOVATION = "No renovation performed"
"""Mapping indicating no renovation occurred."""
RENOVATION_ID = "Retrofit_mechanische_Umrüstung"
"""Mapping to the renovation ID."""

# Properties mappings
HELIOSTAT_POSITION_KEY = "heliostat_position"
"""Key for the heliostat position."""
HELIOSTAT_PROPERTIES_KEY = "heliostat-properties"
"""Key for the heliostat properties."""
HELIOSTAT_WIDTH_KEY = "width"
"""Key for the heliostat width."""
HELIOSTAT_HEIGHT_KEY = "height"
"""Key for the heliostat height."""
HELIOSTAT_WIDTH = 3.2200000286102295
"""Mapping to the heliostat width."""
HELIOSTAT_HEIGHT = 2.559999942779541
"""Mapping to the heliostat height."""

# Facet properties
FACET_1_TRANSLATION = [-0.8075, 0.6425, 0.0402]
"""Mapping to the facet 1 translation."""
FACET_1_ROTATION_E = [1, 1, 1]
"""Mapping to the facet 1 rotation in the east direction."""
FACET_1_ROTATION_N = [1, 1, 1]
"""Mapping to the facet 1 rotation in the north direction."""
FACET_2_TRANSLATION = [0.8075, 0.6425, 0.0402]
"""Mapping to the facet 2 translation."""
FACET_2_ROTATION_E = [1, 1, -1]
"""Mapping to the facet 2 rotation in the east direction."""
FACET_2_ROTATION_N = [-1, 1, 1]
"""Mapping to the facet 2 rotation in the north direction."""
FACET_3_TRANSLATION = [-0.8075, -0.6425, 0.0402]
"""Mapping to the facet 3 translation."""
FACET_3_ROTATION_E = [1, 1, 1]
"""Mapping to the facet 3 rotation in the east direction."""
FACET_3_ROTATION_N = [-1, 1, -1]
"""Mapping to the facet 3 rotation in the north direction."""
FACET_4_TRANSLATION = [0.8075, -0.6425, 0.0402]
"""Mapping to the facet 4 translation."""
FACET_4_ROTATION_E = [1, 1, -1]
"""Mapping to the facet 4 rotation in the east direction."""
FACET_4_ROTATION_N = [1, 1, -1]
"""Mapping to the facet 4 rotation in the north direction."""
FOUR_FACETS = 4
"""Mapping for four facets on the heliostat."""
SPAN_N = "spansN"
"""Key for the span vector in the north direction."""
SPAN_E = "spansE"
"""Key for the span vector in the east direction."""
FACETS_LIST = "facets"
"""Key for the the list of facets."""
NUM_FACETS = "number_of_facets"
"""Key for the number of facets."""
TRANSLATION_VECTOR = "translation_vector"
"""Key for the facet translation vector."""
CANTING_E = "canting_e"
"""Key for the canting vector in the east direction."""
CANTING_N = "canting_n"
"""Key for the canting vector in the north direction."""
CANTING_TYPE = "canting_type"
"""Key for the canting type."""
CANTING_KEY = "canting"
"""Key for the canting."""
MAP_CANTING_TO_READABLE = {"Rec": "receiver canting", "FE": "research level canting"}
"""Mapping from short canting description to readable canting description."""

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
"""Mapping for the WGS84 major axis constant."""
WGS84_B = 6356752.314245  # Minor axis in meters
"""Mapping for the WGS84 minor axis constant."""
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared
"""Mapping for the WGS84 eccentricity squared constant."""

# Keys for Area of Interest Values
AOE_WEST_LONGITUDE = 6.35
"""Mapping for the area of interest west longitude constant."""
AOE_SOUTH_LATITUDE = 50.85
"""Mapping for the area of interest south latitude constant."""
AOE_EAST_LONGITUDE = 6.45
"""Mapping for the area of interest east longitude constant."""
AOE_NORTH_LATITUDE = 50.95
"""Mapping for the area of interest north latitude constant."""

# Extra Kinematic Properties
FIRST_JOINT_TRANSLATION_E_KEY = "joint_translation_e_1"
"""Key for the first joint translation in the east direction."""
FIRST_JOINT_TRANSLATION_N_KEY = "joint_translation_n_1"
"""Key for the first joint translation in the north direction."""
FIRST_JOINT_TRANSLATION_U_KEY = "joint_translation_u_1"
"""Key for the first joint translation in the up direction."""
SECOND_JOINT_TRANSLATION_E_KEY = "joint_translation_e_2"
"""Key for the second joint translation in the east direction."""
SECOND_JOINT_TRANSLATION_N_KEY = "joint_translation_n_2"
"""Key for the second joint translation in the north direction."""
SECOND_JOINT_TRANSLATION_U_KEY = "joint_translation_u_2"
"""Key for the second joint translation in the up direction."""
CONCENTRATOR_TRANSLATION_E_KEY = "concentrator_translation_e"
"""Key for the concentrator translation in the east direction."""
CONCENTRATOR_TRANSLATION_N_KEY = "concentrator_translation_n"
"""Key for the concentrator translation in the north direction."""
CONCENTRATOR_TRANSLATION_U_KEY = "concentrator_translation_u"
"""Key for the concentrator translation in the up direction."""
FIRST_JOINT_TRANSLATION_E = 0.0
"""Mapping to the first joint translation in the east direction."""
FIRST_JOINT_TRANSLATION_N = 0.0
"""Mapping to the first joint translation in the north direction."""
FIRST_JOINT_TRANSLATION_U = 0.0
"""Mapping to the first joint translation in the up direction."""
SECOND_JOINT_TRANSLATION_E = 0.0
"""Mapping to the second joint translation in the east direction."""
SECOND_JOINT_TRANSLATION_N = 0.0
"""Mapping to the second joint translation in the north direction."""
SECOND_JOINT_TRANSLATION_U = 0.0
"""Mapping to the second joint translation in the up direction."""
CONCENTRATOR_TRANSLATION_E = 0.0
"""Mapping to the concentrator translation in the east direction."""
CONCENTRATOR_TRANSLATION_N = 0.175
"""Mapping to the concentrator translation in the north direction."""
CONCENTRATOR_TRANSLATION_U = 0.0
"""Mapping to the concentrator translation in the up direction."""
INITIAL_ORIENTATION_KEY = "initial_orientation"
"""Key for the initial orientation."""
INITIAL_ORIENTATION_VALUE = [0.0, -1.0, 0.0]
"""Mapping to the initial orientation value."""

ACTUATOR_KEY = "actuators"
"""Key for actuators."""
HELIOSTAT_PROPERTIES_CONVERSION_MAP = {
    "Type_axis": "type_axis",
    "MinCounts_axis": "min_increment",
    "MaxCounts_axis": "max_increment",
    "PulseRatio_axis": "increment",
    "A_axis": "offset_shift",
    "B_axis": "initial_stroke_length",
    "C_axis": "offset",
    "D_axis": "pivot_radius",
    "E_axis": "radius_shift",
    "Reversed_axis": "clockwise_axis_movement",
    "AngleK_axis": "initial_angle",
    "AngleMin_axis": "min_movement_angle",
    "AngleMax_axis": "max_movement_angle",
    "AngleW_axis": "movement_speed",
}
"""Mapping to convert heliostat properties keys to a readable format."""

# Keys for dataset splits and plots
AZIMUTH_SPLIT = "azimuth"
"""Key for the azimuth split type."""
SOLSTICE_SPLIT = "solstice"
"""Key for the solstice split type."""
BALANCED_SPLIT = "balanced"
"""Key for the balanced split type."""
HIGH_VARIANCE_SPLIT = "high_variance"
"""Key for the high-variance split type."""
SPLIT_KEY = "Split"
"""Key to access splits."""
DISTANCE_WINTER = "distance_winter"
"""Key for the distance to the winter solstice."""
DISTANCE_SUMMER = "distance_summer"
"""Key for the distance to the summer solstice."""
WINTER_SEASON = "winter"
"""Key for the winter season."""
TRAIN_TEST_VAL_COLORS = {
    TRAIN_INDEX: "#005AA0",
    TEST_INDEX: "#8CB423",
    VALIDATION_INDEX: "#D23264",
}
"""Key to apply different colours depending on the train, test and validation split."""

# Keys for Dataset file identifiers.
CALIBRATION_RAW_IMAGE_IDENTIFIER = "-raw.png"
"""Key for the raw image identifier."""
CALIBRATION_CROPPED_IMAGE_IDENTIFIER = "-cropped.png"
"""Key for the cropped image identifier."""
CALIBRATION_FLUX_IMAGE_IDENTIFIER = "-flux.png"
"""Key for the flux image identifier."""
CALIBRATION_FLUX_CENTERED_IMAGE_IDENTIFIER = "-flux-centered.png"
"""Key for the flux centered image identifier."""
CALIBRATION_PROPERTIES_IDENTIFIER = "-calibration-properties.json"
"""Key for the calibration properties identifier."""

CHECKPOINT_NAME = ".download_checkpoint.json"
"""Name for the heliostat checkpoint file when downloading data."""
WEATHER_CHECKPOINT_NAME = ".weather_checkpoint.json"
"""Name for the weather checkpoint file when downloading data."""
METADATA_CHECKPOINT_NAME = ".metadata_checkpoint.json"
CHECKPOINT_HREF = "href"
"""Key for the href value for the checkpoint data."""
CHECKPOINT_DONE = "done"
"""Key to mark if the download is complete for the checkpoint data."""
