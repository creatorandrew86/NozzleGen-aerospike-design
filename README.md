# Aerospike Design

Aerospike Design is a small desktop application for generating an aerospike nozzle contour using Angelino-style expansion calculations.

The program uses a Tkinter interface to collect engine and geometry inputs, computes the contour, plots the result, and can export the generated points to a `.dat` file.

## Features

- GUI-based input for propellant pair, chamber pressure, mixture ratio, mass flow, and nozzle geometry
- Aerospike contour generation using `rocketcea` thermochemical data
- Plotting of the computed contour with `matplotlib`
- Export of the contour data to a `.dat` file

## Requirements

- Python 3.10 or newer
- `tkinter`
- `matplotlib`
- `scipy`
- `rocketcea`

Notes:

- `tkinter` is included with many Python installations, but some Linux distributions package it separately.
- `rocketcea` may require additional system dependencies depending on your platform.

## Project Structure

- `Source Code/main.py` - application entry point
- `Source Code/interface.py` - Tkinter user interface and file export logic
- `Source Code/solver.py` - aerospike contour calculations
- `Source Code/assets/icon.ico` - window icon used by the GUI

## Running The Program

From the project root:

```bash
python "Source Code/main.py"
```

If you are using a virtual environment, activate it first.

## How It Works

1. Enter the engine definition:
   - oxidizer
   - fuel
   - chamber pressure
   - mixture ratio
   - nozzle mass flow
   - design area ratio
2. Enter the aerospike definition:
   - top radius
   - effective throat area ratio
   - throat angle
   - truncation percentage
   - aerospike resolution
3. Click `Run` to generate the contour.
4. A plot window opens showing the resulting `x` vs `R_x` contour.
5. Click `Save Contour` to export the points to a `.dat` file.

## Input Notes

- Pressure units supported by the UI: `bar`, `Pa`, `atm`, `kPa`, `psi`, `MPa`
- Mass flow units supported by the UI: `kg/s`, `lb/s`, `g/s`
- Radius units supported by the UI: `m`, `cm`, `in`, `ft`
- Throat angle must be between 30 and 90 degrees
- `Save Contour` only works after the contour has been generated

## Output

The saved `.dat` file contains one point per line in the form:

```text
x R_x eps_x
```

where:

- `x` is the axial coordinate
- `R_x` is the radial coordinate
- `eps_x` is the local area ratio used for that station

## Troubleshooting

- If the program reports missing inputs, make sure every field is filled in before running the solver.
- If the plot does not appear, verify that `matplotlib` is installed with a Tk-compatible backend.
- If `rocketcea` fails to import, check that it and its dependencies are installed correctly in the active environment.

## License

This project is distributed under the terms of the GNU GPL v3. See the `LICENSE` file for details.
