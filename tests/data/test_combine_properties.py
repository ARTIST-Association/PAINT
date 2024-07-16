import argparse
import json
import tempfile
from pathlib import Path

from paint import PAINT_ROOT
from paint.data.combine_properties import create_heliostat_properties_json

expected = {
    "number_of_facets": 4,
    "facets": [
        {
            "translation_vector": [
                -0.8075000047683716,
                0.6424999833106995,
                0.040198374539613724,
            ],
            "canting_e": [
                0.6374922394752502,
                1.9569215510273352e-05,
                0.0031505227088928223,
            ],
            "canting_n": [-0.0, 0.8024845123291016, -0.004984567407518625],
        },
        {
            "translation_vector": [
                0.8075000047683716,
                0.6424999833106995,
                0.040198374539613724,
            ],
            "canting_e": [
                0.6374922394752502,
                -1.9569215510273352e-05,
                0.0031505227088928223,
            ],
            "canting_n": [-0.0, 0.8024845123291016, 0.004984567407518625],
        },
        {
            "translation_vector": [
                -0.8075000047683716,
                -0.6424999833106995,
                0.040198374539613724,
            ],
            "canting_e": [
                0.6374922394752502,
                -1.9569215510273352e-05,
                -0.0031505227088928223,
            ],
            "canting_n": [-0.0, 0.8024845123291016, -0.004984567407518625],
        },
        {
            "translation_vector": [
                0.8075000047683716,
                -0.6424999833106995,
                0.040198374539613724,
            ],
            "canting_e": [
                0.6374922394752502,
                1.9569215510273352e-05,
                -0.0031505227088928223,
            ],
            "canting_n": [-0.0, 0.8024845123291016, 0.004984567407518625],
        },
    ],
    "kinematic": {
        "Type_axis_1": "LINEAR",
        "MinCounts_axis_1": 0,
        "MaxCounts_axis_1": 69296,
        "PulseRatio_axis_1": 154166.66666666666,
        "A_axis_1": 0,
        "B_axis_1": 0.0750053113225499,
        "C_axis_1": 0.335308,
        "D_axis_1": 0.338095,
        "E_axis_1": 0,
        "Reversed_axis_1": 0,
        "AngleK_axis_1": 0.0058429526185208,
        "AngleMin_axis_1": 0.0044348817318677,
        "AngleMax_axis_1": 1.5707963267948966,
        "AngleW_axis_1": 0.025,
        "Type_axis_2": "LINEAR",
        "MinCounts_axis_2": 0,
        "MaxCounts_axis_2": 75451,
        "PulseRatio_axis_2": 154166.66666666666,
        "A_axis_2": 0,
        "B_axis_2": 0.0788874149969901,
        "C_axis_2": 0.340771,
        "D_axis_2": 0.3191,
        "E_axis_2": 0,
        "Reversed_axis_2": 1,
        "AngleK_axis_2": 0.9397207629980034,
        "AngleMin_axis_2": -0.95993,
        "AngleMax_axis_2": 0.929079209450228,
        "AngleW_axis_2": 0.025,
    },
}


def test_combine_properties():
    """
    Test the combine properties function.

    In this test sample data for one heliostat is combined and we test to see it is the same as the expected dictionary
    listed as a global variable.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir)
        args = argparse.Namespace(
            input_position=f"{PAINT_ROOT}/tests/data/test_data/test_positions.xlsx",
            input_axis=f"{PAINT_ROOT}/tests/data/test_data/test_axis_data.csv",
            input_facet_root=f"{PAINT_ROOT}/tests/data/test_data/",
            output=output_path,
        )

        create_heliostat_properties_json(args)

        with open(output_path / "AA23_properties.json", "r") as handle:
            data = json.load(handle)
        assert data == expected
