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
