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
LICENSE_LINK = (
    {
        "rel": "license",
        "href": "https://cdla.dev/permissive-2-0/",
        "type": "text/html",
        "title": "Community Data License Agreement – Permissive – Version 2.0",
    },
)
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

COLLECTION = "Collection"
FEATURE = "Feature"

TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"

MIME_PNG = "image/png"
MIME_GEOJSON = "application/geo+json"

CATALOGUE_URL = (
    "https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1"
)

CALIBRATION_COLLECTION_ID = f"{POWER_PLANT_GPPD_ID}-calibration"
CALIBRATION_COLLECTION_FILE = f"{POWER_PLANT_GPPD_ID}-calibration-stac.json"
CALIBRATION_COLLECTION_URL = f"https://zenodo.org/record/loscalibrationes/files/{CALIBRATION_COLLECTION_FILE}?download=1"
