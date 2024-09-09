import deepdiff
import pandas as pd
import pytest

from paint.data.weather_collection_stac import make_weather_collection


@pytest.fixture
def weather_collection_data():
    """
    Make a fixture with data for generating the weather collection.

    Returns
    -------
    pd.DataFrame
        The data for the weather collection as a test fixture.
    """
    # Define the data
    data = {
        "title": ["DWD weather data"],
        "url": ["INSERT/SOMETHING/HERE/dwd-weather-item-stac?download=1"],
        "start": ["2021-03-31Z22:00:00Z"],
        "end": ["2024-02-29Z23:00:00Z"],
        "latitude": [50.7983],
        "longitude": [6.0244],
        "Elevation": [231.0],
    }

    return pd.DataFrame(data)


def test_make_weather_collection(
    weather_collection_data: pd.DataFrame,
) -> None:
    """
    Test the creation of the weather STAC collection.

    Parameters
    ----------
    weather_collection_data: pd.DataFrame
        The test fixture.
    """
    collection = make_weather_collection(data=weather_collection_data)

    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "weather-collection",
        "type": "Collection",
        "title": "All weather measurements",
        "description": "All weather measurements",
        "keywords": ["weather"],
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
            "spatial": {"bbox": [[50.7983, 6.0244, 231.0, 50.7983, 6.0244, 231.0]]},
            "temporal": {"interval": ["2021-03-31Z22:00:00Z", "2024-02-29Z23:00:00Z"]},
        },
        "summaries": {
            "datetime": {
                "minimum": "2021-03-31Z22:00:00Z",
                "maximum": "2024-02-29Z23:00:00Z",
            }
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
                "href": "https://paint-database.org/WRI1030197/Weather/weather-collection-stac.json",
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
                "href": "weather-collection-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "item",
                "href": "INSERT/SOMETHING/HERE/dwd-weather-item-stac?download=1",
                "type": "application/geo+json",
                "title": "STAC item of DWD weather data",
            },
        ],
    }

    assert not deepdiff.DeepDiff(collection, expected, ignore_numeric_type_changes=True)


def test_make_weather_collection_fail() -> None:
    """Test conversion failure on incomplete input data."""
    with pytest.raises(KeyError):
        make_weather_collection(pd.DataFrame())
