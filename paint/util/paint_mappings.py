# CSV columns
INTERNAL_NAME_INDEX = "InternalName"
ID_INDEX = "id"
HELIOSTAT_ID = "HeliostatId"
X_Y_Z_POSITIONS = ["x", "y", "z"]
DEFLECTOMETRY_AVAILABLE = "DeflectometryAvailable"
CREATED_AT = "CreatedAt"
FILE_CREATED_AT = "FileCreatedAt"
UPDATED_AT = "UpdatedAt"
YEAR = "Year"
MONTH = "Month"
HOUR = "Hour"
AZIMUTH = "Azimuth"
SUN_AZIMUTH = "Sun_azimuth"
ELEVATION = "Elevation"
ELEVATION_MIN = "Elevation_min"
ELEVATION_MAX = "Elevation_max"
SUN_ELEVATION = "Sun_elevation"
SYSTEM = "System"
CALIBRATION_TARGET = "CalibrationTargetId"
AXIS1_MOTOR = "Axis1MotorPosition"
AXIS2_MOTOR = "Axis2MotorPosition"
MEASURED_SURFACE = "MeasuredSurface"
SUN_POSITION_EAST = "SunPosE"
SUN_POSITION_NORTH = "SunPosN"
SUN_POSITION_UP = "SunPosU"
DATA_SET_AZIMUTH = "DataSet_Azimuth"
JUNE_DISTANCE = "Jun_Distance"
DECEMBER_DISTANCE = "Dec_Distance"
DATETIME = "DateTime"

# Dataset
TOTAL_INDEX = "Total"
TRAIN_INDEX = "train"
TEST_INDEX = "test"
VALIDATION_INDEX = "validation"

# STAC
STAC_VERSION = "1.0.0"
VIEW_EXTENSION = "https://stac-extensions.github.io/view/v1.0.0/schema.json"
PROCESSING_EXTENSION = "https://stac-extensions.github.io/processing/v1.2.0/schema.json"
LICENSE = "CDLA-2.0"
LICENSE_LINK = {
    "rel": "license",
    "href": "https://cdla.dev/permissive-2-0/",
    "type": "text/html",
    "title": "Community Data License Agreement – Permissive – Version 2.0",
}
PAINT_URL = "https://github.com/ARTIST-Association/PAINT/"
DLR = {
    "name": "German Aerospace Center (DLR)",
    "description": "National center for aerospace, energy and transportation research of Germany",
    "roles": ["licensor", "producer", "processor"],
    "url": PAINT_URL,
}
KIT = {
    "name": "Karlsruhe Institute of Technology (KIT)",
    "description": "Public research center and university in Karlsruhe, Germany",
    "roles": ["producer", "processor", "host"],
    "url": PAINT_URL,
}
POWER_PLANT_GPPD_ID = "WRI1030197"
POWER_PLANT_LAT = 50.91342112259258
POWER_PLANT_LON = 6.387824755874856
POWER_PLANT_ALT = 87.0
POWER_PLANT_KEY = "power_plant_properties"
ID_KEY = "ID"
GK_HEIGHT_BASE = 5642086.619 - 0.063
GK_RIGHT_BASE = 2527317.095 - 1.626

