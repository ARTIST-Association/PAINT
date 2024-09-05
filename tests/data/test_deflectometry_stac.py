from typing import Tuple

import deepdiff
import pandas as pd
import pytest

import paint.util.paint_mappings as mappings
from paint.data.deflectometry_stac import (
    make_deflectometry_collection,
    make_deflectometry_item,
)


@pytest.fixture
def deflectometry_item_data() -> Tuple[str, pd.Series]:
    """
    Make a fixture with data for generating a deflectometry item.

    Returns
    -------
    str
        The heliostat ID.
    pd.Series
        The data for the deflectometry STAC item.
    """
    data = {
        "East": 13.2,
        "North": 154.7,
        "Altitude": 88.66962,
        "HeightAboveGround": 1.66962,
        "CreatedAt": "2023-09-18Z11:39:25Z",
    }
    return "AY39", pd.Series(data)


@pytest.fixture
def deflectometry_collection_data():
    """
    Make a fixture with data for generating the deflectometry collection.

    Returns
    -------
    pd.DataFrame
        The data for the deflectometry collection as a test fixture.
    """
    import pandas as pd

    # Define the data
    data = {
        "HeliostatId": ["AY39", "AY39", "AY39"],
        "title": [
            "Deflectometry measurements for AY39 at 2023-09-18Z11:39:25Z",
            "Deflectometry measurements for AY39 at 2024-09-18Z11:39:25Z",
            "Deflectometry measurements for AY39 at 2022-06-26Z07:07:07Z",
        ],
        "url": [
            "INSERT/SOMETHING/HERE/AY39-2023-09-18Z11:39:25Z-deflectometry-item-stac.json?download=1",
            "INSERT/SOMETHING/HERE/AY39-2024-09-18Z11:39:25Z-deflectometry-item-stac.json?download=1",
            "INSERT/SOMETHING/HERE/AY39-2023-06-26Z07:07:07Z-deflectometry-item-stac.json?download=1",
        ],
        "CreatedAt": [
            "2023-09-18Z11:39:25Z",
            "2024-09-18Z11:39:25Z",
            "2022-06-26Z07:07:07Z",
        ],
        "latitude": [50.914686955478864, 51.914686955478864, 49.914686955478864],
        "longitude": [6.387702537483708, 5.387702537483708, 7.387702537483708],
        "Elevation": [88.66962, 89.66962, 123.66962],
    }

    return pd.DataFrame(data)


def test_make_deflectometry_collection(
    deflectometry_collection_data: pd.DataFrame,
) -> None:
    """
    Test the creation of the deflectometry STAC collection.

    Parameters
    ----------
    deflectometry_collection_data: pd.DataFrame
        The test fixture.
    """
    for heliostat, data in deflectometry_collection_data.groupby(mappings.HELIOSTAT_ID):
        assert isinstance(heliostat, str)
        collection = make_deflectometry_collection(heliostat_id=heliostat, data=data)

        expected = {
            "stac_version": "1.0.0",
            "stac_extensions": [],
            "id": "AY39-deflectometry-collection",
            "type": "Collection",
            "title": "Deflectometry data for heliostat AY39",
            "description": "All deflectometry data, including raw measurements, filled measurements and results summary for heliostat AY39",
            "keywords": ["csp", "deflectometry"],
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
                            49.914686955478864,
                            5.387702537483708,
                            88.66962,
                            51.914686955478864,
                            7.387702537483708,
                            123.66962,
                        ]
                    ]
                },
                "temporal": {
                    "interval": ["2022-06-26Z07:07:07Z", "2024-09-18Z11:39:25Z"]
                },
            },
            "summaries": {
                "datetime": {
                    "minimum": "2022-06-26Z07:07:07Z",
                    "maximum": "2024-09-18Z11:39:25Z",
                },
                "instruments": "QDec_2014-101",
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
                    "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-deflectometry-collection-stac.json",
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
                    "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-deflectometry-collection-stac.json",
                    "type": "application/geo+json",
                    "title": "Reference to this STAC collection file",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/AY39-2023-09-18Z11:39:25Z-deflectometry-item-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "STAC item of Deflectometry measurements for AY39 at 2023-09-18Z11:39:25Z",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/AY39-2024-09-18Z11:39:25Z-deflectometry-item-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "STAC item of Deflectometry measurements for AY39 at 2024-09-18Z11:39:25Z",
                },
                {
                    "rel": "item",
                    "href": "INSERT/SOMETHING/HERE/AY39-2023-06-26Z07:07:07Z-deflectometry-item-stac.json?download=1",
                    "type": "application/geo+json",
                    "title": "STAC item of Deflectometry measurements for AY39 at 2022-06-26Z07:07:07Z",
                },
            ],
        }

        assert not deepdiff.DeepDiff(
            collection, expected, ignore_numeric_type_changes=True
        )


def test_make_deflectometry_item(
    deflectometry_item_data: Tuple[str, pd.Series],
) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    deflectometry_item_data : Tuple[str, pd.Series]
        The test fixture.
    """
    heliostat_key, data = deflectometry_item_data
    assert isinstance(heliostat_key, str)
    _, item = make_deflectometry_item(heliostat_key=heliostat_key, heliostat_data=data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "AY39-2023-09-18Z11:39:25Z-deflectometry",
        "type": "Feature",
        "title": "Deflectometry measurement of AY39",
        "description": "Measured raw and filled deflectometry data containing point clouds and surface normals for heliosat AY39 and the deflectometry measurement results summary",
        "collection": "AY39-deflectometry-collection",
        "geometry": {
            "type": "Point",
            "coordinates": [50.914686955478864, 6.387702537483708, 88.66962],
        },
        "bbox": [
            50.914666955478864,
            6.387682537483708,
            86.66962,
            50.91470695547886,
            6.387722537483708,
            90.66962,
        ],
        "properties": {
            "datetime": "2023-09-18Z11:39:25Z",
            "created": "2023-09-18Z11:39:25Z",
            "instruments": "QDec_2014-101",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-2023-09-18Z11:39:25Z-deflectometry-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the entire catalogue for WRI1030197",
            },
            {
                "rel": "parent",
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-deflectometry-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-deflectometry-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "raw_measurement": {
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-2023-09-18Z11:39:25Z-deflectometry.h5",
                "roles": ["data"],
                "type": "application/x-hdf5",
                "title": "Raw deflectometry measurement of AY39 at 2023-09-18Z11:39:25Z",
            },
            "filled_measurement": {
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-filled-2023-09-18Z11:39:25Z-deflectometry.h5",
                "roles": ["data"],
                "type": "application/x-hdf5",
                "title": "Filled deflectometry measurement of AY39 at 2023-09-18Z11:39:25Z",
            },
            "results_summary": {
                "href": "https://paint-database.org/WRI1030197/AY39/Deflectometry/AY39-2023-09-18Z11:39:25Z-deflectometry-result.pdf",
                "roles": ["metadata"],
                "type": "application/pdf",
                "title": "Summary of deflectometry measurement of AY39 at 2023-09-18Z11:39:25Z",
            },
        },
    }

    assert not deepdiff.DeepDiff(item, expected, ignore_numeric_type_changes=True)


def test_make_delfectometry_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        make_deflectometry_collection("AB123", pd.DataFrame())
