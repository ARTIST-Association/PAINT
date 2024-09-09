#!/usr/bin/env python

import argparse
import json
import os
from pathlib import Path

import pandas as pd

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.dwd_stac_item import make_dwd_item
from paint.data.dwd_weather import DWDWeatherData
from paint.util.utils import to_utc_single


def main(arguments: argparse.Namespace) -> None:
    """
    Download and save the DWD weather as an HDF5 file and generate the associate STAC item.

    This script downloads and saves the DWD weather as an HDF5 file and then generates the appropriate STAC item.
    Additionally, the metadata for this item is saved for collection creation later.

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

    dwd_weather = DWDWeatherData(
        parameters_10min=arguments.parameters_10min,
        parameters_1h=arguments.parameters_1h,
        station_ids=arguments.station_ids,
        start_date=arguments.start_date,
        end_date=arguments.end_date,
        output_path=arguments.output_path,
        file_name=arguments.file_name,
        ts_shape=arguments.ts_shape,
    )
    metadata = dwd_weather.download_and_save_data()
    metadata = metadata.rename(
        columns={
            "station_id": mappings.DWD_STATION_ID,
            "latitude": mappings.LATITUDE_KEY,
            "longitude": mappings.LONGITUDE_KEY,
            "height": mappings.ELEVATION,
            "name": mappings.DWD_STATION_NAME,
        }
    )
    metadata[mappings.DWD_START] = to_utc_single(arguments.start_date)
    metadata[mappings.DWD_END] = to_utc_single(arguments.end_date)
    for _, data in metadata.iterrows():
        dwd_stac = make_dwd_item(data=data)
        save_path = Path(arguments.output_path) / (mappings.DWD_STAC_NAME + ".json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as handle:
            json.dump(dwd_stac, handle)
        dwd_url = mappings.DWD_STAC_URL
        weather_items.loc[len(weather_items)] = [
            "DWD weather data",
            dwd_url,
            data[mappings.DWD_START],
            data[mappings.DWD_END],
            data[mappings.LATITUDE_KEY],
            data[mappings.LONGITUDE_KEY],
            data[mappings.ELEVATION],
        ]
    weather_items.to_csv(weather_items_path, index=False)


if __name__ == "__main__":
    lsdf_root = os.environ.get("LSDFPROJECTS")
    assert isinstance(lsdf_root, str)
    output_path = (
        Path(lsdf_root) / "paint" / mappings.POWER_PLANT_GPPD_ID / mappings.SAVE_WEATHER
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parameters_10min",
        default=[
            "radiation_sky_short_wave_diffuse",
            "radiation_global",
            "sunshine_duration",
            "radiation_sky_long_wave",
        ],
    )
    parser.add_argument(
        "--parameters_1h",
        default=[
            "cloud_cover_total",
            "humidity",
            "pressure_vapor",
            "visibility_range",
            "weather",
        ],
    )
    parser.add_argument("--station_ids", default=["15000"])
    parser.add_argument("--start_date", type=str, default="2021-04-01")
    parser.add_argument("--end_date", type=str, default="2024-03-01")
    parser.add_argument("--output_path", type=str, default=str(output_path))
    parser.add_argument("--file_name", type=str, default="dwd-weather.h5")
    parser.add_argument("--ts_shape", type=str, default="long")
    args = parser.parse_args()
    main(arguments=args)