# Target coordinates
STJ_UPPER_COORDINATES = [
    [50.91339186595943, 6.387886052532388, 126.476],
    [50.91339196507306, 6.387885982262168, 133.684],
    [50.91339211259599, 6.387763286988281, 133.719],
    [50.91339215692524, 6.387763472205384, 126.506],
    [50.91339186595943, 6.387886052532388, 126.476],
]
STJ_UPPER_BOUNDING_BOX = [
    50.91339186595943,
    6.387763286988281,
    126.476,
    50.91339215692524,
    6.387886052532388,
    133.719,
]
STJ_UPPER_ENU = [
    [4.32, -3.23, 46.70],
    [4.32, -3.23, 39.48],
    [-4.30, -3.23, 46.70],
    [-4.30, -3.23, 39.48],
]
STJ_LOWER_COORDINATES = [
    [50.913391839040266, 6.38788603808917, 119.268],
    [50.91339186595943, 6.387886052532388, 126.47],
    [50.91339215692524, 6.387763472205384, 126.506],
    [50.9133923375531, 6.387763217765237, 119.279],
    [50.913391839040266, 6.38788603808917, 119.268],
]
STJ_LOWER_BOUNDING_BOX = [
    50.913391839040266,
    6.387763217765237,
    119.268,
    50.9133923375531,
    6.387886052532388,
    126.506,
]
STJ_LOWER_ENU = [
    [4.33, -3.23, 39.49],
    [4.33, -3.23, 32.27],
    [-4.29, -3.23, 39.49],
    [-4.29, -3.23, 32.27],
]
MFT_COORDINATES = [
    [50.91339634341573, 6.387612841591359, 135.789],
    [50.91339628900999, 6.387612983329584, 142.175],
    [50.913396616772935, 6.387536032350528, 142.172],
    [50.91339655432386, 6.3875358896401675, 135.783],
    [50.91339634341573, 6.387612841591359, 135.789],
]
MFT_BOUNDING_BOX = [
    50.91339628900999,
    6.3875358896401675,
    135.783,
    50.913396616772935,
    6.387612983329584,
    142.175,
]
MFT_ENU = [
    [-14.88, -2.83, 55.17],
    [-14.88, -2.83, 48.78],
    [-20.29, -2.83, 55.17],
    [-20.29, -2.83, 48.78],
]
RECEIVER_COORDINATES = [
    [50.913406544144294, 6.387853925842858, 139.86],
    [50.91342645401072, 6.387854205350705, 144.592],
    [50.91342387604005, 6.387765392341336, 144.593],
    [50.91340664929649, 6.387795301404112, 139.862],
    [50.913406544144294, 6.387853925842858, 139.86],
]
RECEIVER_BOUNDING_BOX = [
    50.913406544144294,
    6.387765392341336,
    139.86,
    50.91342645401072,
    6.387854205350705,
    144.593,
]

# Target center coordinates
STJ_UPPER_CENTER = (50.91339203683997, 6.387824563513243, 130.09766666666667)
STJ_LOWER_CENTER = (50.91339203683997, 6.387824563513243, 122.8815)
MFT_CENTER = (50.91339645088695, 6.387574436728054, 138.97975)
RECEIVER_CENTER = (50.91341660151, 6.387825304776098, 142.22674999999998)


CATALOG = "Catalog"
COLLECTION = "Collection"
FEATURE = "Feature"

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"
TIME_FILE_FORMAT = "%Y-%m-%dZ%H-%M-%SZ"

MIME_PNG = "image/png"
MIME_GEOJSON = "application/geo+json"
MIME_HDF5 = "application/x-hdf5"
MIME_PDF = "application/pdf"

URL_BASE = f"https://paint-database.org/{POWER_PLANT_GPPD_ID}"
SAVE_DEFLECTOMETRY = "Deflectometry"
SAVE_PROPERTIES = "Properties"
SAVE_CALIBRATION = "Calibration"
SAVE_WEATHER = "Weather"

CATALOG_ID = f"{POWER_PLANT_GPPD_ID}-catalog"
CATALOG_FILE = f"{POWER_PLANT_GPPD_ID}-catalog-stac.json"

HELIOSTAT_CATALOG_ID = "%s-heliostat-catalog"
HELIOSTAT_CATALOG_FILE = "%s-heliostat-catalog-stac.json"
HELIOSTAT_CATALOG_URL = f"{URL_BASE}/%s/{HELIOSTAT_CATALOG_FILE}"


CATALOGUE_URL = f"{URL_BASE}/{CATALOG_FILE}"

CALIBRATION_COLLECTION_ID = "%s-calibration-collection"
CALIBRATION_COLLECTION_FILE = "%s-calibration-collection-stac.json"
CALIBRATION_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_CALIBRATION}/{CALIBRATION_COLLECTION_FILE}"
)
CALIBRATION_ITEM = "%d-calibration-item-stac.json"
CALIBRATION_ITEM_URL = f"{URL_BASE}/%s/{SAVE_CALIBRATION}/{CALIBRATION_ITEM}"
CALIBRATION_TARGET_TO_COORDINATES = {
    1: STJ_LOWER_COORDINATES,
    3: MFT_COORDINATES,
    4: STJ_UPPER_COORDINATES,
    5: STJ_UPPER_COORDINATES,
    6: STJ_UPPER_COORDINATES,
    7: STJ_LOWER_COORDINATES,
}
CALIBRATION_TARGET_TO_BOUNDING_BOX = {
    1: STJ_LOWER_BOUNDING_BOX,
    3: MFT_BOUNDING_BOX,
    4: STJ_UPPER_BOUNDING_BOX,
    5: STJ_UPPER_BOUNDING_BOX,
    6: STJ_UPPER_BOUNDING_BOX,
    7: STJ_LOWER_BOUNDING_BOX,
}
DEFLECTOMETRY_COLLECTION_ID = "%s-deflectometry-collection"
DEFLECTOMETRY_COLLECTION_FILE = "%s-deflectometry-collection-stac.json"
DEFLECTOMETRY_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_DEFLECTOMETRY}/{DEFLECTOMETRY_COLLECTION_FILE}"
)
DEFLECTOMETRY_ITEM = "%s-%s-deflectometry-item-stac.json"
DEFLECTOMETRY_ITEM_URL = f"{URL_BASE}/%s/{SAVE_DEFLECTOMETRY}/{DEFLECTOMETRY_ITEM}"

