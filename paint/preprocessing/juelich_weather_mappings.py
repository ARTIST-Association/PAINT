# Names for renamed columns
DIRECT_IRRADIATION = "direct_irradiation"
"""Key for the direct irradiation column name in the Jülich weather data."""
GLOBAL_IRRADIATION = "global_irradiation"
"""Key for the global irradiation column name in the Jülich weather data."""
DIFFUSE_IRRADIATION = "diffuse_irradiation"
"""Key for the diffuse irradiation column name in the Jülich weather data."""
WIND_SPEED = "wind_speed"
"""Key for the wind speed column name in the Jülich weather data."""
WIND_DIRECTION = "wind_direction"
"""Key for the wind direction column name in the Jülich weather data."""
TEMPERATURE = "temperature"
"""Key for the temperature column name in the Jülich weather data."""
RELATIVE_HUMIDITY = "relative_humidity"
"""Key for the relative humidity column name in the Jülich weather data."""
PRECIPITATION = "precipitation"
"""Key for the precipitation column name in the Jülich weather data."""
ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
"""Key for the atmospheric pressure column name in the Jülich weather data."""
TEMPERATURE_DIRECT = "temperature_direct"
"""Key for the direct temperature column name in the Jülich weather data."""
TEMPERATURE_GLOBAL = "temperature_global"
"""Key for the global temperature column name in the Jülich weather data."""
TEMPERATURE_DIFFUSE = "temperature_diffuse"
"""Key for the diffuse temperature column name in the Jülich weather data."""

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
"""Dictionary to map parameter names from the original name to the saved name for the Jülich weather data."""

juelich_metadata_description = {
    DIRECT_IRRADIATION: "The direct irradiance, i.e., part of the solar irradiance directly reaching the surface.",
    GLOBAL_IRRADIATION: "The global irradiance, i.e., the sum of the direct and diffuse irradiation.",
    DIFFUSE_IRRADIATION: "The diffuse irradiance, i.e., the part of the irradiance scattered by the atmosphere.",
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
"""Dictionary to include descriptions for the weather parameters for the attributes in the Jülich weather HDF5 files."""

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
"""Dictionary to include units for the weather parameters in the Jülich weather HDF5 files."""

DESCRIPTION = "description"
"""Key to access the description attribute for the Jülich weather HDF5 files."""
UNITS = "units"
"""Key to access the units attribute for the Jülich weather HDF5 files."""
