import json
import os
import tempfile
from pathlib import Path

import h5py
import pytest
import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.binary_extractor import BinaryExtractor
from paint.util.utils import to_utc_single


@pytest.mark.parametrize(
    "test_data_path, surface_header_name, facet_header_name, points_on_facet_struct_name",
    [
        (
            Path(
                f"{PAINT_ROOT}/tests/data/test_data/Helio_AA23_test_data_230918133925.binp"
            ),
            "=5f2I2f",
            "=i9fI",
            "=7f",
        ),
    ],
)
def test_binary_extractor(
    test_data_path: Path,
    surface_header_name: str,
    facet_header_name: str,
    points_on_facet_struct_name: str,
):
    """
    Test the binary extractor.

    This test extracts the deflectometry data to h5 and the heliostat properties to json and saves these files in a
    temporary directory. Then, we test if the appropriate keys are available and the shape of the data matches the
    expected shape.

    Parameters
    ----------
    test_data_path : str
        The path to the test binary file.
    surface_header_name : str
        The name for the surface header in the test binary file.
    facet_header_name : str
        The name for the facet header in the test binary file.
    points_on_facet_struct_name : str
        The name of the point on facet structure in the test binary file.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        file_name = (
            test_data_path.name.split("_")[1]
            + "_"
            + str(to_utc_single(test_data_path.name.split("_")[-1].split(".")[0]))
            + mappings.DEFLECTOMETRY_SUFFIX
        )
        json_handle = test_data_path.name.split("_")[1] + mappings.PROPERTIES_SUFFIX
        converter = BinaryExtractor(
            input_path=test_data_path,
            output_path=output_path,
            surface_header_name=surface_header_name,
            facet_header_name=facet_header_name,
            points_on_facet_struct_name=points_on_facet_struct_name,
        )
        converter.convert_to_h5_and_extract_properties()

        # check the HDF5 file
        file_path = Path(output_path, file_name)
        assert os.path.exists(file_path)

        # check the HDF5 file
        json_file_path = Path(output_path, json_handle)
        assert os.path.exists(json_file_path)

        # check the extracted heliostat properties are correct
        # Open the file and load the JSON data
        with open(json_file_path, "r") as file:
            data = json.load(file)
        assert data[mappings.NUM_FACETS] == 4
        assert data[mappings.DEFLECTOMETRY_CREATED_AT] == "230918133925"
        num_facets = data[mappings.NUM_FACETS]
        for i in range(num_facets):
            assert torch.tensor(
                data[mappings.FACETS_LIST][i][mappings.TRANSLATION_VECTOR]
            ).shape == torch.Size([3])
            assert torch.tensor(
                data[mappings.FACETS_LIST][i][mappings.CANTING_E]
            ).shape == torch.Size([3])
            assert torch.tensor(
                data[mappings.FACETS_LIST][i][mappings.CANTING_N]
            ).shape == torch.Size([3])

        # check the extracted deflectometry shapes are correct
        with h5py.File(file_path, "r") as file:
            for i in range(num_facets):
                assert torch.tensor(
                    file[f"{mappings.FACET_KEY}{i+1}"][mappings.SURFACE_NORMAL_KEY],
                    dtype=torch.float32,
                ).shape == torch.Size([80755, 3])
                assert torch.tensor(
                    file[f"{mappings.FACET_KEY}{i + 1}"][mappings.SURFACE_POINT_KEY],
                    dtype=torch.float32,
                ).shape == torch.Size([80755, 3])
