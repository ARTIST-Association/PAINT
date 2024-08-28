from typing import Tuple

import deepdiff
import pandas as pd
import pytest

import paint.util.paint_mappings as mappings
from paint.data.calibration_stac import (
    make_calibration_collection,
    make_calibration_item,
)


@pytest.fixture
def calibration_item_data() -> Tuple[int, pd.Series]:
    """
    Make a fixture with data for generating a calibration item.

    Returns
    -------
    int
        The image ID.
    pd.Series
        The data for the calibration STAC item.
    """
    data = {
        "FieldId": 1,
        "HeliostatId": "BC52",
        "CameraId": 0,
        "CalibrationTargetId": 7,
        "System": "HeliOS.FDM",
        "Version": 1.0,
        "Axis1MotorPosition": 44350,
        "Axis2MotorPosition": 59345,
        "ImageOffsetX": 343.2206783955819,
        "ImageOffsetY": 336.57737110870715,
        "TargetOffsetE": 0.8986945895769931,
        "TargetOffsetN": -3.2362078192934702,
        "TargetOffsetU": 123.49814527419454,
        "TrackingOffsetE": 0.0,
        "TrackingOffsetU": 0.0,
        "SunPosE": -0.3783143931471522,
        "SunPosN": -0.4191916363901756,
        "SunPosU": 0.825322114036834,
        "LastScore": 8.717597473226798,
        "GeometryData": '{\r\n  "alpha" : 1.586571429484214,\r\n  "beta" : 1.574961871386958,\r\n  "gamma" : 0.0,\r\n  "delta" : 0.0,\r\n  "axis1k" : 0.017594028615554223,\r\n  "axis2k" : 0.9056999844505894,\r\n  "axis3k" : 0.0,\r\n  "axis1b" : 0.07894519658593206,\r\n  "axis2b" : 0.07716455571024607,\r\n  "axis3b" : 0.0\r\n}',
        "IsDeleted": 1,
        "CreatedAt": pd.Timestamp("2022-06-01 11:08:45+0000", tz="UTC"),
        "UpdatedAt": pd.Timestamp("2022-10-27 07:05:55+0000", tz="UTC"),
        "OverExpRatio": -1,
        "Az": -1,
        "iO": 1,
        "ApX": 0.0,
        "ApY": 0.0,
        "ApZ": 0.0,
        "OvrExp": 5.34028589409332,
        "Azimuth": -42.06579562155874,
        "Sun_elevation": 55.621162346471515,
    }
    return 115399, pd.Series(data)


@pytest.fixture
def calibration_collection_data():
    """
    Make a fixture with data for generating the calibration collection.

    Returns
    -------
    pd.DataFrame
        The data for the calibration collection as a test fixture.
    """
    data = {
        mappings.HELIOSTAT_ID: ["BC52", "BC52", "BC52", "BC52"],
        mappings.TITLE_KEY: [
            "calibration image 115399 and associated motor positions for heliostat BC52",
            "calibration image 116262 and associated motor positions for heliostat BC52",
            "calibration image 116310 and associated motor positions for heliostat BC52",
            "calibration image 116384 and associated motor positions for heliostat BC52",
        ],
        mappings.URL_KEY: [
            "INSERT/SOMETHING/HERE/BC52-115399-calibration-item-stac.json",
            "INSERT/SOMETHING/HERE/BC52-116262-calibration-item-stac.json",
            "INSERT/SOMETHING/HERE/BC52-116310-calibration-item-stac.json",
            "INSERT/SOMETHING/HERE/BC52-116384-calibration-item-stac.json",
        ],
        mappings.CREATED_AT: [
            pd.Timestamp("2022-06-01 11:08:45+00:00", tz="UTC"),
            pd.Timestamp("2022-06-02 10:10:19+00:00", tz="UTC"),
            pd.Timestamp("2022-06-02 10:15:40+00:00", tz="UTC"),
            pd.Timestamp("2022-06-02 10:26:01+00:00", tz="UTC"),
        ],
        mappings.AZIMUTH: [
            -42.06579562155874,
            -17.92779175130011,
            -20.35899048157409,
            -24.95280670914511,
        ],
        mappings.SUN_ELEVATION: [
            55.621162346471515,
            60.38321187895165,
            60.10724673519602,
            59.47986694914367,
        ],
        mappings.SYSTEM: ["HeliOS.FDM"] * 4,
        mappings.LATITUDE_KEY: [50.4, 60.7, 70.1, 68.3],
        mappings.LONGITUDE_KEY: [5.0, 6.3, 7.2, 8.1],
        mappings.ELEVATION: [100, 200, 300, 400],
    }

    return pd.DataFrame(data)


