#!/usr/bin/env python
import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Union

import h5py
import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT


class BinaryExtractor:
    """
    Implement an extractor that extracts data from a binary file and saves it to h5 and json.

    This extractor considers data form a binary file that contains deflectometry data and heliostat properties. The data
    is extracted and the deflectometry data saved in a h5 format and the heliostat properties as a json.

    Attributes
    ----------
    input_path : Path
        The file path to the binary data file that will be converted.
    output_path : Path
        The file path to save the converted h5 file.
    file_name : str
        The file name of the converted h5 file.
    save_properties : bool
        Whether to save the heliostat properties extracted from the binary file.
    json_handle : str
        The file path to save the json containing the heliostat properties data.
    deflectometry_created_at : str
        The time stamp for when the deflectometry data was created. Required for properties later.
    surface_header_name : str
        The name for the surface header in the binary file.
    facet_header_name : str
        The name for the facet header in the binary file.
    points_on_facet_struct_name : str
        The name of the point on facet structure in the binary file.

    Methods
    -------
    nwu_to_enu()
        Cast from an NWU to an ENU coordinate system.
    convert_to_h5_and_extract_properties()
        Convert binary data to h5 and extract heliostat properties not to be saved in the deflectometry file.
    """

    def __init__(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        surface_header_name: str,
        facet_header_name: str,
        points_on_facet_struct_name: str,
    ) -> None:
        """
        Initialize the extractor.

        Parameters
        ----------
        input_path : Union[str, Path]
            The file path to the binary data file that will be converted.
        output_path : Union[str, Path]
            The file path to save the converted h5 deflectometry file.
        surface_header_name : str
            The name for the surface header in the binary file.
        facet_header_name : str
            The name for the facet header in the binary file.
        points_on_facet_struct_name : str
            The name of the point on facet structure in the binary file.
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=True)
        name_string = self.input_path.name.split("_")
        if len(name_string) == 6:
            file_name = (
                name_string[1]
                + "_"
                + name_string[4]
                + "_"
                + name_string[-1].split(".")[0]
            )
            self.save_properties = False
        else:
            file_name = name_string[1] + "_" + name_string[-1].split(".")[0]
            self.save_properties = True
        self.file_name = file_name + mappings.DEFLECTOMETRY_SUFFIX
        self.json_handle = name_string[1] + mappings.PROPERTIES_SUFFIX
        self.deflectometry_created_at = self.input_path.name.split("_")[-1].split(".")[
            0
        ]
        self.surface_header_name = surface_header_name
        self.facet_header_name = facet_header_name
        self.points_on_facet_struct_name = points_on_facet_struct_name

    @staticmethod
    def nwu_to_enu(nwu_tensor: torch.Tensor) -> torch.Tensor:
        """
        Cast the coordinate system from NWU to ENU.

        Parameters
        ----------
        nwu_tensor : torch.Tensor
            The tensor in the NWU coordinate system.

        Returns
        -------
        torch.Tensor
            The converted tensor in the ENU coordinate system.
        """
        return torch.tensor(
            [-nwu_tensor[1], nwu_tensor[0], nwu_tensor[2]], dtype=torch.float
        )

    def convert_to_h5_and_extract_properties(
        self,
    ) -> None:
        """
        Extract data from a binary file and save the deflectometry measurements and heliostat properties.

        The binary files we consider, contain both deflectometry measurements and certain heliostat properties, such as
        the number of facets, the facet translation vectors, and the facet canting vectors. Therefore, the deflectometry
        measurements are extracted and saved as a h5 file, whilst the heliostat properties are extracted and saved in a
        json file.
        """
        # Create structures for reading binary file correctly.
        surface_header_struct = struct.Struct(self.surface_header_name)
        facet_header_struct = struct.Struct(self.facet_header_name)
        points_on_facet_struct = struct.Struct(self.points_on_facet_struct_name)

        with open(self.input_path, "rb") as file:
            surface_header_data = surface_header_struct.unpack_from(
                file.read(surface_header_struct.size)
            )
            # Load width and height.
            width, height = surface_header_data[3:5]

            # Calculate the number of facets.
            n_xy = surface_header_data[5:7]
            number_of_facets = int(n_xy[0] * n_xy[1])

            # Create empty tensors for storing data.
            facet_translation_vectors = torch.empty(number_of_facets, 3)
            canting_e = torch.empty(number_of_facets, 3)
            canting_n = torch.empty(number_of_facets, 3)
            surface_points_with_facets = torch.empty(0)
            surface_normals_with_facets = torch.empty(0)
            for f in range(number_of_facets):
                facet_header_data = facet_header_struct.unpack_from(
                    file.read(facet_header_struct.size)
                )

                facet_translation_vectors[f] = torch.tensor(
                    facet_header_data[1:4], dtype=torch.float
                )
                canting_n[f] = self.nwu_to_enu(
                    torch.tensor(
                        facet_header_data[4:7],
                        dtype=torch.float,
                    )
                )
                canting_e[f] = self.nwu_to_enu(
                    torch.tensor(
                        facet_header_data[7:10],
                        dtype=torch.float,
                    )
                )
                number_of_points = facet_header_data[10]
                if f == 0:
                    surface_points_with_facets = torch.empty(
                        number_of_facets, number_of_points, 3
                    )
                    surface_normals_with_facets = torch.empty(
                        number_of_facets, number_of_points, 3
                    )

                points_data = points_on_facet_struct.iter_unpack(
                    file.read(points_on_facet_struct.size * number_of_points)
                )
                for i, point_data in enumerate(points_data):
                    surface_points_with_facets[f, i, :] = torch.tensor(
                        point_data[:3], dtype=torch.float
                    )
                    surface_normals_with_facets[f, i, :] = torch.tensor(
                        point_data[3:6], dtype=torch.float
                    )

        # to maintain consistency, we cast the west direction to east direction
        canting_e[:, 0] = -canting_e[:, 0]

        # extract deflectometry data and save
        with h5py.File(self.output_path / self.file_name, "w") as file:
            for i in range(number_of_facets):
                facet = file.create_group(name=f"{mappings.FACET_KEY}{i+1}")
                facet.create_dataset(
                    name=f"{mappings.SURFACE_NORMAL_KEY}",
                    data=surface_normals_with_facets[i, :, :],
                )
                facet.create_dataset(
                    name=f"{mappings.SURFACE_POINT_KEY}",
                    data=surface_points_with_facets[i, :, :],
                )

        # extract heliostat properties data and save
        if self.save_properties:
            with open(self.output_path / self.json_handle, "w") as handle:
                properties = {
                    mappings.DEFLECTOMETRY_CREATED_AT: self.deflectometry_created_at,
                    mappings.NUM_FACETS: number_of_facets,
                    mappings.FACETS_LIST: [
                        {
                            mappings.TRANSLATION_VECTOR: facet_translation_vectors[
                                i, :
                            ].tolist(),
                            mappings.CANTING_E: canting_e[i, :].tolist(),
                            mappings.CANTING_N: canting_n[i, :].tolist(),
                        }
                        for i in range(number_of_facets)
                    ],
                }
                json.dump(properties, handle)


if __name__ == "__main__":
    # Simulate command-line arguments for testing or direct script execution
    sys.argv = [
        "binary_extractor.py",
        "--input_path",
        f"{PAINT_ROOT}/ExampleDataKIT/Helio_AY39_Rim0_STRAL-Input_230918133925.binp",
        "--output_path",
        f"{PAINT_ROOT}/ConvertedData",
        "--surface_header_name",
        "=5f2I2f",
        "--facet_header_name",
        "=i9fI",
        "--points_on_facet_struct_name",
        "=7f",
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path", type=Path, help="Path to the binary input file."
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Path to save the output files",
    )
    parser.add_argument(
        "--surface_header_name",
        type=str,
        help="The header of the surface struct",
    )
    parser.add_argument(
        "--facet_header_name",
        type=str,
        help="The header of the facet struct",
    )
    parser.add_argument(
        "--points_on_facet_struct_name",
        type=str,
        help="The header of the points on the facet struct",
    )
    args = parser.parse_args()
    converter = BinaryExtractor(
        input_path=args.input_path,
        output_path=args.output_path,
        surface_header_name=args.surface_header_name,
        facet_header_name=args.facet_header_name,
        points_on_facet_struct_name=args.points_on_facet_struct_name,
    )
    converter.convert_to_h5_and_extract_properties()
