<p align="center">
  <a href="https://paint-database.org" target="_blank">
    <img src="logo.svg" alt="logo" width="450"/>
  </a>
</p>

# PAINT

[![](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![](https://img.shields.io/badge/Contact-artist%40lists.kit.edu-blue?label=Contact)](artist@lists.kit.edu)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B%20%20%E2%97%8F%20%20%E2%97%8B-orange)](https://fair-software.eu)
[![codecov](https://codecov.io/gh/ARTIST-Association/PAINT/graph/badge.svg?token=B2pjCVgOhc)](https://codecov.io/gh/ARTIST-Association/PAINT)

## Welcome to ``PAINT``

This repository contains code associated with the [PAINT database](https://paint-database.org). The ``PAINT`` database
makes operational data of concentrating solar power plants available in accordance with the FAIR data principles, i.e.,
making them findable, accessible, interoperable, and reusable. Currently, the data encompasses calibration images,
deflectometry measurements, kinematic settings, and weather information of the concentrating solar power plant in
Jülich, Germany, with the global power plant id (GPPD) WRI1030197. Metadata for all database entries follows the
spatio-temporal asset catalog (STAC) standard.

## What can this repository do for you?

This repository contains two main types of code:
1. **Preprocessing:** This code was used to preprocess the data and extract all metadata into the STAC format. This
preprocessing included moving and renaming files to be in the correct structure, converting coordinates to the WGS84
format, and generating all STAC files (items, collections, and catalogs). This code is found in the subpackage
``paint.preprocessing`` and executed in the scripts located in ``preprocessing-scripts``. This code could be useful if
you have similar data that you would also like to process and include in the ``PAINT`` database!
2. **Data Access and Usage:** This code enables data from the ``PAINT`` database to be easily accessed from a code-base
and applied for a specific use case. Specifically, we provide a ``StacClient`` for browsing the STAC metadata files in
the ``PAINT`` database and downloading specific files. Furthermore, we provide utilities to generate custom benchmarks
for evaluating various calibration algorithms and also a ``torch.Dataset`` for efficiently loading and using calibration
data. This code is found in the subpackage ``paint.data`` and examples of possible execution are found in the
``scripts`` folder.

In the following, we will highlight how to use the code in more detail!

### Installation
We heavily recommend installing the `PAINT` package in a dedicated `Python3.9+` virtual environment. You can
install ``PAINT`` directly from the GitHub repository via:
```bash
pip install git+https://github.com/ARTIST-Association/PAINT
```
Alternatively, you can install ``PAINT`` locally. To achieve this, there are two steps you need to follow:
1. Clone the `PAINT` repository:
   ```bash
   git clone https://github.com/ARTIST-Association/PAINT.git
   ```
2. Install the package from the main branch:
   - Install basic dependencies: ``pip install .``
   - If you want to develop paint, install an editable version with developer dependencies: ``pip install -e ".[dev]"``

### Structure
The ``PAINT`` repository is structured as shown below:
```
.
├── html # Code for the paint-database.org website
├── markers # Saved markers for the WRI1030197 power plant in Jülich
├── paint # Python package
│   ├── data
│   ├── preprocessing
│   └── util
├── plots # Scripts used to generate plots found in our paper
├── preprocessing-scripts # Scripts used for preprocessing and STAC generation
├── scripts # Scripts highlighting example usage of the data
└── test # Tests for the python package
    ├── data
    ├── preprocessing
    └── util
```

### Example usage: ``StacClient``
The ``StacClient`` provides a simple way of browsing and downloading data from the
[PAINT database](https://paint-database.org) directly within a python program. The `StacClient` we provide is based on
`pystac`, however, we have included a few wrapper functions tailored for the [PAINT database](https://paint-database.org).

An example of how to use the `StacClient` is found in [this example script](scripts/example_stac_client.py). In this
script, we first initialize the ``StacClient``:
```python
client = StacClient(output_dir=args.output_dir)
```
The `StacClient` includes built in functions to automatically download the tower measurements for the power plant with
the global id WRI1030197 in Jülich, or weather data from the DWD or Jülich for a desired period of time:
```python
# Download tower measurements.
 client.get_tower_measurements()

 # Download weather data between a certain time period.
 client.get_weather_data(
     data_sources=args.weather_data_sources,
     start_date=datetime.strptime(args.start_date, mappings.TIME_FORMAT),
     end_date=datetime.strptime(args.end_date, mappings.TIME_FORMAT),
 )
```
The most useful function enables data from one or more heliostats to be downloaded:
```python
# Download heliostat data.
 client.get_heliostat_data(
     heliostats=args.heliostats,
     collections=args.collections,
     filtered_calibration_keys=args.filtered_calibration,
    )
```
Here the arguments are important:
- ``heliostats`` - this is a list of heliostats or `None`. If `None` is provided, then data for all heliostats will be
downloaded.
- ``collections`` - this indicates from which STAC collections data should be downloaded. These collections include
calibration data, deflectometry measurements, and heliostat properties. If ``None`` is provided, then data for all
collections will be downloaded.
- ``filtered_calibration_keys`` - the calibration collection includes multiple items, i.e. raw images, cropped images,
flux images, flux centered images, and calibration properties. With this argument it is possible to decide which items
will be downloaded. If ``None`` is provided, then data for all items will be downloaded.

Finally, if you are only interested in the metadata to do some more in depth data exploration or generate plots then you
can download the heliostat metadata with the following function:
```python
# Download metadata for all heliostats.
 client.get_heliostat_metadata(heliostats=None)
```
Of course this `StacClient` doesn't cover all possible use cases - but with the code provided we hope to give you enough
information to write your own extensions if required!

### Example usage: ``DatasetSplitter``
The ``DatasetSplitter`` class is used to create benchmark dataset splits. When working with calibration data and
developing alignment algorithms to optimize performance, it is important that the train, test, and validation data are
diverse. Currently, there is no standard to benchmark different algorithms and part of the ``PAINT`` project is to
provide this standard. Therefore, we include methods for generating benchmark splits, that can then be used for a
standardized evaluation process. We currently provide support for the following splits:
- **Azimuth Split:** This splits the data based on the azimuth of the sun for each considered calibration sample. For a
single heliostat, the ``training_size`` indices with the smallest azimuth values are selected for the training split,
while the ``validation_size`` indices with the largest values are selected for the validation split. The remaining
indices are assigned to the test split. This ensures that indices with very different azimuth values are considered in
the train and validation samples, i.e., the train and validation splits should contain very different samples. This
difference leads to a high level of difficulty and should guarantee that the trained calibration method is robust.
- **Solstice Split:** This splits the data based on the time of the year, more specifically, how close the measurement
date was to the winter or summer solstice. Specifically, for a single heliostat, the ``training_size`` indices closest
to the winter solstice are selected for the training split, while the ``validation_size`` indices closest to the summer
solstice are selected for the validation split. The remaining indices are assigned to the test split. This ensures that
indices from very different seasons, i.e. different conditions, are considered in training and validation, i.e., the
train and validation splits should contain very different samples. This difference leads to a high level of difficulty
and should guarantee that the trained calibration method is robust.

The [example dataset splits script](scripts/example_dataset_splits.py) provides an example of how to use the ``DatasetSplitter``.
To generate splits we first initialize the class with an ``input_file`` that contains the path to the metadata required
to generate the splits and an ``output_dir`` where the split information will be saved:
```python
splitter = DatasetSplitter(
    input_file=args.input_file, output_dir=args.output_dir, remove_unused_data=False
    )
```
Additionally, the `removed_unused_data` boolean indicates whether extra metadata not required for the split calculation
should be removed from the ``pandas.Dataframe`` that is returned or not. This extra metadata may be useful to generate
plots or analyse the splits in more detail.

To generate the splits we simply call the ``get_dataset_splits()`` function:
```python
# Example for azimuth splits
azimuth_splits = splitter.get_dataset_splits(
    split_type="azimuth", training_size=10, validation_size=30
)
```

### Example usage: ``PaintCalibrationDataset``
Since multiple calibration items may be required for training an alignment optimization or similar, we have created a
custom ``torch.Dataset`` that loads calibration items from the ``PAINT`` database. An example of how to use this dataset
is provided in [this script](scripts/example_dataset.py).

There are three ways of creating a ``PaintCalibrationDataset``:
1. Directly creating the dataset, based on calibration data that has already been downloaded and saved in a ``root_dir``:
```python
dataset = PaintCalibrationDataset(
     root_dir=direct_root_dir,
     item_ids=None,
     item_type=args.item_type,
 )
```
Here, the ``item_ids`` can be a list indicating which of the items contained in the ``root_dir`` should be used or if
``None`` all items will be used. The ``item_type`` is used to determine what type of calibration item should be loaded,
i.e. the raw image, cropped image, flux image, flux centered image, or calibration properties file.
2. Creating the dataset from a benchmark file (see above). In this case the ``benchmark_file`` must also be provided:
```python
train, test, val = PaintCalibrationDataset.from_benchmark(
     benchmark_file=benchmark_file,
     root_dir=benchmark_root_dir,
     item_type=args.item_type,
     download=True,
)
```
This class method will generate three ``torch.Datasets``, one for each of the considered splits.
3. Creating the dataset from a single heliostat or list of heliostats. In this case, all calibration items for the
provided heliostats will be used to create a dataset. In this case a list of ``heliostats`` must be provided:
```python
heliostat_dataset = PaintCalibrationDataset.from_heliostats(
     heliostats=heliostats,
     root_dir=heliostat_root_dir,
     item_type=args.item_type,
     download=True,
 )
```

### Example usage: Full dataset workflow
The [full dataset workflow](scripts/example_benchmark_dataset_full_workflow.py) provides an executable example of how
``PAINT`` calibration data could be directly used in further applications. When executed, the script will download the
necessary metadata to generate benchmark splits (if this data is not already downloaded), generate the dataset benchmark
splits, and initialize a ``torch.Dataset`` based on these splits (downloading the data if necessary). The script takes
the following arguments:
- ``metadata_input`` - Path to the file containing the metadata required to generate the dataset splits.
- ``output_dir`` - Root directory to save all outputs and data.
- ``split_type`` - The benchmark dataset split type to apply.
- ``train_size`` - The number of training samples required per heliostat - the total training size depends on the number
of heliostats.
- ``val_size`` - The number of validation samples required per heliostat - the total training size depends on the number
of heliostats.
- ``remove_unused_data`` - Whether to remove metadata that is not required to load benchmark splits, but may be useful
for plots or data inspection.
- ``item_type`` - The type of calibration item to be loaded -- i.e., raw image, cropped image, flux image, flux
centered image, or calibration properties.

Feel free to execute the script and have some fun :rocket:!

## How to contribute
Check out our [contribution guidelines](CONTRIBUTING.md) if you are interested in contributing to the `PAINT` project :fire:.
Please also carefully check our [code of conduct](CODE_OF_CONDUCT.md) :blue_heart:.

## Acknowledgments
This work is supported by the [Helmholtz AI](https://www.helmholtz.ai/) platform grant.

-----------
<div align="center">
  <a href="https://www.dlr.de/EN/Home/home_node.html"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_dlr.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="http://www.kit.edu/english/index.php"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_kit.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="https://synhelion.com/"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_synhelion.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="https://www.helmholtz.ai/"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_hai.svg" height="25px" hspace="3%" vspace="25px"></a>
</div>
