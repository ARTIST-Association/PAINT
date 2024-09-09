"""
Convert a Gauss-Kruger coordinate to a latitude / longitude coordinate.

This code is adapted from ``https://github.com/okin/GKConverter/tree/master``, with minimal changes.
"""

from math import atan, cos, pi, sin, sqrt, tan, trunc


def convert_gk_to_lat_long(
    right: float, height: float, use_wgs84: bool = False
) -> tuple[float, float]:
    """
    Convert a Gauss-Kruger coordinate to a latitude / longitude coordinate.

    Parameters
    ----------
    right : float
        The right coordinate from the Gauss-Krueger coordinate system.
    height : float
        The height of the Gauss-Krueger coordinate system.
    use_wgs84 : bool
        Whether the wgs84 conversion should be applied (Default: ``False``).

    Returns
    -------
    float
        The converted latitude.
    float
        The converted longitude.
    """
    x, y = gauss_krueger_transformation(right, height)

    return helmert_transformation(x, y, use_wgs84)


def gauss_krueger_transformation(right: float, height: float) -> tuple[float, float]:
    """
    Perform the Gauss-Kruger transformation.

    Parameters
    ----------
    right : float
        The right coordinate from the Gauss-Krueger coordinate system.
    height : float
        The height of the Gauss-Krueger coordinate system.

    Returns
    -------
    float
        The transformed x coordinate.
    float
        The transformed y coordinate.
    """
    # Check for invalid parameters.
    if not ((right > 1000000) and (height > 1000000)):
        raise ValueError("Gauss-Kruger conversion not possible for these parameters.")

    # Variables to prepare the geovalues
    gk_right = right
    gk_height = height
    e2 = 0.0067192188
    c = 6398786.849
    rho = 180 / pi
    b_ii = (gk_height / 10000855.7646) * (gk_height / 10000855.7646)
    bf = (
        325632.08677
        * (gk_height / 10000855.7646)
        * (
            (
                (
                    ((0.00000562025 * b_ii + 0.00022976983) * b_ii - 0.00113566119)
                    * b_ii
                    + 0.00424914906
                )
                * b_ii
                - 0.00831729565
            )
            * b_ii
            + 1
        )
    )

    bf /= 3600 * rho
    co = cos(bf)
    g2 = e2 * (co * co)
    g1 = c / sqrt(1 + g2)
    t = tan(bf)
    fa = (gk_right - trunc(gk_right / 1000000) * 1000000 - 500000) / g1

    geo_dez_right = (
        bf
        - fa * fa * t * (1 + g2) / 2
        + fa * fa * fa * fa * t * (5 + 3 * t * t + 6 * g2 - 6 * g2 * t * t) / 24
    ) * rho
    dl = (
        fa
        - fa * fa * fa * (1 + 2 * t * t + g2) / 6
        + fa * fa * fa * fa * fa * (1 + 28 * t * t + 24 * t * t * t * t) / 120
    )
    geo_dez_height = dl * rho / co + trunc(gk_right / 1000000) * 3

    return geo_dez_right, geo_dez_height


def helmert_transformation(
    x: float, y: float, use_wgs84: bool = False, tolerance: float = 0.000000000000001
) -> tuple[float, float]:
    """
    Convert an (x,y) coordinate to latitude and longitude.

    Parameters
    ----------
    x : float
        The original x coordinate.
    y : float
        The original y coordinate.
    use_wgs84 : bool
        Whether the wgs84 conversion should be applied (Default: ``False``).
    tolerance : bool
        The tolerance to consider during the conversion (Default: ``0.000000000001``).

    Returns
    -------
    float
        The converted latitude coordinate.
    float
        The converted longitude coordinate.
    """
    # Define constants required for the transformation.
    earth_radius = 6378137  # Earth is a sphere with this radius in meter.
    a_bessel = 6377397.155
    ee_bessel = 0.0066743722296294277832
    scale_factor = 0.00000982
    rot_x_rad = -7.16069806998785e-06
    rot_y_rad = 3.56822869296619e-07
    rot_z_rad = 7.06858347057704e-06
    shift_x_meters = 591.28
    shift_y_meters = 81.35
    shift_z_meters = 396.39

    if use_wgs84:
        ee = 0.0066943799
    else:
        ee = 0.00669438002290

    geo_dez_right = (x / 180) * pi
    geo_dez_height = (y / 180) * pi

    n = ee_bessel * sin(geo_dez_right) * sin(geo_dez_right)
    n = 1 - n
    n = sqrt(n)
    n = a_bessel / n

    cartesian_x_meters = n * cos(geo_dez_right) * cos(geo_dez_height)
    cartesian_y_meters = n * cos(geo_dez_right) * sin(geo_dez_height)
    cartesian_z_meters = n * (1 - ee_bessel) * sin(geo_dez_right)

    cart_output_x_meters = (
        (1 + scale_factor) * cartesian_x_meters
        + rot_z_rad * cartesian_y_meters
        - rot_y_rad * cartesian_z_meters
        + shift_x_meters
    )
    cart_output_y_meters = (
        -1 * rot_z_rad * cartesian_x_meters
        + (1 + scale_factor) * cartesian_y_meters
        + rot_x_rad * cartesian_z_meters
        + shift_y_meters
    )
    cart_output_z_meters = (
        rot_y_rad * cartesian_x_meters
        - rot_x_rad * cartesian_y_meters
        + (1 + scale_factor) * cartesian_z_meters
        + shift_z_meters
    )

    geo_dez_height = atan(cart_output_y_meters / cart_output_x_meters)

    latitude = (cart_output_x_meters * cart_output_x_meters) + (
        cart_output_y_meters * cart_output_y_meters
    )
    latitude = sqrt(latitude)
    latitude = cart_output_z_meters / latitude
    latitude = atan(latitude)

    continue_conversion = True

    while continue_conversion:
        latitude_it = latitude

        n = 1 - ee * sin(latitude) * sin(latitude)
        n = sqrt(n)
        n = earth_radius / n

        latitude = (
            cart_output_x_meters * cart_output_x_meters
            + cart_output_y_meters * cart_output_y_meters
        )
        latitude = sqrt(latitude)
        latitude = (cart_output_z_meters + ee * n * sin(latitude_it)) / latitude
        latitude = atan(latitude)

        continue_conversion = abs(latitude - latitude_it) >= tolerance

    geo_dez_right = (latitude / pi) * 180
    geo_dez_height = geo_dez_height / pi * 180

    return geo_dez_right, geo_dez_height