DEFLECTOMETRY_PDF_NAME = "%s-%s-deflectometry-result.pdf"
DEFLECTOMETRY_INSTRUMENTS = "QDec_2014-101"

HELIOSTAT_PROPERTIES_COLLECTION_ID = "%s-heliostat_properties-collection"
HELIOSTAT_PROPERTIES_COLLECTION_FILE = "%s-heliostat_properties-collection-stac.json"
HELIOSTAT_PROPERTIES_COLLECTION_URL = (
    f"{URL_BASE}/%s/{SAVE_PROPERTIES}/{HELIOSTAT_PROPERTIES_COLLECTION_FILE}"
)
HELIOSTAT_PROPERTIES_ITEM = "%s-heliostat_properties-item-stac.json"
HELIOSTAT_PROPERTIES_ITEM_URL = (
    f"{URL_BASE}/%s/{SAVE_PROPERTIES}/{HELIOSTAT_PROPERTIES_ITEM}"
)
HELIOSTAT_PROPERTIES_SAVE_NAME = "%s-heliostat_properties.json"

WEATHER_COLLECTION_ID = "weather-collection"
WEATHER_COLLECTION_FILE = "weather-collection-stac.json"
WEATHER_COLLECTION_URL = f"{URL_BASE}/{SAVE_WEATHER}/{WEATHER_COLLECTION_FILE}"


URL_KEY = "url"
TITLE_KEY = "title"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
LATITUDE_MIN_KEY = "latitude_min"
LONGITUDE_MIN_KEY = "longitude_min"
LATITUDE_MAX_KEY = "latitude_max"
LONGITUDE_MAX_KEY = "longitude_max"
DEFLECTOMETRY_RAW_KEY = "raw_measurement"
DEFLECTOMETRY_FILLED_KEY = "filled_measurement"
DEFLECTOMETRY_RESULTS_KEY = "results_summary"
CALIBRATION_RAW_IMAGE_KEY = "raw_image"
CALIBRATION_CROPPED_IMAGE_KEY = "cropped_image"
CALIBRATION_FLUX_IMAGE_KEY = "flux_image"
CALIBRATION_FLUX_CENTERED_IMAGE_KEY = "flux_centered_image"
CALIBRATION_PROPERTIES_KEY = "calibration_properties"
FACET_PROPERTIES_KEY = "facet_properties"
KINEMATIC_PROPERTIES_KEY = "kinematic_properties"
CALIBRATION_PROPERTIES_NAME = "%d-calibration-properties"
WEATHER_DATA_KEY = "weather_data"

# Calibration properties
MOTOR_POS_KEY = "motor_position"
TARGET_NAME_KEY = "target_name"
FOCAL_SPOT_KEY = "focal_spot"
UTIS_KEY = "UTIS"
UTIS_URL = "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization"
UTIS_MODEL_CHECKPOINT = (
    "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization/"
    "raw/main/trained_models/utis_model_scripted.pt"
)
HELIOS_KEY = "HeliOS"
TARGET_OFFSET_E = "TargetOffsetE"
TARGET_OFFSET_N = "TargetOffsetN"
TARGET_OFFSET_U = "TargetOffsetU"
PAINT_REPO_URL = "https://github.com/ARTIST-Association/PAINT"
UTIS_X = "ApX"
UTIS_Y = "ApY"
UTIS_ELEVATION = "ApZ"

