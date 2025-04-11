import argparse

import pandas as pd
import pytest

from paint import PAINT_ROOT
from paint.util.preprocessing import (
    load_and_format_heliostat_axis_data,
    load_and_format_heliostat_positions,
    merge_and_sort_df,
)


@pytest.fixture
def preprocessing_arguments() -> argparse.Namespace:
    """
    Make a fixture simulating the command line arguments required for testing the preprocessing functions.

    Returns
    -------
    argparse.Namespace
        The simulated command line arguments as a test fixture.
    """
    args = argparse.Namespace(
        input_position=f"{PAINT_ROOT}/tests/util/test_data/test_positions.csv",
        input_axis=f"{PAINT_ROOT}/tests/util/test_data/test_axis_data.csv",
    )
    return args


def test_preprocessing(preprocessing_arguments: argparse.Namespace) -> None:
    """
    Test the preprocessing functions.

    Parameters
    ----------
    preprocessing_arguments : argparse.Namespace
        The simulated command line arguments.
    """
    expected_data = {
        "HeliostatId": ["AA23"],
        "CreatedAt": ["2021-07-20 07:09:29"],
        "East": [-57.2],
        "North": [25],
        "Altitude": [88.711],
        "FieldId": [1],
        "Type_axis_1": ["LINEAR"],
        "MinCounts_axis_1": [0],
        "MaxCounts_axis_1": [69296],
        "PulseRatio_axis_1": [154166.66666666666],
        "A_axis_1": [0],
        "B_axis_1": [0.0750053113225499],
        "C_axis_1": [0.335308],
        "D_axis_1": [0.338095],
        "E_axis_1": [0],
        "Reversed_axis_1": [0],
        "AngleK_axis_1": [0.0058429526185208],
        "AngleMin_axis_1": [0.0044348817318677],
        "AngleMax_axis_1": [1.5707963267948966],
        "AngleW_axis_1": [0.025],
        "Type_axis_2": ["LINEAR"],
        "MinCounts_axis_2": [0],
        "MaxCounts_axis_2": [75451],
        "PulseRatio_axis_2": [154166.66666666666],
        "A_axis_2": [0],
        "B_axis_2": [0.0788874149969901],
        "C_axis_2": [0.340771],
        "D_axis_2": [0.3191],
        "E_axis_2": [0],
        "Reversed_axis_2": [1],
        "AngleK_axis_2": [0.9397207629980034],
        "AngleMin_axis_2": [-0.95993],
        "AngleMax_axis_2": [0.929079209450228],
        "AngleW_axis_2": [0.025],
    }
    expected_df = pd.DataFrame(expected_data)
    expected_df.set_index("HeliostatId", inplace=True)

    df_axis = load_and_format_heliostat_axis_data(preprocessing_arguments)
    df_position = load_and_format_heliostat_positions(preprocessing_arguments)
    df = merge_and_sort_df(df_heliostat_positions=df_position, df_axis=df_axis)

    assert df.equals(expected_df)
