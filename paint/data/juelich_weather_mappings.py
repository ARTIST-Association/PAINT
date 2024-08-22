drop_columns = [
    "TriggerBarometer",
    "Fuse1",
    "Fuse2",
    "Fuse3",
    "Fuse4",
    "Fuse5",
    "Fuse6",
    "Fuse7",
    "Fuse9",
    "UPS",
    "OvervoltageProtection",
    "Lnet",
    "Tb",
    "Ld",
]
"""Columns to drop from the initial Juelich weather data frame."""

# Names for renamed columns
DIRECT_IRRADIATION = "direct_irradiation"
GLOBAL_IRRADIATION = "global_irradiation"
DIFFUSE_IRRADIATION = "diffuse_irradiation"
WIND_SPEED = "wind_speed"
WIND_DIRECTION = "wind_direction"
TEMPERATURE = "temperature"
RELATIVE_HUMIDITY = "relative_humidity"
PRECIPITATION = "precipitation"
ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
TEMPERATURE_DIRECT = "temperature_direct"
TEMPERATURE_GLOBAL = "temperature_global"
TEMPERATURE_DIFFUSE = "temperature_diffuse"

juelich_weather_parameter_mapping = {
    "Direct": DIRECT_IRRADIATION,
    "Global": GLOBAL_IRRADIATION,
    "Diffuse": DIFFUSE_IRRADIATION,
    "WindSpeed": WIND_SPEED,
    "WindDirection": WIND_DIRECTION,
    "AmbientTemperature": TEMPERATURE,
    "Humidity": RELATIVE_HUMIDITY,
    "Rain": PRECIPITATION,
    "Pressure": ATMOSPHERIC_PRESSURE,
    "PT100Direct": TEMPERATURE_DIRECT,
    "PT100Global": TEMPERATURE_GLOBAL,
    "PT100Diffuse": TEMPERATURE_DIFFUSE,
}
"""Dictionary to map parameter names for the Juelich weather data."""

juelich_metadata_description = {
    DIRECT_IRRADIATION: "The direct irradiance, i.e. part of the solar irradiance directly reaching the surface.",
    GLOBAL_IRRADIATION: "The global irradiance, i.e. the sum of the direct and diffuse irradiation.",
    DIFFUSE_IRRADIATION: "The diffuse irradiance, i.e. the part of the irradiance scattered by the atmosphere.",
    WIND_SPEED: "The intensity of the wind.",
    WIND_DIRECTION: "The direction of the wind.",
    TEMPERATURE: "The ambient temperature.",
    RELATIVE_HUMIDITY: "The relative humidity in the air.",
    PRECIPITATION: "The amount of water rain registered.",
    ATMOSPHERIC_PRESSURE: "The observed atmospheric pressure.",
    TEMPERATURE_DIRECT: "The internal temperature used to calculate the direct irradiation.",
    TEMPERATURE_GLOBAL: "The internal temperature used to calculate the global irradiance.",
    TEMPERATURE_DIFFUSE: "The internal temperature used to calculate the diffuse irradiance.",
}
"""Dictionary to include Juelich weather parameter descriptions in the HDF5 file."""

juelich_metadata_units = {
    DIRECT_IRRADIATION: "[W/m2]",
    GLOBAL_IRRADIATION: "[W/m2]",
    DIFFUSE_IRRADIATION: "[W/m2]",
    WIND_SPEED: "[m/s]",
    WIND_DIRECTION: "Angle in Degrees, between 0 and 360",
    TEMPERATURE: "Degrees Celsius",
    RELATIVE_HUMIDITY: "Percent [%]",
    PRECIPITATION: "[mm/d]",
    ATMOSPHERIC_PRESSURE: "[hPa]",
    TEMPERATURE_DIRECT: "Degrees Celsius",
    TEMPERATURE_GLOBAL: "Degrees Celsius",
    TEMPERATURE_DIFFUSE: "Degrees Celsius",
}
"""Dictionary to include Juelich weather parameter units in the HDF5 file."""

DESCRIPTION = "description"
UNITS = "units"