# Convert deflectometry
FACET_KEY = "facet"
SURFACE_NORMAL_KEY = "surface_normals"
SURFACE_POINT_KEY = "surface_points"
DEFLECTOMETRY_SUFFIX = "-deflectometry.h5"
FACET_PROPERTIES_SUFFIX = "-facet_properties.json"
DEFLECTOMETRY_CREATED_AT = "deflectometry_created_at"
KINEMATIC_PROPERTIES_SUFFIX = "-kinematic_properties.json"

# Combine properties
EAST_KEY = "East"
NORTH_KEY = "North"
ALTITUDE_KEY = "Altitude"
FIELD_ID = "FieldId"
HELIOSTAT_SIZE = "Heliostat Size"
KINEMATIC_KEY = "kinematic"
HEIGHT_ABOVE_GROUND = "HeightAboveGround"

# DWD KEYS
DWD_STATION_ID = "StationID"
DWD_STATION_NAME = "StationName"
DWD_START = "start"
DWD_END = "end"
DWD_STAC_NAME = "dwd-weather-item-stac"
DWD_STAC_URL = f"{URL_BASE}/{SAVE_WEATHER}/{DWD_STAC_NAME}"

# Juelich weather keys
JUELICH_START = "start"
JUELICH_END = "end"
JUELICH_FILE_NAME = "%s-juelich_weather"
JUELICH_STAC_NAME = "%s-juelich_weather-item-stac"
JUELICH_STAC_URL = f"{URL_BASE}/{SAVE_WEATHER}/{JUELICH_STAC_NAME}"
JUELICH_WEATHER_LAT = 50.916518
JUELICH_WEATHER_LON = 6.387409
JUELICH_WEATHER_ALTITUDE = 89
DATE_TIME_INDEX = "DateTimeIndex"


# Tower measurement keys
STJ_UPPER = "solar_tower_juelich_upper"
STJ_LOWER = "solar_tower_juelich_lower"
MFT = "multi_focus_tower"
CENTER = "center"
RECEIVER = "receiver"
UPPER_RIGHT = "upper_right"
UPPER_MIDDLE = "upper_middle"
UPPER_LEFT = "upper_left"
LOWER_RIGHT = "lower_right"
LOWER_MIDDLE = "lower_middle"
LOWER_LEFT = "lower_left"
RECEIVER_OUTER_UPPER_RIGHT = "receiver_outer_upper_right"
RECEIVER_OUTER_LOWER_RIGHT = "receiver_outer_lower_right"
RECEIVER_OUTER_LOWER_LEFT = "receiver_outer_lower_left"
RECEIVER_OUTER_UPPER_LEFT = "receiver_outer_upper_left"
RECEIVER_INNER_UPPER_RIGHT = "receiver_inner_upper_right"
RECEIVER_INNER_LOWER_RIGHT = "receiver_inner_lower_right"
RECEIVER_INNER_LOWER_LEFT = "receiver_inner_lower_left"
RECEIVER_INNER_UPPER_LEFT = "receiver_inner_upper_left"
TOWER_START_DATETIME = "2013-02-25"
TOWER_END_DATETIME = "2020-10-07"
TOWER_KEY = "measurements"
TOWER_FILE_NAME = f"{POWER_PLANT_GPPD_ID}-tower-measurements"
TOWER_STAC_NAME = f"{POWER_PLANT_GPPD_ID}-tower-measurements-item-stac"
TOWER_STAC_URL = f"{URL_BASE}/{TOWER_STAC_NAME}.json"
TOWER_NORMAL_VECTOR = (0, 1, 0)
TOWER_NORMAL_VECTOR_KEY = "normal_vector"
TOWER_COORDINATES_KEY = "coordinates"
TOWER_TYPE_KEY = "type"
PLANAR_KEY = "planar"
CONVEX_CYLINDER_KEY = "convex_cylinder"

CALIBRATION_TARGET_TO_NAME = {
    1: STJ_LOWER,
    3: MFT,
    4: STJ_UPPER,
    5: STJ_UPPER,
    6: STJ_UPPER,
    7: STJ_LOWER,
}

# Cropper mappings
DESTINATION_SIZE = (3072, 1728)
INITIAL_HEIGHT = 250
HEIGHT_OFFSET = 1250
INITIAL_WIDTH = 450
WIDTH_OFFSET = 2222
MARKERS_FOLDER = "markers"

# Renovation mappings
RENOVATION_ERROR = "renovation_error"
RENOVATION_PROPERTIES_KEY = "renovation"
NO_RENOVATION = "No renovation performed"
RENOVATION_ID = "Retrofit_mechanische_Umrüstung"

