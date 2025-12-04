<p align="center">
  <a href="https://paint-database.org" target="_blank">
    <img src="https://raw.githubusercontent.com/ARTIST-Association/PAINT/main/logo.svg" alt="logo" width="450"/>
  </a>
</p>

# PAINT

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17816865.svg)](https://doi.org/10.5281/zenodo.17816865)
![PyPI](https://img.shields.io/pypi/v/paint-csp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10540/badge)](https://www.bestpractices.dev/projects/10540)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=32113&i=32322&r=133)
[![](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
![PyPI - Downloads](https://static.pepy.tech/badge/paint-csp/month)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/ARTIST-Association/PAINT/graph/badge.svg?token=B2pjCVgOhc)](https://codecov.io/gh/ARTIST-Association/PAINT)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ARTIST-Association/PAINT/main.svg)](https://results.pre-commit.ci/latest/github/ARTIST-Association/PAINT/main)
[![Documentation Status](https://readthedocs.org/projects/paint/badge/?version=latest)](https://paint.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/badge/Contact-artist%40lists.kit.edu-blue?label=Contact)](artist@lists.kit.edu)

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
We heavily recommend installing the `PAINT` package in a dedicated `Python3.10+` virtual environment. You can install the
latest stable version of PAINT directly from PyPI using:
```bash
  pip install paint-csp
  ```
Alternatively, You can install the latest developmental version of ``PAINT`` directly from the GitHub repository via:
```bash
pip install git+https://github.com/ARTIST-Association/PAINT
```
You can also install ``PAINT`` locally. To achieve this, there are two steps you need to follow:
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

### Example usage:
In the ``scripts`` folder there are multiple scripts highlighting how ``PAINT`` can be used. Detailed
descriptions of these scripts are available via our [Documentation](http://paint.readthedocs.io).

## How to contribute
Check out our [contribution guidelines](CONTRIBUTING.md) if you are interested in contributing to the `PAINT` project :fire:.
Please also carefully check our [code of conduct](CODE_OF_CONDUCT.md) :blue_heart:.

## Acknowledgments
This work is supported by the [Helmholtz AI](https://www.helmholtz.ai/) platform grant.

<div align="center">
  <a href="https://www.re3data.org/badges/s/light/100014627.svg">
    <img src="https://www.re3data.org/badges/s/light/100014627.svg" alt="re3data Badge">
  </a>
</div>

-----------
<div align="center">
  <a href="https://www.dlr.de/EN/Home/home_node.html"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_dlr.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="http://www.kit.edu/english/index.php"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_kit.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="https://synhelion.com/"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_synhelion.svg" height="50px" hspace="3%" vspace="25px"></a>
  <a href="https://www.helmholtz.ai/"><img src="https://raw.githubusercontent.com/ARTIST-Association/ARTIST/main/logos/logo_hai.svg" height="25px" hspace="3%" vspace="25px"></a>
</div>
