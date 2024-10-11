import math

import pytest

from paint.util.gauss_kruger_converter import convert_gk_to_lat_long


@pytest.mark.parametrize(
    "right, height, expected",
    [
        (2527321, 5642083, (50.91338840729781, 6.387880009062387)),
        (2587321, 5692083, (51.35676168825242, 7.252991080488028)),
    ],
)
def test_gauss_kruger_convertor(
    right: float, height: float, expected: tuple[float, float]
) -> None:
    """
    Test the Gauss-Kruger convertor.

    Parameters
    ----------
    right : float
        The original right coordinate.
    height : float
        The original height coordinate.
    expected : tuple[float, float
        The expected converted latitude and longitude coordinate.
    """
    actual = convert_gk_to_lat_long(right, height)
    assert math.isclose(actual[0], expected[0])
    assert math.isclose(actual[1], expected[1])
