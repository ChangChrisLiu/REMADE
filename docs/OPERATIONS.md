# Setup and operation

## Environment

The runtime uses Python, NumPy, OpenCV, Ultralytics/PyTorch, the RealSense SDK and pymodbus. Use a separate Python 3.10 or 3.11 environment on the laboratory computer. Offline tests also cover Python 3.12. Runtime constraints are a compatibility candidate derived from checkpoint metadata and historical APIs, not a captured original lockfile.

```bash
python -m venv .venv
```

Activate on Linux with `source .venv/bin/activate`, or in Windows PowerShell with `.\.venv\Scripts\Activate.ps1`. Then run:

```bash
python -m pip install -r requirements.txt
python REMADEDEMO.py --help
```

The display requires a desktop environment and GUI-enabled opencv-python. A headless-only installation cannot create the window. RealSense needs device permissions, working USB and a supported stream configuration. Automatic vacuum bridging uses Linux and socat; on Ubuntu install it with `sudo apt-get install socat`.

## Live monitoring

```bash
python REMADEDEMO.py
python -m remade --confidence 0.8 --fps 30
```

By default, only the camera and model are used. No robot or vacuum connection is opened. The window shows boxes, class labels, confidence and measured loop FPS. Requested capture FPS differs from visible inference FPS; performance depends on the camera, USB, CPU/GPU and model.

The default checkpoint resolves relative to the project root. An explicit --weights path is interpreted as supplied. Sorting checks model class IDs and names against the routing configuration. Capture stays at 1920 x 1080 to match the retained intrinsics; changing capture resolution requires a calibration review.

## Sorting

```bash
python REMADEDEMO.py --sort --robot-ip 10.125.145.89
```

The UR controller must permit external script control, with TCP 30003 reachable. The VGC10 tool serial interface must be forwarded on port 54321 for automatic bridging. The program owns a temporary serial path and its own socat process. An existing serial connection can be supplied instead:

```bash
python REMADEDEMO.py --sort --serial-device /dev/ttyUSB0
```

See the [connection workflow](CONNECTION_WORKFLOW.md) for startup checks and connection order. After startup, the robot returns home. Each observation selects one supported target, picks it, places it at its class destination and returns home before another observation can trigger motion. Monitoring continues during motion.

The base frame, camera mount, TCP, gripper, worktable and destinations must correspond to [config.py](../remade/config.py). The application does not provide obstacle avoidance, part-presence sensing, grasp confirmation or automatic extrinsic updates. A Modbus acknowledgement confirms command acceptance only.

## Options

| Option | Default | Meaning |
|---|---|---|
| --weights | assets/models/smallmodeldet.pt | Supplied checkpoint |
| --confidence | 0.9 | Original DEMO threshold; the paper reports 0.8 |
| --fps | 30 | Requested capture FPS, subject to device support |
| --robot-ip | 10.125.145.89 | Original laboratory controller address |
| --speed | 0.2 | Cartesian speed in m/s; original DEMO ordinary moves used 2.5 |
| --acceleration | 0.5 | Cartesian acceleration in m/s squared; original DEMO used 2.5 |
| --vacuum-percent | 60 | Both channels' target percentage, from 1 to 80 |
| --serial-device | Automatic bridge | Existing device, such as /dev/ttyUSB0 or a configured Windows COM port |

Speed and acceleration use the lower values found in historical comments. The 60% vacuum target follows historical gripper experiments and replaces the old VG implementation's 0xff value. These defaults require validation on actual equipment before changing laboratory operating limits.

## Exit and troubleshooting

Q, Esc, window closure or Ctrl+C ends the session. The application stops submitting targets, requests worker shutdown, sends stopl and closes serial, bridge, camera and window resources. It does not intentionally release a component during shutdown. Software stopping depends on connection and driver state and does not replace equipment emergency stops.

| Symptom | Check |
|---|---|
| Model missing | --weights and the asset manifest |
| Camera cannot start or frames stop | USB, permissions, competing applications and supported --fps |
| OpenCV window fails | Desktop session and GUI-enabled OpenCV |
| Checkpoint loading fails | Supplied model's Ultralytics 8.2.41 metadata and installed versions |
| pymodbus.client.sync cannot import | The runtime uses pymodbus 2.5.3, not the incompatible 3.x API |
| Vacuum bridge fails | Linux/socat, tool-serial forwarding, port 54321 and serial permissions |
| Robot arrival times out | Controller state, external-control permission, station coordinates and protective stops |

## Offline checks

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
```

Only discover tests under tests/. Files named test in legacy/ and references/ are often hardware experiments with import-time effects. pytest.ini also limits discovery to tests/.
