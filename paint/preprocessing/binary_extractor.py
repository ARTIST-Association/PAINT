import struct
from pathlib import Path

import h5py
import torch

import paint.util.paint_mappings as mappings
from paint.util.utils import to_utc_single


class BinaryExtractor:
    """
    Implement an extractor that extracts data from a binary file and saves it to h5.

    This extractor considers data from a binary file containing deflectometry data and heliostat properties. The data
    is extracted and only the deflectometry data is saved in an h5 file.

    Attributes
    ----------
    input_path : Path
        The file path to the binary data file that will be converted.
    output_path : Path
        The file path to save the converted h5 file.
    file_name : str
        The file name of the converted h5 file.
    raw_data : bool
        Whether the raw data or filled data is extracted.
    heliostat_id : str
        The heliostat ID of the heliostat considered in the binary file.
    json_handle : str
        The file path to save the json containing the heliostat properties data.
    deflectometry_created_at : str
        The time stamp for when the deflectometry data was created. Required for properties later.
    deflectometry_created_at_file_name : str
        The time stamp in the file name format for when the deflectometry data was created. Required for saving
        different files later.
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
    convert_to_h5()
        Convert binary data to h5.
    """

    def __init__(
        self,
        input_path: str | Path,
        output_path: str | Path,
        surface_header_name: str,
        facet_header_name: str,
        points_on_facet_struct_name: str,
    ) -> None:
        """
        Initialize the extractor.

        Parameters
        ----------
        input_path : str | Path
            The file path to the binary data file that will be converted.
        output_path : str | Path
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
        name_string = self.input_path.name.split("_")
        if len(name_string) == 6:
            file_name = (
                name_string[1]
                + "-"
                + name_string[4]
                + "-"
                + str(
                    to_utc_single(name_string[-1].split(".")[0], file_name_format=True)
                )
            )
            self.raw_data = False
        else:
            file_name = (
                name_string[1]
                + "-"
                + str(
                    to_utc_single(name_string[-1].split(".")[0], file_name_format=True)
                )
            )
            self.raw_data = True
        self.heliostat_id = name_string[1]
        self.file_name = file_name + mappings.DEFLECTOMETRY_SUFFIX
        self.json_handle = name_string[1] + mappings.FACET_PROPERTIES_SUFFIX
        self.deflectometry_created_at = to_utc_single(name_string[-1].split(".")[0])
        self.deflectometry_created_at_file_name = to_utc_single(
            name_string[-1].split(".")[0], file_name_format=True
        )
        self.surface_header_name = surface_header_name
        self.facet_header_name = facet_header_name
        self.points_on_facet_struct_name = points_on_facet_struct_name

    def convert_to_h5(
        self,
    ) -> None:
        """Extract data from a binary file and save the deflectometry measurements."""
        # Create structures for reading binary file correctly.
        surface_header_struct = struct.Struct(self.surface_header_name)
        facet_header_struct = struct.Struct(self.facet_header_name)
        points_on_facet_struct = struct.Struct(self.points_on_facet_struct_name)

        with open(self.input_path, "rb") as file:
            surface_header_data = surface_header_struct.unpack_from(
                file.read(surface_header_struct.size)
            )

            # Calculate the number of facets.
            n_xy = surface_header_data[5:7]
            number_of_facets = int(n_xy[0] * n_xy[1])

            # Create empty tensors for storing data.
            _unused_facet_translation_vectors = torch.empty(number_of_facets, 3)
            _unused_canting_e = torch.empty(number_of_facets, 3)
            _unused_canting_n = torch.empty(number_of_facets, 3)
            surface_points_with_facets = []
            surface_normals_with_facets = []
            for f in range(number_of_facets):
                facet_header_data = facet_header_struct.unpack_from(
                    file.read(facet_header_struct.size)
                )

                _unused_facet_translation_vectors[f] = torch.tensor(
                    facet_header_data[1:4], dtype=torch.float
                )
                _unused_canting_e[f] = torch.tensor(
                    facet_header_data[4:7],
                    dtype=torch.float,
                )
                _unused_canting_n[f] = torch.tensor(
                    facet_header_data[7:10],
                    dtype=torch.float,
                )
                number_of_points = facet_header_data[10]
                single_facet_surface_points = torch.empty(number_of_points, 3)
                single_facet_surface_normals = torch.empty(number_of_points, 3)

                points_data = points_on_facet_struct.iter_unpack(
                    file.read(points_on_facet_struct.size * number_of_points)
                )
                for i, point_data in enumerate(points_data):
                    single_facet_surface_points[i, :] = torch.tensor(
                        point_data[:3], dtype=torch.float
                    )
                    single_facet_surface_normals[i, :] = torch.tensor(
                        point_data[3:6], dtype=torch.float
                    )
                surface_points_with_facets.append(single_facet_surface_points)
                surface_normals_with_facets.append(single_facet_surface_normals)

        # Extract deflectometry data and save.
        saved_deflectometry_path = (
            Path(self.output_path)
            / self.heliostat_id
            / mappings.SAVE_DEFLECTOMETRY
            / self.file_name
        )
        saved_deflectometry_path.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(saved_deflectometry_path, "w") as file:
            for i in range(number_of_facets):
                facet = file.create_group(name=f"{mappings.FACET_KEY}{i + 1}")
                facet.create_dataset(
                    name=f"{mappings.SURFACE_NORMAL_KEY}",
                    data=surface_normals_with_facets[i],
                )
                facet.create_dataset(
                    name=f"{mappings.SURFACE_POINT_KEY}",
                    data=surface_points_with_facets[i],
                )
