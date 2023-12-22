[![Mypy](https://github.com/BioImaging-NKI/pymicroscopysoftwareautomation/actions/workflows/mypy.yml/badge.svg)](https://github.com/BioImaging-NKI/pymicroscopysoftwareautomation/actions/workflows/mypy.yml)
[![Black](https://github.com/BioImaging-NKI/pymicroscopysoftwareautomation/actions/workflows/black.yml/badge.svg)](https://github.com/BioImaging-NKI/pymicroscopysoftwareautomation/workflows/black.yml)
# Automation of microscopy software
Give python control over commercial microscopy software. 

At the moment it is used to aquire data on a dragonfly, and automate starting different protocols if needed. It could be used in combination with h5py to analyse the .ims files. It can also be used for automatic timed injection of a stimulus while a running protocol is temorarily paused. If the injector supports python.

This method is not intended for direct interfacing with the hardware. Depending on what software features the vendors port to their API this package might support movement of a stage in the future. But since control will always go through the commercial software it will likely not be fast enough to automatically track particles or cells.

## Install
Clone or download the repository

Run: `pip install .`

## Development
Clone the repository

Run: `pip install -e .[dev]`

## Documentation
Microscopy software must support at minimum:
* run()
* pause()
* resume()
* stop()
* get_state()

