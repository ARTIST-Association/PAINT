import os
import tempfile
from pathlib import Path

import h5py
import numpy as np

import paint.preprocessing.juelich_weather_mappings as juelich_weather_mappings
from paint import PAINT_ROOT
from paint.preprocessing.juelich_weather_converter import JuelichWeatherConverter


def test_juelich_weather_convertor():
    """
    Test the Juelich weather convertor.

    This test merges two text files saved as test data and generates the resulting Juelich weather HDF5. This file is
    then compared to an existing HDF5 also saved in the test data folder.
    """
    # Load the expected HDF5 file.
    expected_hdf5_file = (
        f"{PAINT_ROOT}/tests/preprocessing/test_data/2021-01-juelich-weather.h5"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        file_name = "2021-01-juelich-weather.h5"

        # Define and run weather converter.
        weather_converter = JuelichWeatherConverter(
            input_root_dir=f"{PAINT_ROOT}/tests/preprocessing/test_data/juelich_weather",
            output_path=output_path,
        )
        _ = weather_converter.merge_and_save_to_hdf5()

        # Check the HDF5 file exists.
        file_path = Path(output_path, file_name)
        assert os.path.exists(file_path)

        # Check the content of the HDF5 file.
        with (
            h5py.File(file_path, "r") as output,
            h5py.File(expected_hdf5_file, "r") as expected,
        ):
            # Check all keys are present.
            assert all(key in expected.keys() for key in output.keys())

            # Go through keys and check the contents are the same.
            for key in output.keys():
                assert np.array_equal(output[key][:], expected[key][:])

                # For all keys apart from time, check the attributes are correct.
                if key != "time":
                    assert np.array_equal(
                        output[key].attrs[juelich_weather_mappings.DESCRIPTION],
                        expected[key].attrs[juelich_weather_mappings.DESCRIPTION],
                    )
                    assert np.array_equal(
                        output[key].attrs[juelich_weather_mappings.UNITS],
                        expected[key].attrs[juelich_weather_mappings.UNITS],
                    )
