#!/usr/bin/env python
import json
import argparse
from pathlib import Path

import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.preprocessing.focal_spot_extractor import detect_focal_spot
from paint.preprocessing.target_cropper import crop_image_with_template_matching


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process calibration data for heliostats.")
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to save the downloaded data.",
        default=f"{PAINT_ROOT}/download_test",
    )
    parser.add_argument(
        "--heliostats",
        type=str,
        help="List of heliostats to be downloaded.",
        nargs="+",
        default=["AA23"],
    )
    parser.add_argument(
        "--collections",
        type=str,
        help="List of collections to be downloaded.",
        nargs="+",
        default=["calibration"],
    )
    parser.add_argument(
        "--filtered_calibration",
        type=str,
        help="List of calibration items to download.",
        nargs="+",
        default=["raw_image", "calibration_properties"],
    )
    parser.add_argument(
        "--measurement_id",
        type=str,
        help="ID(s) of the measurement to apply the algorithm.",
        nargs="+",
        default=["123819"],
    )
    args = parser.parse_args()

    # Ensure the output directory is a Path object
    output_dir = Path(args.output_dir)

    # Create STAC client and download heliostat data
    client = StacClient(output_dir=output_dir)
    client.get_heliostat_data(
        heliostats=args.heliostats,
        collections=args.collections,
        filtered_calibration_keys=args.filtered_calibration,
    )

    # Load the UTIS model for target image segmentation
    model_path = Path(PAINT_ROOT) / "paint/preprocessing/models/utis_model_scripted.pt"
    loaded_model = torch.jit.load(model_path, map_location="cpu")

    # Process each heliostat and its measurements
    for heliostat in args.heliostats:
        # TODO: Replace hardcoded measurement_ids with dynamic retrieval of available IDs
        measurement_ids = args.measurement_id

        for measurement_id in measurement_ids:
            # Define paths for current measurement
            image_path = output_dir / heliostat / "Calibration" / f"{measurement_id}_raw.png"
            calibration_properties_path = output_dir / heliostat / "Calibration" / f"{measurement_id}-calibration-properties.json"

            # Extract target from calibration properties
            with open(calibration_properties_path, "r") as file:
                calibration_data = json.load(file)
            target = calibration_data["target_name"]

            # Crop the image using template matching
            cropped_image = crop_image_with_template_matching(
                image_path, target, n_grid=256
            )
            
            # Convert to grayscale by using only green color channel and convert to torch tensor
            cropped_image_tensor = torch.tensor(cropped_image[:, :, 1], dtype=torch.float32) / 255.0

            # Detect focal spot
            focal_spot = detect_focal_spot(cropped_image_tensor, target, loaded_model)

            # Print the detected aim point
            print(
                f"Heliostat {heliostat}: For Measurement {measurement_id}, "
                f"Focal Spot detected at {focal_spot.aim_point.tolist()}."
            )

            # TODO: Write results to CSV or database?


if __name__ == "__main__":
    main()
