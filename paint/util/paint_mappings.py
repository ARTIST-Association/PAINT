TIME_FORMAT = "%Y-%m-%dZ%H:%M:%SZ"
INTERNAL_NAME_INDEX = "InternalName"
ID_INDEX = "id"
HELIOSTAT_ID = "HeliostatID"
X_Y_Z_POSITIONS = ["x", "y", "z"]
DEFLECTOMETRY_AVAILABLE = "DeflectometryAvailable"
CREATED_AT = "CreatedAt"
UPDATED_AT = "UpdatedAt"
YEAR = "Year"
MONTH = "Month"
HOUR = "Hour"
AZIMUTH = "Azimuth"
ELEVATION = "Elevation"
MEASURED_SURFACE = "MeasuredSurface"
SUN_POSITION_EAST = "SunPosE"
SUN_POSITION_NORTH = "SunPosN"
SUN_POSITION_UP = "SunPosU"
TOTAL_INDEX = "Total"
TRAIN_INDEX = "train"
TEST_INDEX = "test"
VALIDATION_INDEX = "validation"
DATA_SET_AZIMUTH = "DataSet_Azimuth"
DECEMBER_DISTANCE = "Dec_Distance"
JUNE_DISTANCE = "Jun_Distance"

STAC_VERSION = "1.0.0"
ITEM_ASSETS_SCHEMA = (
    f"https://stac-extensions.github.io/item-assets/v{STAC_VERSION}/schema.json"
)
CSP_SCHEMA = f"https://stac-extensions.github.io/csp/v{STAC_VERSION}/schema.json"
CDLA = "CDLA-2.0"
DLR = {
    "name": "German Aerospace Center (DLR)",
    "description": "National center for aerospace, energy and transportation research of Germany",
    "roles": ["licensor", "producer", "processor"],
    "url": "https://github.com/ARTIST-Association/PAINT/",
}
KIT = {
    "name": "Karlsruhe Institute of Technology (KIT)",
    "description": "Public research center and university in Karlsruhe, Germany",
    "roles": ["producer", "processor", "host"],
    "url": "https://github.com/ARTIST-Association/PAINT/",
}

POWER_PLANT_GPPD_ID = "WRI1030197"
COLLECTION = "Collection"
FEATURE = "Feature"

CALIBRATION_COLLECTION_ID = f"{POWER_PLANT_GPPD_ID}-calibration-images"
CALIBRATION_COLLECTION_FILE = "calibration-collection-stac.json"
CALIBRATION_COLLECTION_URL = (
    f"https://zenodo.org/record/xxx/files/{CALIBRATION_COLLECTION_FILE}?download=1"
)
