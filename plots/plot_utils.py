from typing import Union

import matplotlib as mpl
import torch


def set_plot_style() -> None:
    """Set global plot style for all plots."""
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    mpl.rcParams["font.size"] = 12
    mpl.rcParams["axes.titlesize"] = 14
    mpl.rcParams["axes.labelsize"] = 12
    mpl.rcParams["axes.labelweight"] = "bold"
    mpl.rcParams["xtick.labelsize"] = 10
    mpl.rcParams["ytick.labelsize"] = 10
    mpl.rcParams["legend.fontsize"] = 10


def decimal_to_dms(value: float, is_latitude: bool = True) -> str:
    """
    Convert decimal degrees to degrees, minutes, and seconds (DMS).

    Parameters
    ----------
    value : float
        The decimal degree value to convert.
    is_latitude : bool, optional
        Whether the value provided is latitude (N/S), otherwise longitude (E/W) (Default: True).

    Returns
    -------
    str
        The coordinate in DMS format as a string.
    """
    direction = (
        "N"
        if (value >= 0 and is_latitude)
        else "S"
        if is_latitude
        else "E"
        if value >= 0
        else "W"
    )
    abs_value = abs(value)
    degrees = int(abs_value)
    minutes = int((abs_value - degrees) * 60)
    seconds = (abs_value - degrees - minutes / 60) * 3600
    return f"{degrees}° {minutes}' {seconds:.4f}'' {direction}"


def convert_wgs84_coordinates_to_local_enu(
    coordinates_to_transform: torch.Tensor,
    reference_point: torch.Tensor,
    device: Union[torch.device, str] = "cpu",
) -> torch.Tensor:
    """
    Transform coordinates from latitude, longitude and altitude (WGS84) to local east, north, up (ENU).

    This function calculates the north and east offsets in meters of a coordinate from the reference point.
    It converts the latitude and longitude to radians, calculates the radius of curvature values,
    and then computes the offsets based on the differences between the coordinate and the reference point.
    Finally, it returns a tensor containing these offsets along with the altitude difference.

    Parameters
    ----------
    coordinates_to_transform : torch.Tensor
        The coordinates in latitude, longitude, altitude that are to be transformed.
    reference_point : torch.Tensor
        The center of origin of the ENU coordinate system in WGS84 coordinates.
    device : Union[torch.device, str]
        The device on which to initialize tensors (default is cuda).

    Returns
    -------
    torch.Tensor
        The east offset in meters, north offset in meters, and the altitude difference from the reference point.
    """
    device = torch.device(device)
    wgs84_a = 6378137.0  # Major axis in meters
    wgs84_b = 6356752.314245  # Minor axis in meters
    wgs84_e2 = (wgs84_a**2 - wgs84_b**2) / wgs84_a**2  # Eccentricity squared

    # Convert latitude and longitude to radians.
    lat_rad = torch.deg2rad(coordinates_to_transform[0])
    lon_rad = torch.deg2rad(coordinates_to_transform[1])
    alt = coordinates_to_transform[2] - reference_point[2]
    lat_tower_rad = torch.deg2rad(reference_point[0])
    lon_tower_rad = torch.deg2rad(reference_point[1])

    # Calculate meridional radius of curvature for the first latitude.
    sin_lat1 = torch.sin(lat_rad)
    rn1 = wgs84_a / torch.sqrt(1 - wgs84_e2 * sin_lat1**2)

    # Calculate transverse radius of curvature for the first latitude.
    rm1 = (wgs84_a * (1 - wgs84_e2)) / ((1 - wgs84_e2 * sin_lat1**2) ** 1.5)

    # Calculate delta latitude and delta longitude in radians.
    dlat_rad = lat_tower_rad - lat_rad
    dlon_rad = lon_tower_rad - lon_rad

    # Calculate north and east offsets in meters.
    north_offset_m = dlat_rad * rm1
    east_offset_m = dlon_rad * rn1 * torch.cos(lat_rad)

    return torch.tensor(
        [-east_offset_m, -north_offset_m, alt], dtype=torch.float32, device=device
    )
