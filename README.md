# REMADE

Real-time visual monitoring and robot-assisted sorting of end-of-life phone components, built around a UR5e, an Intel RealSense camera and an OnRobot VGC10 vacuum gripper.

[Documentation](docs/README.md) · [Connection workflow](docs/CONNECTION_WORKFLOW.md) · [Code review](docs/CODE_REVIEW.md) · [Paper-to-code mapping](docs/PAPER_MAPPING.md)

`REMADEDEMO.py` is the maintained entry point. It continuously captures images, runs YOLO and displays labeled detections with measured FPS. With `--sort`, one robot worker picks a component and returns home while monitoring continues. The next target comes from a fresh image after the robot returns.

## Run

Use Python 3.10 or 3.11 on the laboratory computer. The runtime requirements are a compatibility candidate for the supplied checkpoint, not a captured original environment.

```bash
git clone https://github.com/ChangChrisLiu/REMADE.git
cd REMADE
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python REMADEDEMO.py
```

The default is camera monitoring without a robot connection. Press **Q** or **Esc**, or close the window, to exit. Robot sorting uses the stored lab calibration and requires the configured robot and vacuum interface:

```bash
python REMADEDEMO.py --sort --robot-ip 10.125.145.89
python REMADEDEMO.py --help
```

The automatic vacuum bridge requires Linux and `socat`; an existing serial interface can be supplied with `--serial-device`. See [setup and operation](docs/OPERATIONS.md) before using motion. This checkout has been checked offline; physical motion, grasping, camera latency and calibration have not been validated here.

## Repository

```text
REMADEDEMO.py       maintained launcher
remade/            application, monitoring, vision, geometry, robot and vacuum modules
assets/            supplied checkpoint, sample image and runtime trajectories
tests/             offline regression tests, with no robot/camera access
tools/             static repository validation and source index generation
docs/              architecture, file guide, review, operation and research mapping
legacy/            original experiments, retained as historical source
references/        third-party source snapshots with original notices
```

Every original file is accounted for in the [migration manifest](docs/inventory/migration.csv). Original experiments are archived, not collected as automated tests. Reference snapshots are ordinary files, so a regular clone includes their source.

Documentation and source comments are in English. Translated archives retain their original snapshots in Git and separate original/current hashes. The [connection workflow](docs/CONNECTION_WORKFLOW.md) traces startup checks, continuous vision, coordinate conversion, robot/vacuum commands and shutdown. Offline integration tests exercise this complete software chain through simulated device boundaries.

## Classes

| ID | Checkpoint label | Sorting destination |
|---|---|---|
| 0 | Case | Low-value bin |
| 1 | Film | Low-value bin |
| 2 | High Value Middle | High-value bin |
| 3 | Screen | Low-value bin |
| 4 | iPhone Case | High-value bin |

The checkpoint is a YOLOv8 segmentation model; the active sorting logic uses bounding-box centers and a calibrated plane. Automatic case flipping and the battery-removal sequence described in the paper are not integrated into this entry point.

## Development checks

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
```

These checks do not load the model, deserialize trajectory files, connect to hardware or execute archived experiments. CI runs the same checks.

## Research and attribution

Related publication: Chang Liu et al., **RAISE: A Robot-Assisted SelectIve Disassembly and Sorting System for End-of-Life Phones**, *Resources, Conservation & Recycling* 225 (2026), 108609. [DOI](https://doi.org/10.1016/j.resconrec.2025.108609).

REMADE is the repository name; RAISE is the paper's system name. The paper describes a wider cutting, sorting and battery-removal system. Its reported performance is not a benchmark of this refactored checkout. See [paper correspondence](docs/PAPER_MAPPING.md) and [third-party notices](THIRD_PARTY_NOTICES.md). No new blanket license has been assigned to the mixed historical source.
