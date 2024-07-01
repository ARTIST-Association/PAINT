# PAINT

[![](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![](https://img.shields.io/badge/Contact-artist%40lists.kit.edu-orange?label=Contact)](artist@lists.kit.edu)

## What is ``PAINT``

PAINT is a FAIR database for Concentrating Solar Power plants (CSP).

## Installation
We heavily recommend installing the `PAINT` package in a dedicated `Python3.8+` virtual environment. You can
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
├── paint # Parent package
│   ├── data # Objects in the field, e.g. heliostats and receivers
│   └── util
├── plots # scripts to create summary plots of the data
├── tests/
│   ├── data
│   └── util
└── tutorials # small use example for the PAINT data API
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
