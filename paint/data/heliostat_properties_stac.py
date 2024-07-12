#!/usr/bin/env python

import argparse
import json
import pathlib
from typing import Any
import sys
import pandas as pd

import paint.util.paint_mappings as mappings
import paint.util.utils as utils


def make_collection(data: pd.DataFrame) -> dict[str, Any]:
    """
    Generate the STAC collection.

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe containing all image data.

    Returns
    -------
    dict[str, Any]
        The STAC collection as dictionary.
    """
    return {
        "stac_version": mappings.STAC_VERSION,
        "stac_extensions": [mappings.ITEM_ASSETS_SCHEMA, mappings.CSP_SCHEMA],
        "id": mappings.HELIOSTAT_PROPERTY_COLLECTION_ID,
        "type": mappings.COLLECTION,
        "title": f"Heliostat properties of CSP {mappings.POWER_PLANT_GPPD_ID}",
        "description": f"Properties of the heliostats of the concentrating solar power plant {mappings.POWER_PLANT_GPPD_ID} in Jülich, Germany. These properties include their meausred position and their construction details.",
        "keywords": ["csp", "heliostat", "position", "construction",],
        "license": mappings.LICENSE,
        "providers": [mappings.DLR, mappings.KIT],
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        mappings.POWER_PLANT_LON,
                        mappings.POWER_PLANT_LAT,
                        mappings.POWER_PLANT_LON,
                        mappings.POWER_PLANT_LAT,
                    ]
                ]
            },
            "temporal": {
                "interval": [
                    data[mappings.CREATED_AT].min().strftime(mappings.TIME_FORMAT),
                    data[mappings.CREATED_AT].max().strftime(mappings.TIME_FORMAT),
                ]
            },
        },
        "summaries": {
            "csp:gppd_id": {
                "type": "string",
                "const": mappings.POWER_PLANT_GPPD_ID,
                "count": data.shape[0],
            },
            "datetime": {
                "minimum": data[mappings.CREATED_AT]
                .min()
                .strftime(mappings.TIME_FORMAT),
                "maximum": data[mappings.CREATED_AT]
                .max()
                .strftime(mappings.TIME_FORMAT),
            },
            "view:sun_azimuth": {
                "minimum": data[mappings.AZIMUTH].min(),
                "maximum": data[mappings.AZIMUTH].max(),
            },
            "view:sun_elevation": {
                "minimum": data[mappings.ELEVATION].min(),
                "maximum": data[mappings.ELEVATION].max(),
            },
            "instruments": list(data[mappings.SYSTEM].unique()),
        },
        "links": [
            mappings.LICENSE_LINK,
            {
                "rel": "self",
                "href": mappings.HELIOSTAT_PROPERTY_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
            {
                "rel": "root",
                "href": mappings.CATALOGUE_URL,
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the entire catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
            {
                "rel": "collection",
                "href": mappings.HELIOSTAT_PROPERTY_COLLECTION_URL,
                "type": mappings.MIME_GEOJSON,
                "title": "Reference to this STAC collection file",
            },
        ]
        + [
            {
                "rel": "item",
                "href": mappings.HELIOSTAT_PROPERTY_ITEM_URL % image,
                "type": mappings.MIME_GEOJSON,
                "title": f"STAC item of image {image}",
            }
            for image, _ in data.iterrows()
        ],
        "item_assets": {
            "target": {
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": "Calibration images of heliostats",
            }
        },
    }


def make_item(image: int, heliostat_data: pd.Series) -> dict[str, Any]:
    """
    Generate a STAC item for an image.

    Parameters
    ----------
    image: int
        The image id.
    heliostat_data: pd.Series.
        The data belonging to the heliostat.

    Returns
    -------
    dict[str, Any]
        The STAC item data as dictionary.
    """
    return {
        "stac_version": "1.0.0",
        "stac_extensions": [
            "view",
            "https://raw.githubusercontent.com/ARTIST-Association/csp/main/json-schema/schema.json",
        ],
        "id": f"{image}",
        "type": "Feature",
        "title": f"Calibration of heliostat {image}",
        "description": f"Images of focused sunlight on the calibration target of heliostat {image}",
        "collection": mappings.HELIOSTAT_PROPERTY_COLLECTION_ID,
        "geometry": {
            "type": "Point",
            "coordinates": [mappings.POWER_PLANT_LON, mappings.POWER_PLANT_LAT],
        },
        "properties": {
            "datetime": heliostat_data[mappings.CREATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "created": heliostat_data[mappings.CREATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "updated": heliostat_data[mappings.UPDATED_AT].strftime(
                mappings.TIME_FORMAT
            ),
            "instruments": [heliostat_data[mappings.SYSTEM]],
        },
        "view:sun_azimuth": heliostat_data[mappings.AZIMUTH],
        "view:sun_elevation": heliostat_data[mappings.ELEVATION],
        "csp:gppd_id": mappings.POWER_PLANT_GPPD_ID,
        "csp:target_id": heliostat_data[mappings.HELIOSTAT_PROPERTY_TARGET],
        "csp:heliostats": [
            {
                "csp:heliostat_id": heliostat_data[mappings.HELIOSTAT_ID],
                "csp:heliostat_motors": [
                    heliostat_data[mappings.AXIS1_MOTOR],
                    heliostat_data[mappings.AXIS2_MOTOR],
                ],
            }
        ],
        "links": [
            {
                "rel": "self",
                "href": f"./{image}-stac.json",
                "type": "application/geo+json",
                "title": "Reference to this STAC file",
            },
            {
                "rel": "root",
                "href": f"./{mappings.CATALOGUE_URL}",
                "type": mappings.MIME_GEOJSON,
                "title": f"Reference to the entire catalogue for {mappings.POWER_PLANT_GPPD_ID}",
            },
            {
                "rel": "parent",
                "href": f"{mappings.HELIOSTAT_PROPERTY_COLLECTION_URL}/{mappings.HELIOSTAT_PROPERTY_COLLECTION_FILE}",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
            {
                "rel": "collection",
                "href": f"{mappings.HELIOSTAT_PROPERTY_COLLECTION_URL}/{mappings.HELIOSTAT_PROPERTY_COLLECTION_FILE}",
                "type": "application/geo+json",
                "title": "Reference to the collection STAC file",
            },
        ],
        "assets": {
            "target": {
                "href": f"../{image}.png",
                "roles": ["data"],
                "type": mappings.MIME_PNG,
                "title": f"Calibration image of heliostat with id {image}",
            }
        },
    }


def prepare_axis_file_for_concatenation(arguments: argparse.Namespace) -> pd.DataFrame:
    df_axis = pd.read_csv(arguments.input_axis, header=0, decimal=",", sep=";",)
    pivoted_df = df_axis.pivot(index='HeliostatId', columns='Number')
    # Flatten the multi-index columns
    pivoted_df.columns = ['_'.join(map(str, col)).strip() for col in pivoted_df.columns.values]

    # Reset index to bring 'HeliostatId' back as a column
    pivoted_df = pivoted_df.reset_index()
    # Rename columns that are always identical
    pivoted_df = pivoted_df.rename(columns={
        'FieldId_1': 'FieldId',
        'CreatedAt_1': 'CreatedAt',
        'UpdatedAt_1': 'UpdatedAt'
    })
    pivoted_df = pivoted_df.drop(columns=['FieldId_2', 'CreatedAt_2', 'UpdatedAt_2'])
    pivoted_df.columns = [col.replace('_1', '_axis_1').replace('_2', '_axis_2') for col in pivoted_df.columns]
    # Get list of columns ending with _axis_1 and _axis_2
    axis_1_columns = [col for col in pivoted_df.columns if col.endswith('_axis_1')]
    axis_2_columns = [col for col in pivoted_df.columns if col.endswith('_axis_2')]

    # Sort the columns list to have _axis_1 columns first, followed by _axis_2 columns
    sorted_columns = axis_1_columns + axis_2_columns
    # Reorder columns in the dataframe
    # Reorder columns in the dataframe
    pivoted_df = pivoted_df[['HeliostatId', 'FieldId', 'CreatedAt'] + sorted_columns]
    pivoted_df.set_index(mappings.HELIOSTAT_ID, inplace=True)
    pivoted_df.index = pivoted_df.index.map(utils.heliostat_id_to_name)
    return pivoted_df

def prepare_heliostat_positions_for_concatenation(arguments: argparse.Namespace) -> pd.DataFrame:
    df_heliostat_positions = pd.read_excel(arguments.input_position, header=0)
    df_heliostat_positions.set_index(
            mappings.INTERNAL_NAME_INDEX, inplace=True
        )
    df_heliostat_positions.rename_axis('HeliostatId', inplace=True)
    # Drop the specified columns
    df_heliostat_positions.drop(columns=['RowName', 'Number', 'ColumnName'], inplace=True)
    
    # Rename the columns
    df_heliostat_positions.rename(columns={
        'x': 'East',
        'y': 'North',
        'z': 'Altitude',
        'Spalte1': 'Heliostat Size'
    }, inplace=True)
    
    return df_heliostat_positions

def merge_and_sort_df(df_heliostat_positions: pd.DataFrame, df_axis: pd.DataFrame) -> pd.DataFrame:
    df_concatenated = pd.concat([df_heliostat_positions, df_axis], axis=1, join='inner')
    created_at = df_concatenated.pop('CreatedAt')
    df_concatenated.insert(0, 'CreatedAt', created_at)
    return df_concatenated
def convert(arguments: argparse.Namespace) -> None:
    """
    Convert an internal CSV file to STAC.

    Parameters
    ----------
    arguments: argparse.Namespace
        The arguments containing input and output path.
    """
    # ensure that the output paths exist
    arguments.output.mkdir(parents=True, exist_ok=True)

    # read in the data in CSV

    df_heliostat_positions = prepare_heliostat_positions_for_concatenation(arguments)
    df_axis = prepare_axis_file_for_concatenation(arguments)
    df_concatenated = merge_and_sort_df(df_heliostat_positions, df_axis)

    # generate the STAC collection
    with open(arguments.output / mappings.HELIOSTAT_PROPERTY_COLLECTION_FILE, "w") as handle:
        stac_item = make_collection(df_concatenated)
        json.dump(stac_item, handle)

    # generate the STAC item files for each image
    for image, heliostat_data in data.iterrows():
        with open(
            arguments.output / (mappings.HELIOSTAT_PROPERTY_ITEM % image), "w"
        ) as handle:
            stac_item = make_item(image, heliostat_data)
            json.dump(stac_item, handle)

    # generate the STAC collection
    with open(arguments.output / mappings.HELIOSTAT_PROPERTY_COLLECTION_FILE, "w") as handle:
        stac_item = make_collection(data)
        json.dump(stac_item, handle)


import argparse
import pathlib
import sys

def main(args):
    convert(args)

if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = ["heliostat_properties_stac.py", "-i_position", "data/Heliostatpositionen_xyz.xlsx", "-i_axis", "data/axis_data.csv", "-o", "stac/heliostat_property_collection"]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i_position",
        "--input_position",
        type=pathlib.Path,
        default="dataframe.csv",
        help="Path to the primary input file"
    )
    parser.add_argument(
        "-i_axis",
        "--input_axis",
        type=pathlib.Path,
        default="axis_data.csv",
        help="Path to the secondary input file"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default="stac",
        help="Path to the output file"
    )
    args = parser.parse_args()

    main(args)

