import os
import tempfile
from pathlib import Path

import h5py
import pytest
import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.preprocessing.binary_extractor import BinaryExtractor
from paint.util.utils import to_utc_single


@pytest.mark.parametrize(
    "test_data_path, surface_header_name, facet_header_name, points_on_facet_struct_name",
    [
        (
            Path(
                f"{PAINT_ROOT}/tests/preprocessing/test_data/Helio_AA23_test_data_230918133925.binp"
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
            + "-"
            + str(to_utc_single(test_data_path.name.split("_")[-1].split(".")[0]))
            + mappings.DEFLECTOMETRY_SUFFIX
        )
        converter = BinaryExtractor(
            input_path=test_data_path,
            output_path=output_path,
            surface_header_name=surface_header_name,
            facet_header_name=facet_header_name,
            points_on_facet_struct_name=points_on_facet_struct_name,
        )
        converter.convert_to_h5()

        # check the HDF5 file
        file_path = (
            Path(output_path)
            / converter.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / file_name
        )
        assert os.path.exists(file_path)

        # Check the extracted deflectometry shapes are correct.
        with h5py.File(file_path, "r") as file:
            for i in range(4):
                assert torch.tensor(
                    file[f"{mappings.FACET_KEY}{i+1}"][mappings.SURFACE_NORMAL_KEY],
                    dtype=torch.float32,
                ).shape == torch.Size([80755, 3])
                assert torch.tensor(
                    file[f"{mappings.FACET_KEY}{i + 1}"][mappings.SURFACE_POINT_KEY],
                    dtype=torch.float32,
                ).shape == torch.Size([80755, 3])
