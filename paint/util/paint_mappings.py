# CSV columns
INTERNAL_NAME_INDEX = "InternalName"
ID_INDEX = "id"
HELIOSTAT_ID = "HeliostatId"
X_Y_Z_POSITIONS = ["x", "y", "z"]
DEFLECTOMETRY_AVAILABLE = "DeflectometryAvailable"
CREATED_AT = "CreatedAt"
UPDATED_AT = "UpdatedAt"
YEAR = "Year"
MONTH = "Month"
HOUR = "Hour"
AZIMUTH = "Azimuth"
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

# dataset
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
POWER_PLANT_LAT = 50.913296351383806
POWER_PLANT_LON = 6.387514846666862
POWER_PLANT_ALT = 87

# Target coordinates
STJ_UPPER_COORDINATES = [
    [50.91338897581139, 6.387856033619183, 126.476],
    [50.913389074925156, 6.38785596334749, 133.684],
    [50.91338922182834, 6.3877332676815515, 133.719],
    [50.913389266158724, 6.3877334528986855, 126.506],
    [50.91338897581139, 6.387856033619183, 126.476],
]
STJ_UPPER_BOUNDING_BOX = [
    50.91338897581139,
    6.3877332676815515,
    126.476,
    50.913389266158724,
    6.387856033619183,
    133.719,
]
STJ_LOWER_COORDINATES = [
    [50.913388948892035, 6.387856019176258, 119.268],
    [50.91338897581139, 6.387856033619183, 126.476],
    [50.913389266158724, 6.3877334528986855, 126.506],
    [50.91338944678619, 6.3877331984554475, 119.279],
    [50.913388948892035, 6.387856019176258, 119.268],
]
STJ_LOWER_BOUNDING_BOX = [
    50.913388948892035,
    6.3877331984554475,
    119.268,
    50.91338944678619,
    6.387856033619183,
    126.506,
]
MFT_COORDINATES = [
    [50.91339345190814, 6.387582821752781, 135.789],
    [50.91339339750286, 6.387582963492142, 142.175],
    [50.91339372487825, 6.387506012264232, 142.172],
    [50.913393662428156, 6.387505869554209, 135.783],
    [50.91339345190814, 6.387582821752781, 135.789],
]
MFT_BOUNDING_BOX = [
    50.91339339750286,
    6.387505869554209,
    135.783,
    50.91339372487825,
    6.387582963492142,
    142.175,
]
RECEIVER_COORDINATES = [
    [50.913403653906435, 6.387823906642166, 139.86],
    [50.91342356387283, 6.387824185899528, 144.592],
    [50.91342387604005, 6.387765392341336, 144.593],
    [50.91340375876268, 6.387765282015661, 139.862],
    [50.913403653906435, 6.387823906642166, 139.86],
]
RECEIVER_BOUNDING_BOX = [
    50.913403653906435,
    6.387765282015661,
    139.86,
    50.91342387604005,
    6.387824185899528,
    144.593,
]

# Target center coordinates
STJ_UPPER_CENTER = (50.91338911716799, 6.387794544159513, 130.09766666666667)
STJ_LOWER_CENTER = (50.91338911716799, 6.387794544159513, 122.8815)
MFT_CENTER = (50.91339355918569, 6.3875444167659845, 138.97975)
RECEIVER_CENTER = (50.91341371314919, 6.387794691724733, 142.22674999999998)


CATALOG = "Catalog"
COLLECTION = "Collection"
FEATURE = "Feature"

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"

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

# Calibration Properties
MOTOR_POS_KEY = "motor_position"
TARGET_NAME_KEY = "target_name"
FOCAL_SPOT_KEY = "focal_spot"
UTIS_KEY = "UTIS"
UTIS_URL = "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization"
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
FACETS_LIST = "facets"
NUM_FACETS = "number_of_facets"
TRANSLATION_VECTOR = "translation_vector"
CANTING_E = "canting_e"
CANTING_N = "canting_n"
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
MFT = "multi_functions_tower"
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
TOWER_FILE_NAME = "juelich-tower-measurements"
TOWER_STAC_NAME = "juelich-tower-measurements-item-stac"
TOWER_STAC_URL = f"{URL_BASE}/{TOWER_STAC_NAME}"

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

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
WGS84_B = 6356752.314245  # Minor axis in meters
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared
