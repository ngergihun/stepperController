# 3-Axis Stepper Motor Controller

This open-source 3-axis stepper motor controller project was developed by the SMIS beamline of synchrotron SOLEIL in collaboration with DM Devices.

The goal is to provide a complete electronics and software solution for controlling three stepper motors, including:

- Controller electronics and schematics
- Embedded firmware for the motor controller
- Hardware documentation and assembly information
- A Python communication layer for full computer control

## Repository contents

- [`docs/`](docs/): Controller documentation and reference PDFs
- [`schematics/`](schematics/): Electronics design files and interactive bill of materials
- [`software/Firmware/`](software/Firmware/): Embedded controller firmware
- [`software/SerialParser/`](software/SerialParser/): Python communication and command interface

## Documentation

See the [3-axis Stepper Motor Controller documentation](docs/3axisStepperController.md) for system details, wiring information, configuration, and serial commands.

## Licensing

The repository uses separate licenses for its different types of work:

| Repository content | License | License file |
| --- | --- | --- |
| Hardware designs, schematics, and related hardware documentation | CERN Open Hardware Licence Version 2 - Strongly Reciprocal (`CERN-OHL-S-2.0`) | [`LICENSE-CERN-OHL-S-2.0.txt`](LICENSE-CERN-OHL-S-2.0.txt) |
| Firmware and Python communication layer | MIT License | [`LICENSE-MIT.txt`](LICENSE-MIT.txt) |
| User documentation and explanatory text | Creative Commons Attribution 4.0 International (`CC BY 4.0`) | [`LICENSE-CC-BY-4.0.txt`](LICENSE-CC-BY-4.0.txt) |

Please preserve the project attribution to the [SMIS beamline][smis_website] of synchrotron SOLEIL and [DM Devices][dm_website] when redistributing or modifying the project. These licensing notices apply only to material for which the project contributors have the necessary rights to grant the stated license.

[dm_website]: https://curiousscientist.tech/
[smis-website]: https://www.synchrotron-soleil.fr/en/beamlines/smis
