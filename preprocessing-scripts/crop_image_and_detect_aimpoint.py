#!/usr/bin/env python
import argparse
import json
import tempfile
from pathlib import Path

import requests
import torch

import paint.util.paint_mappings as mappings
from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.preprocessing.focal_spot_extractor import detect_focal_spot
from paint.preprocessing.target_cropper import crop_image_with_template_matching


def load_model_from_url(url: str) -> torch.jit.ScriptModule:
    """
    Download the model checkpoint from the given URL and load it directly without storing it permanently.

    Parameters
    ----------
    url : str
        URL of the model checkpoint.

    Returns
    -------
    torch.jit.ScriptModule
        Loaded PyTorch model.

    Raises
    ------
    Exception
        If the model cannot be loaded or the download fails.
    """
    print(f"Downloading checkpoint from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print("Checkpoint downloaded successfully. Loading the model...")
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            try:
                model = torch.jit.load(temp_file.name, map_location="cpu")
                print("Model loaded successfully.")
                return model
            except Exception as e:
                print(f"Failed to load the model: {e}")
                raise
    else:
        print(f"Failed to download the checkpoint. Status code: {response.status_code}")
        response.raise_for_status()


def main(args: argparse.Namespace) -> None:
    """
    Process calibration images and extract focal spots using UTIS.

    This function downloads and processes heliostat calibration data before loading the UTIS model from a given URL.
    It then applies UTIS to detect focal spots for specified heliostats and measurement IDs.
    """
    # Base directory for all outputs
    output_dir = Path(args.output_dir)

    # Subdirectories for specific types of outputs
    downloaded_data_dir = output_dir / "downloaded_data"
    extracted_focal_spots_dir = output_dir / "extracted_focal_spots"

    # Create STAC client and download heliostat data.
    client = StacClient(output_dir=downloaded_data_dir)

    # Load the UTIS model directly from the URL.
    loaded_model = load_model_from_url(mappings.UTIS_MODEL_CHECKPOINT)

    # Load single measurement.
    client.get_single_calibration_item_by_id(
        heliostat_id=args.heliostat,
        item_id=args.measurement_id,
        filtered_calibration_keys=args.filtered_calibration,
    )

    # Define paths for current measurement.
    image_path = (
        downloaded_data_dir
        / args.heliostat
        / mappings.SAVE_CALIBRATION
        / f"{args.measurement_id}_raw.png"
    )
    calibration_properties_path = (
        downloaded_data_dir
        / args.heliostat
        / mappings.SAVE_CALIBRATION
        / f"{args.measurement_id}-calibration-properties.json"
    )

    # Extract target from calibration properties.
    with open(calibration_properties_path, "r") as file:
        calibration_data = json.load(file)
    target = calibration_data[mappings.TARGET_NAME_KEY]

    # Crop the image using template matching.
    cropped_image = crop_image_with_template_matching(image_path, target, n_grid=256)

    # Convert to grayscale by using only green color channel and convert to torch tensor.
    cropped_image_tensor = (
        torch.tensor(cropped_image[:, :, 1], dtype=torch.float32) / 255.0
    )

    # Detect focal spot.
    focal_spot = detect_focal_spot(cropped_image_tensor, target, loaded_model)

    # Log the detected aim point.
    print(
        "Heliostat %s: For Measurement %s, Focal Spot detected at %s.",
        args.heliostat,
        args.measurement_id,
        focal_spot.aim_point.tolist(),
    )

    # Save focal spot.
    focal_spot_path = (
        extracted_focal_spots_dir / f"{args.heliostat}_{args.measurement_id}_focal_spot"
    )
    focal_spot_path.parent.mkdir(parents=True, exist_ok=True)
    focal_spot.save(focal_spot_path)


if __name__ == "__main__":
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description="Process calibration data for heliostats."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Base path to save outputs. Downloaded data and extracted focal spots will be saved in separate subdirectories.",
        default=f"{PAINT_ROOT}/outputs",
    )
    parser.add_argument(
        "--heliostat",
        type=str,
        help="Heliostat to be downloaded.",
        nargs="+",
        default="AA23",
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
        type=int,
        help="ID of the measurement to apply the algorithm.",
        nargs="+",
        default=123819,
    )
    arguments = parser.parse_args()
    main(arguments)
