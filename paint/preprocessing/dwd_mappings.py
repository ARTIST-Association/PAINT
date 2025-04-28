dwd_parameter_mapping = {
    "radiation_sky_short_wave_diffuse": "short_wave_radiation",
    "radiation_global": "global_radiation",
    "sunshine_duration": "sunshine_duration",
    "radiation_sky_long_wave": "long_wave_radiation",
    "cloud_cover_total": "cloud_cover",
    "humidity": "humidity",
    "pressure_vapor": "pressure_vapor",
    "visibility_range": "visibility_range",
    "weather": "weather_type",
}
"""Dictionary to map DWD names to simpler names for saving the data."""

DWD_10_MIN_DESCRIPTION = {
    "radiation_sky_short_wave_diffuse": "10min-sum of diffuse solar radiation.",
    "radiation_global": "10min-sum of solar incoming radiation.",
    "sunshine_duration": "10min-sum of sunshine duration.",
    "radiation_sky_long_wave": "10min-sum of longwave downward radiation.",
}
"""Dictionary to include a description for the 10 min resolution weather parameters in the DWD weather HDF5 file."""
DWD_10_MIN_UNIT = {
    "radiation_sky_short_wave_diffuse": "J/cm²",
    "radiation_global": "J/cm²",
    "sunshine_duration": "h",
    "radiation_sky_long_wave": "J/cm²",
}
"""Dictionary to include units for the 10 min resolution weather parameters in the DWD weather HDF5 file."""
DWD_1H_DESCRIPTION = {
    "cloud_cover_total": "The total cloud cover.",
    "humidity": "The humidity.",
    "pressure_vapor": "The vapor pressure.",
    "visibility_range": "The range of visibility.",
    "weather": "The weather code of the current condition.",
}
"""Dictionary to include a description for the 1h resolution weather parameters in the DWD weather HDF5 file."""
DWD_1H_UNIT = {
    "cloud_cover_total": "fraction, 1/8",
    "humidity": "%",
    "pressure_vapor": "hPa",
    "visibility_range": "m",
    "weather": "-",
}
"""Dictionary to include units for the 1h resolution weather parameters in the DWD weather HDF5 file."""
DESCRIPTION = "description"
"""Key to access the description attribute for the DWD weather HDF5 file."""
UNITS = "units"
"""Key to access the units attribute for the DWD weather HDF5 file."""