# Properties mappings
HELIOSTAT_POSITION_KEY = "heliostat_position"
HELIOSTAT_PROPERTIES_KEY = "heliostat_properties"
HELIOSTAT_WIDTH_KEY = "width"
HELIOSTAT_HEIGHT_KEY = "height"
HELIOSTAT_WIDTH = 3.2200000286102295
HELIOSTAT_HEIGHT = 2.559999942779541

# Facet properties
FACET_1_TRANSLATION = [-0.8075, 0.6425, 0.0402]
FACET_1_ROTATION_E = [1, 1, 1]
FACET_1_ROTATION_N = [1, 1, 1]
FACET_2_TRANSLATION = [0.8075, 0.6425, 0.0402]
FACET_2_ROTATION_E = [1, 1, -1]
FACET_2_ROTATION_N = [-1, 1, 1]
FACET_3_TRANSLATION = [-0.8075, -0.6425, 0.0402]
FACET_3_ROTATION_E = [1, 1, 1]
FACET_3_ROTATION_N = [-1, 1, -1]
FACET_4_TRANSLATION = [0.8075, -0.6425, 0.0402]
FACET_4_ROTATION_E = [1, 1, -1]
FACET_4_ROTATION_N = [1, 1, -1]
FOUR_FACETS = 4
SPAN_N = "spansN"
SPAN_E = "spansE"
FACETS_LIST = "facets"
NUM_FACETS = "number_of_facets"
TRANSLATION_VECTOR = "translation_vector"
CANTING_E = "canting_e"
CANTING_N = "canting_n"
CANTING_TYPE = "canting_type"
CANTING_KEY = "canting"
MAP_CANTING_TO_READABLE = {"Rec": "receiver canting", "FE": "research level canting"}

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
WGS84_B = 6356752.314245  # Minor axis in meters
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared

# Extra Kinematic Properties
FIRST_JOINT_TRANSLATION_E_KEY = "joint_translation_e_1"
FIRST_JOINT_TRANSLATION_N_KEY = "joint_translation_n_1"
FIRST_JOINT_TRANSLATION_U_KEY = "joint_translation_u_1"
SECOND_JOINT_TRANSLATION_E_KEY = "joint_translation_e_2"
SECOND_JOINT_TRANSLATION_N_KEY = "joint_translation_n_2"
SECOND_JOINT_TRANSLATION_U_KEY = "joint_translation_u_2"
CONCENTRATOR_TRANSLATION_E_KEY = "concentrator_translation_e"
CONCENTRATOR_TRANSLATION_N_KEY = "concentrator_translation_n"
CONCENTRATOR_TRANSLATION_U_KEY = "concentrator_translation_u"
FIRST_JOINT_TRANSLATION_E = 0.0
FIRST_JOINT_TRANSLATION_N = 0.0
FIRST_JOINT_TRANSLATION_U = 0.0
SECOND_JOINT_TRANSLATION_E = 0.0
SECOND_JOINT_TRANSLATION_N = 0.0
SECOND_JOINT_TRANSLATION_U = 0.3149999976158142
CONCENTRATOR_TRANSLATION_E = 0.0
CONCENTRATOR_TRANSLATION_N = -0.17755000293254852
CONCENTRATOR_TRANSLATION_U = -0.40450000762939453
INITIAL_ORIENTATION_KEY = "initial_orientation"
INITIAL_ORIENTATION_VALUE = [0.0, 0, 0, 1.0]

ACTUATOR_KEY = "actuators"
# Name mapping conversion for Heliostat properties
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

# Keys for dataset splits
AZIMUTH_SPLIT = "azimuth"
SOLSTICE_SPLIT = "solstice"
SPLIT_KEY = "Split"
DISTANCE_WINTER = "distance_winter"
DISTANCE_SUMMER = "distance_summer"


# Keys for Dataset file identifiers.
CALIBRATION_RAW_IMAGE_IDENTIFIER = "_raw.png"
CALIBRATION_CROPPED_IMAGE_IDENTIFIER = "_cropped.png"
CALIBRATION_FLUX_IMAGE_IDENTIFIER = "_flux.png"
CALIBRATION_FLUX_CENTERED_IMAGE_IDENTIFIER = "_flux_centered.png"
CALIBRATION_PROPERTIES_IDENTIFIER = "-calibration-properties.json"
