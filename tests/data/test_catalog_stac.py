import argparse
import pathlib
import tempfile

import deepdiff

import paint.data.catalog_stac
import paint.util.paint_mappings


def test_make_catalog() -> None:
    """Test STAC catalog generation."""
    catalog = paint.data.catalog_stac.make_catalog()
    expected = {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": "WRI1030197-catalog",
        "type": "Catalog",
        "title": "Operational data of concentrating solar power plant WRI1030197",
        "description": "Calibration images, deflectometry measurements, kinematics and weather data",
        "links": [
            {
                "rel": "self",
                "href": "https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": "https://zenodo.org/record/elcatalogo/files/catalogue-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "child",
                "href": "https://zenodo.org/record/loscalibrationes/files/WRI1030197-calibration-stac.json?download=1",
                "type": "application/geo+json",
                "title": "Reference to the STAC collection containing the calibration data",
            },
        ],
    }

    assert not deepdiff.DeepDiff(catalog, expected)


def test_save_catalog() -> None:
    """Test catalog is saved on disk."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = pathlib.Path(tmp_dir)
        catalog_file = output_dir / paint.util.paint_mappings.CATALOG_FILE

        arguments = argparse.Namespace(output=output_dir)
        catalog = paint.data.catalog_stac.make_catalog()

        assert not catalog_file.exists()
        paint.data.catalog_stac.save_catalog(arguments, catalog)
        assert catalog_file.exists()
        assert catalog_file.stat().st_size > 0
