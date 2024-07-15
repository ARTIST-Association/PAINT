import os
import tempfile
from pathlib import Path

import h5py
import pytest
import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.util.binary_to_h5 import BinaryToH5Converter


@pytest.mark.parametrize(
    "test_data_path, surface_header_name, facet_header_name, points_on_facet_struct_name",
    [
        (f"{PAINT_ROOT}/tests/util/binary_test_data.binp", "=5f2I2f", "=i9fI", "=7f"),
    ],
)
def test_binary_to_h5(
    test_data_path: str,
    surface_header_name: str,
    facet_header_name: str,
    points_on_facet_struct_name: str,
):
    """
    Test the binary to h5 converter.

    This test converts a test binary file to h5 and saves this file in a temporary directory. Then, we test if the
    appropriate keys are available and the shape of the data matches the expected shape.

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
        file_name = "test_converter.h5"
        converter = BinaryToH5Converter(
            input_path=test_data_path,
            output_path=output_path,
            file_name=file_name,
            surface_header_name=surface_header_name,
            facet_header_name=facet_header_name,
            points_on_facet_struct_name=points_on_facet_struct_name,
        )
        (
            num_facets,
            translation_vectors,
            canting_e,
            canting_n,
        ) = converter.convert_to_h5_and_extract_properties()

        # check the HDF5 file
        file_path = Path(output_path, file_name)
        assert os.path.exists(file_path)

        # check the extracted heliostat properties are correct
        assert num_facets == 4
        assert translation_vectors.shape == torch.Size([4, 3])
        assert canting_e.shape == torch.Size([4, 3])
        assert canting_n.shape == torch.Size([4, 3])

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
