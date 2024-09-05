import math
from typing import Tuple

import pytest

from paint.util.gauss_kruger_convertor import convert_gk_to_lat_long


@pytest.mark.parametrize(
    "right, height, expected",
    [
        (2527321, 5642083, (50.91338551710208, 6.387849990173632)),
        (2587321, 5692083, (51.35676539020598, 7.252958250006098)),
    ],
)
def test_gauss_kruger_convertor(
    right: float, height: float, expected: Tuple[float, float]
) -> None:
    """
    Test the Gauss-Kruger convertor.

    Parameters
    ----------
    right : float
        The original right coordinate.
    height : float
        The original height coordinate.
    expected : Tuple[float, float
        The expected converted latitude and longitude coordinate.
    """
    actual = convert_gk_to_lat_long(right, height)
    assert math.isclose(actual[0], expected[0])
    assert math.isclose(actual[1], expected[1])
