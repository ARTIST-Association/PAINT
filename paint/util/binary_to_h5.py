import struct
from pathlib import Path
from typing import Tuple, Union

import h5py
import torch


class BinaryToH5Converter:
    """
    Implement a converter that converts binary data to HDF5 format.

    Attributes
    ----------
    input_file_path : str
        The file path to the binary data file that will be converted.
    output_file_path : str
        The file path to save the converted h5 file.
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
        input_file_path: Union[str, Path],
        output_file_path: Union[str, Path],
        surface_header_name: str,
        facet_header_name: str,
        points_on_facet_struct_name: str,
    ) -> None:
        """
        Initialize the converter.

        Parameters
        ----------
        input_file_path : str
            The file path to the binary data file that will be converted.
        output_file_path : str
            The file path to save the converted h5 file.
        surface_header_name : str
            The name for the surface header in the binary file.
        facet_header_name : str
            The name for the facet header in the binary file.
        points_on_facet_struct_name : str
            The name of the point on facet structure in the binary file.
        """
        self.input_file_path = Path(input_file_path)
        self.output_file_path = Path(output_file_path)
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
    ) -> Tuple[int, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Convert binary data to h5 and extract heliostat properties not to be saved in the deflectometry file."""
        # Create structures for reading binary file correctly.
        surface_header_struct = struct.Struct(self.surface_header_name)
        facet_header_struct = struct.Struct(self.facet_header_name)
        points_on_facet_struct = struct.Struct(self.points_on_facet_struct_name)

        with open(f"{self.input_file_path}.binp", "rb") as file:
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

        # to maintain consistency we cast the west direction to east direction
        canting_e[:, 0] = -canting_e[:, 0]

        with h5py.File(self.output_file_path, "w") as file:
            # TODO Save h5py
            pass

        return number_of_facets, facet_translation_vectors, canting_e, canting_n
