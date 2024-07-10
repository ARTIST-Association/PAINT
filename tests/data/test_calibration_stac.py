import deepdiff
import pandas as pd
import pytest

import paint.data.calibration_stac
import paint.util.paint_mappings as mappings


@pytest.fixture
def heliostat_data():
    """
    Make a fixture with two heliostats.

    Returns
    -------
    pd.DataFrame
        The test fixture.
    """
    return pd.DataFrame(
        {
            mappings.ID_INDEX: [115399, 116262],
            mappings.HELIOSTAT_ID: [20352, 20256],
            mappings.CALIBRATION_TARGET: [4, 0],
            mappings.CREATED_AT: [
                pd.Timestamp("2022-06-01 11:08:45", tz="UTC"),
                pd.Timestamp("2022-10-27 03:05:55", tz="UTC"),
            ],
            mappings.UPDATED_AT: [
                pd.Timestamp("2022-06-27 13:08:27", tz="UTC"),
                pd.Timestamp("2022-10-27 03:05:55", tz="UTC"),
            ],
            mappings.AZIMUTH: [135.0, -26.56505118],
            mappings.ELEVATION: [85.95530876, -53.3007748],
            mappings.SYSTEM: ["HeliOS.FDM", "HeliOS.FDM"],
            mappings.AXIS1_MOTOR: [44350, 44072],
            mappings.AXIS2_MOTOR: [59345, 50956],
        }
    ).set_index(mappings.ID_INDEX)


def test_make_collection(heliostat_data: pd.DataFrame) -> None:
    """
    Test the creation of the calibration STAC collection.

    Parameters
    ----------
    heliostat_data: pd.DataFrame
        The test fixture.
    """
    collection = paint.data.calibration_stac.make_collection(heliostat_data)
    print(collection)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json",
            "https://stac-extensions.github.io/csp/v1.0.0/schema.json",
        ],
        "id": "WRI1030197-calibration",
        "type": "Collection",
        "title": "Calibration images of CSP WRI1030197",
        "description": "All calibration images of the concentrating solar power plant WRI1030197 in Jülich, Germany",
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
            "spatial": {
                "bbox": [
                    [
                        6.387514846666862,
                        50.913296351383806,
                        6.387514846666862,
                        50.913296351383806,
                    ]
                ]
            },
            "temporal": {"interval": ["2022-06-01Z11:08:45Z", "2022-10-27Z03:05:55Z"]},
        },
        "summaries": {
            "csp:gppd_id": {"type": "string", "const": "WRI1030197", "count": 2},
            "datetime": {
                "minimum": "2022-06-01Z11:08:45Z",
                "maximum": "2022-10-27Z03:05:55Z",
            },
            "view:sun_azimuth": {"minimum": -26.56505118, "maximum": 135.0},
            "view:sun_elevation": {"minimum": -53.3007748, "maximum": 85.95530876},
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
                "href": "https://zenodo.org/record/loscalibrationes/files/WRI1030197-calibration-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": "https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the entire catalogue for WRI1030197",
            },
            {
                "rel": "collection",
                "href": "https://zenodo.org/record/loscalibrationes/files/WRI1030197-calibration-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "item",
                "href": "https://zenodo.org/record/loscalibrationes/files/115399-calibration-item-stac.json",
                "type": "application/geo+json",
                "title": "STAC item of image 115399",
            },
            {
                "rel": "item",
                "href": "https://zenodo.org/record/loscalibrationes/files/116262-calibration-item-stac.json",
                "type": "application/geo+json",
                "title": "STAC item of image 116262",
            },
        ],
        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": "image/png",
                "title": "Calibration images of heliostats",
            }
        },
    }

    assert not deepdiff.DeepDiff(collection, expected, ignore_numeric_type_changes=True)


def test_make_item(heliostat_data: pd.DataFrame) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    heliostat_data: pd.DataFrame
        The test fixture.
    """
    image = 116262
    single_heliostat = heliostat_data.loc[image]

    item = paint.data.calibration_stac.make_item(image, single_heliostat)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "view",
            "https://raw.githubusercontent.com/ARTIST-Association/csp/main/json-schema/schema.json",
        ],
        "id": "116262",
        "type": "Feature",
        "title": "Calibration of heliostat 116262",
        "description": "Images of focused sunlight on the calibration target of heliostat 116262",
        "collection": "WRI1030197-calibration",
        "geometry": {
            "type": "Point",
            "coordinates": [6.387514846666862, 50.913296351383806],
        },
        "properties": {
            "datetime": "2022-10-27Z03:05:55Z",
            "created": "2022-10-27Z03:05:55Z",
            "updated": "2022-10-27Z03:05:55Z",
            "instruments": ["HeliOS.FDM"],
        },
        "view:sun_azimuth": -26.56505118,
        "view:sun_elevation": -53.3007748,
        "csp:gppd_id": "WRI1030197",
        "csp:heliostats": [
            {"csp:heliostat_id": 20256, "csp:heliostat_motors": [44072, 50956]}
        ],
        "links": [
            {
                "rel": "self",
                "href": "./116262-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": "./https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the entire catalogue for WRI1030197",
            },
            {
                "rel": "parent",
                "href": "https://zenodo.org/record/loscalibrationes/files/WRI1030197-calibration-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://zenodo.org/record/loscalibrationes/files/WRI1030197-calibration-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "target": {
                "href": "../116262.png",
                "roles": ["data"],
                "type": "image/png",
                "title": "Calibration image of heliostat with id 116262",
            }
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)


def test_make_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        paint.data.calibration_stac.make_collection(pd.DataFrame())
