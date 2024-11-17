#!/usr/bin/env python
import argparse
import json
import logging
import tempfile
from pathlib import Path

import requests
import torch

from paint import PAINT_ROOT
from paint.data.stac_client import StacClient
from paint.preprocessing.focal_spot_extractor import detect_focal_spot
from paint.preprocessing.target_cropper import crop_image_with_template_matching

# Configure the logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Function to download and load the checkpoint
def load_model_from_url(url):
    """
    Download the model checkpoint from the given URL and load it directly without storing it permanently.

    Parameters
    ----------
    url : str
        The URL of the model checkpoint.

    Returns
    -------
    torch.jit.ScriptModule
        The loaded PyTorch model.

    Raises
    ------
    Exception
        If the model cannot be loaded or the download fails.
    """
    logger.info(f"Downloading checkpoint from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        logger.info("Checkpoint downloaded successfully. Loading the model...")
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            try:
                model = torch.jit.load(temp_file.name, map_location="cpu")
                logger.info("Model loaded successfully.")
                return model
            except Exception as e:
                logger.error(f"Failed to load the model: {e}")
                raise
    else:
        logger.error(
            f"Failed to download the checkpoint. Status code: {response.status_code}"
        )
        response.raise_for_status()


def main():
    """
    Process calibration data for heliostats.

    This function:
    - Parses command-line arguments.
    - Downloads and processes heliostat calibration data.
    - Loads the UTIS model from a given URL.
    - Detects focal spots for specified heliostats and measurements.

    Command-line Arguments
    -----------------------
    --output_dir : str
        Path to save the downloaded data. Default is `PAINT_ROOT/download_test`.
    --heliostats : str
        List of heliostats to be downloaded. Default is ["AA23"].
    --collections : str
        List of collections to be downloaded. Default is ["calibration"].
    --filtered_calibration : str
        List of calibration items to download. Default is ["raw_image", "calibration_properties"].
    --measurement_id : str
        ID(s) of the measurement to apply the algorithm. Default is ["123819"].

    Raises
    ------
    FileNotFoundError
        If a required calibration file is missing.
    Exception
        If an error occurs during focal spot detection.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Process calibration data for heliostats."
    )
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

    # Load the UTIS model directly from the URL
    model_url = (
        "https://github.com/DLR-SF/UTIS-HeliostatBeamCharacterization/"
        "raw/main/trained_models/utis_model_scripted.pt"
    )
    loaded_model = load_model_from_url(model_url)

    # Process each heliostat and its measurements
    for heliostat in args.heliostats:
        measurement_ids = args.measurement_id

        for measurement_id in measurement_ids:
            # Define paths for current measurement
            image_path = (
                output_dir / heliostat / "Calibration" / f"{measurement_id}_raw.png"
            )
            calibration_properties_path = (
                output_dir
                / heliostat
                / "Calibration"
                / f"{measurement_id}-calibration-properties.json"
            )

            # Extract target from calibration properties
            with open(calibration_properties_path, "r") as file:
                calibration_data = json.load(file)
            target = calibration_data["target_name"]

            # Crop the image using template matching
            cropped_image = crop_image_with_template_matching(
                image_path, target, n_grid=256
            )

            # Convert to grayscale by using only green color channel and convert to torch tensor
            cropped_image_tensor = (
                torch.tensor(cropped_image[:, :, 1], dtype=torch.float32) / 255.0
            )

            # Detect focal spot
            focal_spot = detect_focal_spot(cropped_image_tensor, target, loaded_model)

            # Print the detected aim point
            logger.info(
                "Heliostat %s: For Measurement %s, Focal Spot detected at %s.",
                heliostat,
                measurement_id,
                focal_spot.aim_point.tolist(),
            )

            # TODO: Write results to CSV or database?


if __name__ == "__main__":
    main()
