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
CSP_SCHEMA = f"https://stac-extensions.github.io/csp/v{STAC_VERSION}/schema.json"
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

CATALOG_ID = f"{POWER_PLANT_GPPD_ID}-catalog"
CATALOG_FILE = f"{POWER_PLANT_GPPD_ID}-catalog-stac.json"

CATALOGUE_URL = (
    "https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1"
)

CALIBRATION_COLLECTION_ID = f"{POWER_PLANT_GPPD_ID}-calibration"
CALIBRATION_COLLECTION_FILE = f"{POWER_PLANT_GPPD_ID}-calibration-stac.json"
CALIBRATION_COLLECTION_URL = f"https://zenodo.org/record/loscalibrationes/files/{CALIBRATION_COLLECTION_FILE}?download=1"
CALIBRATION_ITEM = "%d-calibration-item-stac.json"
CALIBRATION_ITEM_URL = (
    f"https://zenodo.org/record/loscalibrationes/files/{CALIBRATION_ITEM}"
)

HELIOSTAT_PROPERTY_COLLECTION_ID = f"{POWER_PLANT_GPPD_ID}-heliostat_property"
HELIOSTAT_PROPERTY_COLLECTION_FILE = (
    f"{POWER_PLANT_GPPD_ID}-heliostat_property-stac.json"
)
HELIOSTAT_PROPERTY_COLLECTION_URL = f"https://zenodo.org/record/losheliostat_propertiones/files/{HELIOSTAT_PROPERTY_COLLECTION_FILE}?download=1"
HELIOSTAT_PROPERTY_ITEM = "%d-heliostat_property-item-stac.json"
HELIOSTAT_PROPERTY_ITEM_URL = (
    f"https://zenodo.org/record/loscalibrationes/files/{HELIOSTAT_PROPERTY_ITEM}"
)


# Convert deflectometry
FACET_KEY = "facet"
SURFACE_NORMAL_KEY = "surface_normals"
SURFACE_POINT_KEY = "surface_points"

# Constants for WGS84
WGS84_A = 6378137.0  # Major axis in meters
WGS84_B = 6356752.314245  # Minor axis in meters
WGS84_E2 = (WGS84_A**2 - WGS84_B**2) / WGS84_A**2  # Eccentricity squared