def test_make_calibration_collection(calibration_collection_data: pd.DataFrame) -> None:
    """
    Test the creation of the calibration STAC collection.

    Parameters
    ----------
    calibration_collection_data: pd.DataFrame
        The test fixture.
    """
    for heliostat, data in calibration_collection_data.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_calibration_collection(heliostat_id=heliostat, data=data)

        expected = {
            "stac_version": "1.0.0",
            "stac_extensions": [
                "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json"
            ],
            "id": "BC52-calibration-collection",
            "type": "Collection",
            "title": "Calibration images from heliostat BC52",
            "description": "All calibration images from the heliostat BC52",
            "keywords": ["csp", "calibration", "tracking"],
            "license": "CDLA-2.0",
            "providers": [
                {
                    "name": "German Aerospace Center (DLR)",
                    "description": "National center for aerospace, energy and transportation research of Germany",
                    "roles": ["licensor", "producer", "processor"],
                    "url": "https://github.com/ARTIST-Association/PAINT/",
                },
                {
                    "name": "Karlsruhe Institute of Technology (KIT)",
                    "description": "Public research center and university in Karlsruhe, Germany",
                    "roles": ["producer", "processor", "host"],
                    "url": "https://github.com/ARTIST-Association/PAINT/",
                },
            ],
            "extent": {
                "spatial": {"bbox": [50.4, 5.0, 100, 70.1, 8.1, 400]},
                "temporal": {
                    "interval": ["2022-06-01Z11:08:45Z", "2022-06-02Z10:26:01Z"]
                },
            },
            "summaries": {
                "datetime": {
                    "minimum": "2022-06-01Z11:08:45Z",
                    "maximum": "2022-06-02Z10:26:01Z",
                },
                "view:sun_azimuth": {
                    "minimum": -42.06579562155874,
                    "maximum": -17.92779175130011,
                },
                "view:sun_elevation": {
                    "minimum": 55.621162346471515,
                    "maximum": 60.38321187895165,
                },
                "instruments": ["HeliOS.FDM"],
            },
            "links": [
                {
                    "rel": "license",
                    "href": "https://cdla.dev/permissive-2-0/",
                    "type": "text/html",
                    "title": "Community Data License Agreement – Permissive – Version 2.0",
                },
                {
                    "rel": "self",
                    "href": "https://paint-database.org/WRI1030197/BC52/Calibration/BC52-calibration-collection-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "root",
                    "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to the entire catalogue for WRI1030197",
                },
                {
                    "rel": "collection",
                    "href": "https://paint-database.org/WRI1030197/BC52/Calibration/BC52-calibration-collection-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/BC52-115399-calibration-item-stac.json",
                    "type": "application/geo+json",
                    "title": "STAC item of calibration image 115399 and associated motor positions for heliostat BC52",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/BC52-116262-calibration-item-stac.json",
                    "type": "application/geo+json",
                    "title": "STAC item of calibration image 116262 and associated motor positions for heliostat BC52",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/BC52-116310-calibration-item-stac.json",
                    "type": "application/geo+json",
                    "title": "STAC item of calibration image 116310 and associated motor positions for heliostat BC52",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/BC52-116384-calibration-item-stac.json",
                    "type": "application/geo+json",
                    "title": "STAC item of calibration image 116384 and associated motor positions for heliostat BC52",
                },
            ],
        }

        assert not deepdiff.DeepDiff(
            collection, expected, ignore_numeric_type_changes=True
        )


def test_make_calibration_item(calibration_item_data: Tuple[str, pd.Series]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    calibration_item_data : Tuple[str, pd.Series]
        The test fixture.
    """
    image, data = calibration_item_data
    assert isinstance(image, int)
    item = make_calibration_item(image=image, heliostat_data=data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": ["view"],
        "id": "115399",
        "type": "Feature",
        "title": "Calibration data from heliostat BC52 for image 115399",
        "description": "Image of focused sunlight on the calibration target from heliostat BC52 for image 115399 with associated motor positions",
        "collection": "BC52-calibration-collection",
        "geometry": {
            "type": "Point",
            "coordinates": [50.91338911716799, 6.387794544159513, 122.8815],
        },
        "bbox": [
            50.91338911716799,
            6.387794544159513,
            122.8815,
            50.91338911716799,
            6.387794544159513,
            122.8815,
        ],
        "properties": {
            "datetime": "2022-06-01Z11:08:45Z",
            "created": "2022-06-01Z11:08:45Z",
            "updated": "2022-10-27Z07:05:55Z",
            "instruments": ["HeliOS.FDM"],
        },
        "view:sun_azimuth": -42.06579562155874,
        "view:sun_elevation": 55.621162346471515,
        "links": [
            {
                "rel": "self",
                "href": "./115399-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": "./https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the entire catalogue for WRI1030197",
            },
            {
                "rel": "parent",
                "href": "https://paint-database.org/WRI1030197/BC52/Calibration/BC52-calibration-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://paint-database.org/WRI1030197/BC52/Calibration/BC52-calibration-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "target": {
                "href": "./115399.png",
                "roles": ["data"],
                "type": "image/png",
                "title": "Calibration image with id 115399",
            },
            "motor_positions": {
                "href": "./BC52-115399-motor-position.json",
                "roles": ["metadata"],
                "type": "application/geo+json",
                "title": "Motor positions for the calibration image id 115399",
            },
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)


def test_make_calibration_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        make_calibration_collection("AB123", pd.DataFrame())
