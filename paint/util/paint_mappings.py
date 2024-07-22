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

CATALOGUE_URL = "Insert/URL/Here"

CALIBRATION_COLLECTION_ID = "%s-calibration"
CALIBRATION_COLLECTION_FILE = "%s-calibration-stac.json"
CALIBRATION_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{CALIBRATION_COLLECTION_FILE}?download=1"
)
CALIBRATION_ITEM = "%d-%s-calibration-item-stac.json"
CALIBRATION_ITEM_URL = f"INSERT/SOMETHING/HERE/{CALIBRATION_ITEM}"

DEFLECTOMETRY_COLLECTION_ID = "%s-deflectometry"
DEFLECTOMETRY_COLLECTION_FILE = "%s-deflectometry-stac.json"
DEFLECTOMETRY_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_COLLECTION_FILE}?download=1"
)
DEFLECTOMETRY_RAW_ITEM = "%s-%s-deflectometry-item-stac.json"
DEFLECTOMETRY_FILLED_ITEM = "%s-filled-%s-deflectometry-item-stac.json"
DEFLECTOMETRY_RAW_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_RAW_ITEM}?download=1"
)
DEFLECTOMETRY_FILLED_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_FILLED_ITEM}?download=1"
)
DEFLECTOMETRY_RESULT_ITEM = "%s-%s-deflectometry-result-item-stac.json"
DEFLECTOMETRY_RESULT_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{DEFLECTOMETRY_RESULT_ITEM}?download=1"
)
DEFLECTOMETRY_PDF_NAME = "%s-%s-deflectometry-result.pdf"
DEFLECTOMETRY_INSTRUMENTS = "QDec_2014-101"

HELIOSTAT_PROPERTIES_COLLECTION_ID = "%s-heliostat_properties"
HELIOSTAT_PROPERTIES_COLLECTION_FILE = "%s-heliostat_properties-stac.json"
HELIOSTAT_PROPERTIES_COLLECTION_URL = (
    f"INSERT/SOMETHING/HERE/{HELIOSTAT_PROPERTIES_COLLECTION_FILE}?download=1"
)
FACET_PROPERTIES_ITEM = "%s-facet_properties-item-stac.json"
FACET_PROPERTIES_ITEM_ITEM_URL = (
    f"INSERT/SOMETHING/HERE/{FACET_PROPERTIES_ITEM}?download=1"
)

URL_KEY = "url"
TITLE_KEY = "title"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"

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

# Combine properties
EAST_KEY = "East"
NORTH_KEY = "North"
ALTITUDE_KEY = "Altitude"
FIELD_ID = "FieldId"
HELIOSTAT_SIZE = "Heliostat Size"
KINEMATIC_KEY = "kinematic"
HEIGHT_ABOVE_GROUND = "HeightAboveGround"

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
WGS84_B = 6356752.314245  # Minor axis in meters
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared
