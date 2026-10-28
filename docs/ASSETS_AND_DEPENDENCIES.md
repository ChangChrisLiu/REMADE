# Assets, dependencies and provenance

## Model and images

| Path | Content | Maintained runtime |
|---|---|---|
| assets/models/smallmodeldet.pt | Original 23,850,851-byte segmentation checkpoint | Yes |
| assets/images/001_Color.png | Original sample colour image | Documentation/offline material; runtime uses live capture |
| references/arws/yolov8n.pt | Fruit-picking reference model | No |
| references/arws/src/camera_control/camera_control/scripts/yolov8n.pt | Another copy of the reference model | No |

Although named smallmodeldet.pt, static metadata identifies the main checkpoint as an Ultralytics SegmentationModel. Active sorting uses bounding boxes only. Training data, data1.yaml, training commands and the identity of the paper's final evaluation weights are not established by this checkout.

[assets.csv](inventory/assets.csv) records sizes and SHA-256 hashes for .pt, .pkl and the sample image. Validation reads bytes without executing pickle or PyTorch deserialization.

## Trajectories

- assets/trajectories/runtime/: the original root paths_for_demo directory, containing start_to_high, start_to_low, high_to_home and low_to_home.
- legacy/trajectory_tools/original_paths/: original trajectories.
- legacy/trajectory_tools/paths_for_demo/: converted copies from the original 04 directory.
- legacy/trajectory_tools/convert_paths.py: adds pi/2 to the first joint of every waypoint, retaining the other joints.

Historical comments attribute trajectories to MPNet, but no MPNet model, training code, planner or collision environment is supplied. The maintained entry point follows the DEMO Cartesian sequence and does not load these pickle files. Their presence does not establish a complete planning implementation.

## Runtime dependencies

| Dependency | Purpose | Version decision |
|---|---|---|
| NumPy | Geometry and arrays | At least 1.24 and below 2.0 for historical compatibility |
| OpenCV | Annotation display, windows and keyboard input | GUI-enabled opencv-python; range in requirements.txt |
| Ultralytics | Checkpoint inference | 8.2.41, matching checkpoint metadata |
| PyTorch / torchvision | Model execution | Candidate ranges 2.2–2.5 / 0.17–0.20, not an original environment lock |
| pyrealsense2 | RealSense colour stream | SDK 2.x; actual device support requires validation |
| pymodbus | VGC10 Modbus RTU | 2.5.3, retaining pymodbus.client.sync |
| pyserial | Serial transport | 3.x |
| socat | TCP-to-tool-serial bridge | System executable used by automatic Linux bridging |

These historical versions are compatibility choices. Future dependency upgrades must validate checkpoint loading and model behaviour. Do not treat the constraints as proof that the laboratory stack has been reproduced.

Monitoring uses BGR images. See [Ultralytics prediction documentation](https://docs.ultralytics.com/modes/predict/) for NumPy input and plotted output conventions, and the [librealsense Python pipeline definition](https://github.com/realsenseai/librealsense/blob/master/wrappers/python/pyrs_pipeline.cpp) for pipeline lifecycle.

## Historical dependencies

urx, ur-rtde, ROS1 rospy, ROS2 rclpy/MoveIt, DepthAI, supervision, SciPy and scikit-learn occur in archived experiments or reference systems. They are not all required for the maintained DEMO. The reference ROS2 project uses other hardware and an independent workspace.

## Preservation and English translation

The original local directory was not a parent Git repository; the old remote contained one README commit. Importing the project on that parent retained the original repository identity. All 461 original publishable files are represented in the [migration manifest](inventory/migration.csv). Editor settings, bytecode caches and nested .git histories remain local.

The manifest keeps original path, current path, original byte count, original raw SHA-256 and original normalized SHA-256. Text canonicalization only replaces CRLF with LF. The English update adds sha256_current, transformation and original_snapshot_commit. Original hashes are never replaced with translation hashes.

The 17 translated Python archives contain comment-only changes, verified by identical parsed ASTs. One reference README consolidates its duplicated bilingual prose into English while retaining attribution. The complete pre-translation snapshot remains at commit 0358cac7fcff1f2dd9bf7c0e0ba79e3eb9fb289b. Asset bytes are unchanged.

Reference snapshots include upstream content and local edits that predated reorganization. Their upstream revisions and pre-existing changes are recorded in [references.json](inventory/references.json). These are ordinary tracked files, without gitlinks to unpublished local commits. No changes were submitted to the upstream repositories.
