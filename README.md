<p align="center">
<img src="logo.svg" alt="logo" width="450"/>
</p>

# PAINT

[![](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![](https://img.shields.io/badge/Contact-artist%40lists.kit.edu-blue?label=Contact)](artist@lists.kit.edu)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B%20%20%E2%97%8F%20%20%E2%97%8B-orange)](https://fair-software.eu)
[![codecov](https://codecov.io/gh/ARTIST-Association/PAINT/graph/badge.svg?token=B2pjCVgOhc)](https://codecov.io/gh/ARTIST-Association/PAINT)

## What is ``PAINT``

The PAINT database makes operational data of concentrating solar power plants available in accordance with the FAIR data
principles, i.e., making them findable, accessible, interoperable, and reusable. Currently, the data encompasses
calibration images, deflectometry measurements, kinematic settings, and weather information of the concentrating solar
power plant in Jülich, Germany, with the global power plant id (GPPD) WRI1030197. Metadata for all database entries
follows the spatio-temporal asset catalog (STAC) standard.

## Installation
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
   - Install basic dependencies: ``pip install -e .``

## Structure
The ``PAINT`` repository is structured as shown below:
```
.
├── data-preparation-scripts # Scripts used to generate STAC files and structure data
├── html # Code for the paint-database.org website
├── markers # Saved markers for the WRI1030197 power plant in Jülich
├── paint # Python package/
│   ├── data
│   └── util
├── plots # Scripts to generate plots
└── tests # Tests for the python package/
    ├── data
    └── util
```

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
