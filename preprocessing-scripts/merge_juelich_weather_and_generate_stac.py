#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.preprocessing.juelich_weather_converter import JuelichWeatherConverter
from paint.preprocessing.juelich_weather_stac_item import make_juelich_weather_item


def main(arguments: argparse.Namespace) -> None:
    """
    Merge the Juelich weather data and save it as an HDF5 file and generate the associate STAC item.

    This script merges all Juelich weather data files and saves the result as an HDF5 file before generating the
    appropriate STAC item. Additionally, the metadata for this item is saved for collection creation later.

    Parameters
    ----------
    arguments : argparse.Namespace
        The command-line arguments.

    """
    # Check if saved metadata exists and load if required.
    weather_items_path = Path(f"{PAINT_ROOT}/TEMPDATA/weather_items.csv")
    if weather_items_path.exists():
        weather_items = pd.read_csv(weather_items_path)
    else:
        weather_items_path.parent.mkdir(parents=True, exist_ok=True)
        weather_items = pd.DataFrame(
            columns=[
                mappings.TITLE_KEY,
                mappings.URL_KEY,
                mappings.DWD_START,
                mappings.DWD_END,
                mappings.LATITUDE_KEY,
                mappings.LONGITUDE_KEY,
                mappings.ELEVATION,
            ]
        )

    weather_converter = JuelichWeatherConverter(
        input_root_dir=arguments.input_root_dir,
        output_path=arguments.output_path,
    )
    metadata_df = weather_converter.merge_and_save_to_hdf5()

    for group_name, metadata in metadata_df.iterrows():
        assert isinstance(group_name, str)
        juelich_stac = make_juelich_weather_item(data=metadata, month_group=group_name)
        save_path = Path(arguments.output_path) / (
            mappings.JUELICH_STAC_NAME % group_name + ".json"
        )
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as handle:
            json.dump(juelich_stac, handle)

        weather_items.loc[len(weather_items)] = [
            f"Juelich weather data for {group_name}",
            f"{mappings.JUELICH_STAC_URL % group_name}.json",
            metadata[mappings.JUELICH_START],
            metadata[mappings.JUELICH_END],
            mappings.JUELICH_WEATHER_LAT,
            mappings.JUELICH_WEATHER_LON,
            mappings.JUELICH_WEATHER_ALTITUDE,
        ]
        weather_items.to_csv(weather_items_path, index=False)


if __name__ == "__main__":
    lsdf_root = str(os.environ.get("LSDFPROJECTS"))
    input_folder = Path(lsdf_root) / "paint" / "MeteoDaten"
    output_folder = (
        Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID / mappings.SAVE_WEATHER
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_root_dir", type=str, default=str(input_folder))
    parser.add_argument("--output_path", type=str, default=str(output_folder))
    args = parser.parse_args()
    main(arguments=args)
