#!/usr/bin/env python

import argparse
import json
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.juelich_weather_convertor import JuelichWeatherConvertor
from paint.data.juelich_weather_stac_item import make_juelich_weather_item


def main(arguments: argparse.Namespace) -> None:
    """
    Merge the Juelich weather data and save it as an HDF5 file and generate the associate STAC item.

    This script merges all Juelich weather data files and saves the result as as an HDF5 file before generating the
    appropriate STAC item. Additionally, the metadata for this item is saved for collection creation later.

    Parameters
    ----------
    arguments: argparse.Namespace
        The command line arguments.

    """
    # check if saved metadata exists and load if required
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

    weather_convertor = JuelichWeatherConvertor(
        input_root_dir=arguments.input_root_dir,
        output_path=arguments.output_path,
        file_name=arguments.file_name,
    )
    metadata = weather_convertor.merge_and_save_to_hdf5()

    juelich_stac = make_juelich_weather_item(data=metadata)
    save_path = Path(arguments.output_path) / (mappings.JUELICH_STAC_NAME + ".json")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w") as handle:
        json.dump(juelich_stac, handle)

    weather_items.loc[len(weather_items)] = [
        "Juelich weather data",
        mappings.JUELICH_STAC_URL,
        metadata[mappings.JUELICH_START],
        metadata[mappings.JUELICH_END],
        mappings.POWER_PLANT_LAT,
        mappings.POWER_PLANT_LON,
        0,  # TODO: Correct Elevation
    ]
    weather_items.to_csv(weather_items_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_root_dir", type=str, default=f"{PAINT_ROOT}/ExampleDataKIT/Weather"
    )
    parser.add_argument(
        "--output_path", type=str, default=f"{PAINT_ROOT}/ConvertedData/Weather"
    )
    parser.add_argument("--file_name", type=str, default="juelich-weather.h5")
    args = parser.parse_args()
    main(arguments=args)
