import deepdiff
import numpy as np
import pytest

from paint.data.tower_stac import make_tower_item


@pytest.fixture
def tower_item_data() -> dict[str, np.ndarray]:
    """
    Make a fixture with data for generating a tower STAC item.

    Returns
    -------
    dict[str, np.ndarray]
        The data for the Juelich stac item.
    """
    return {
        "longitude": np.array([6.38750587, 6.38785603]),
        "latitude": np.array([50.91338895, 50.91342485]),
        "Elevation": np.array([119.268, 144.82]),
    }


def test_make_tower_item(tower_item_data: dict[str, np.ndarray]) -> None:
    """
    Test the creation of a STAC item.

    Parameters
    ----------
    tower_item_data : Dict[str, np.ndarray]
        The test fixture.
    """
    item = make_tower_item(tower_item_data)
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "WRI1030197-tower-measurements",
        "type": "Feature",
        "title": "The coordinates of different targets from the Juelich solar tower",
        "description": "The latitude, longitude, and elevation coordinates for the center and corners of all "
        "calibration targets and the receiver for the Juelich solar tower as well as the associated normal vectors, "
        "geometry type, and properties of the power plant",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [50.91338895, 6.38750587, 119.268],
                [50.91342485, 6.38785603, 144.82],
                [50.91338895, 6.38750587, 119.268],
            ],
        },
        "bbox": [50.91338895, 6.38750587, 119.268, 50.91342485, 6.38785603, 144.82],
        "properties": {
            "datetime": None,
            "start_datetime": "2013-02-25",
            "end_datetime": "2020-10-07",
            "created": "2013-02-25",
            "updated": "2020-10-07",
        },
        "links": [
            {
                "rel": "self",
                "href": "https://paint-database.org/WRI1030197/WRI1030197-tower-measurements-item-stac.json",
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
                "href": "https://paint-database.org/WRI1030197/WRI1030197-catalog-stac.json",
                "type": "application/geo+json",
                "title": "Reference to the catalogue for WRI1030197",
            },
        ],
        "assets": {
            "measurements": {
                "href": "https://paint-database.org/WRI1030197/WRI1030197-tower-measurements.json",
                "roles": ["data"],
                "type": "application/geo+json",
                "title": "Tower measurement properties",
            }
        },
    }

    assert not deepdiff.DeepDiff(
        item, expected, ignore_numeric_type_changes=True, significant_digits=5
    )
