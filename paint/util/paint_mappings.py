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
ITEM_ASSETS_SCHEMA = (
    f"https://stac-extensions.github.io/item-assets/v{STAC_VERSION}/schema.json"
)
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

CATALOG = "Catalog"
COLLECTION = "Collection"
FEATURE = "Feature"

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"

MIME_PNG = "image/png"
MIME_GEOJSON = "application/geo+json"
MIME_HDF5 = "application/x-hdf5"
MIME_PDF = "application/pdf"

CATALOG_ID = f"{POWER_PLANT_GPPD_ID}-catalog"
CATALOG_FILE = f"{POWER_PLANT_GPPD_ID}-catalog-stac.json"

HELIOSTAT_CATALOG_ID = "%s-heliostat-catalog"
HELIOSTAT_CATALOG_FILE = "%s-heliostat-catalog-stac.json"
HELIOSTAT_CATALOG_URL = f"INSERT/SOMETHING/HERE/{HELIOSTAT_CATALOG_FILE}?download=1"

CATALOGUE_URL = "Insert/URL/Here"

CALIBRATION_COLLECTION_ID = "%s-calibration-collection"
CALIBRATION_COLLECTION_FILE = "%s-calibration-collection-stac.json"
CALIBRATION_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{CALIBRATION_COLLECTION_FILE}?download=1"
)
CALIBRATION_ITEM = "%s-%d-calibration-item-stac.json"
CALIBRATION_ITEM_URL = f"INSERT/SOMETHING/HERE/{CALIBRATION_ITEM}"

DEFLECTOMETRY_COLLECTION_ID = "%s-deflectometry-collection"
DEFLECTOMETRY_COLLECTION_FILE = "%s-deflectometry-collection-stac.json"
DEFLECTOMETRY_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_COLLECTION_FILE}?download=1"
)
DEFLECTOMETRY_ITEM = "%s-%s-deflectometry-item-stac.json"
DEFLECTOMETRY_ITEM_URL = f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_ITEM}?download=1"

DEFLECTOMETRY_PDF_NAME = "%s-%s-deflectometry-result.pdf"
DEFLECTOMETRY_INSTRUMENTS = "QDec_2014-101"

HELIOSTAT_PROPERTIES_COLLECTION_ID = "%s-heliostat_properties-collection"
HELIOSTAT_PROPERTIES_COLLECTION_FILE = "%s-heliostat_properties-collection-stac.json"
HELIOSTAT_PROPERTIES_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{HELIOSTAT_PROPERTIES_COLLECTION_FILE}?download=1"
)
FACET_PROPERTIES_ITEM = "%s-facet_properties-item-stac.json"
FACET_PROPERTIES_ITEM_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{FACET_PROPERTIES_ITEM}?download=1"
)
KINEMATIC_PROPERTIES_ITEM = "%s-kinematic_properties-item-stac.json"
KINEMATIC_PROPERTIES_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{KINEMATIC_PROPERTIES_ITEM}?download=1"
)

WEATHER_COLLECTION_ID = "weather-collection"
WEATHER_COLLECTION_FILE = "weather-collection-stac.json"
WEATHER_COLLECTION_URL = f"INSERT/SOMETHING/HERE/{WEATHER_COLLECTION_FILE}?download=1"


URL_KEY = "url"
TITLE_KEY = "title"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
DEFLECTOMETRY_RAW_KEY = "raw_measurement"
DEFLECTOMETRY_FILLED_KEY = "filled_measurement"
DEFLECTOMETRY_RESULTS_KEY = "results_summary"
CALIBRATION_TARGET_KEY = "target"
CALIBRATION_MOTOR_POS_KEY = "motor_positions"
FACET_PROPERTIES_KEY = "facet_properties"
KINEMATIC_PROPERTIES_KEY = "kinematic_properties"
MOTOR_POS_NAME = "%s-%d-motor-position"
WEATHER_DATA_KEY = "weather_data"

SAVE_DEFLECTOMETRY = "Deflectometry"
SAVE_PROPERTIES = "Properties"
SAVE_CALIBRATION = "Calibration"
BBOX_LAT_LON_DEVIATION = 2e-05
BBOX_ALTITUDE_DEVIATION = 2

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
DWD_STAT_URL = f"INSERT/SOMETHING/HERE/{DWD_STAC_NAME}?download=1"

# JUELICH WEATHER KEYS
JUELICH_START = "start"
JUELICH_END = "end"
JUELICH_STAC_NAME = "juelich-weather-item-stac"
JUELICH_STAT_URL = f"INSERT/SOMETHING/HERE/{JUELICH_STAC_NAME}?download=1"

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
WGS84_B = 6356752.314245  # Minor axis in meters
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared
