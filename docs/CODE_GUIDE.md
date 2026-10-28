# File-by-file code guide

## Maintained modules

| File | Main interfaces | Responsibility |
|---|---|---|
| [Launcher](../REMADEDEMO.py) | main(argv) | Retains the original entry-point name without embedding control logic |
| [app](../remade/app.py) | parser, main | CLI validation, resource composition, vision preparation, mode selection and exit codes |
| [monitor](../remade/monitor.py) | run_monitor, StopRequested | Main-thread image loop, single worker, fresh-frame scheduling and error propagation |
| [vision](../remade/vision.py) | RealSenseStream, Detector, OpenCVDisplay, DetectionFrame | Camera capture, model inference and window interfaces |
| [geometry](../remade/geometry.py) | rotation_matrix, rotation_error, project_pixel_to_plane, detections_to_poses | Offline-testable coordinate mathematics |
| [robot](../remade/robot.py) | read_tcp_pose, URSocket, Sorter | Bounded transport, connection preparation and one-component motion sequence |
| [vacuum](../remade/vacuum.py) | VacuumController | Read-only preparation, two-channel commands, response checks and owned bridge lifecycle |
| [config](../remade/config.py) | Settings, calibration and class constants | Central station parameters and runtime configuration |

remade/__init__.py defines package information and version; remade/__main__.py supports python -m remade. Imports do not start hardware. See the [source index](CODE_INDEX.md) for every class/function and its line number.

## Original application and experiments

The files below are historical material, not dependencies of the maintained runtime or automated test discovery. Their comments are now English; executable Python ASTs are unchanged by translation. Original snapshots and hashes remain recorded in Git and the migration manifest. Some files access hardware on import. Their old relative paths do not form a ready-to-run installation after relocation.

| Archived script | Actual role or distinguishing behaviour |
|---|---|
| [REMADE.py](../legacy/scripts/REMADE.py) | Sorting prototype with six fixed detections; Image2TCP uses a fixed matrix despite defining a YOLO helper |
| [REMADEDEMO.py](../legacy/scripts/REMADEDEMO.py) | Source of the maintained workflow: one real capture, confidence 0.9, then batch picking |
| [REMADETEST.py](../legacy/scripts/REMADETEST.py) | Repeated capture/sorting at confidence 0.8; also opens localhost RTDE at top level |
| [runwithpath.py](../legacy/scripts/runwithpath.py) | ur_rtde and stored joint trajectories; repeatedly mutates shared waypoint rows |
| [standardpickup.py](../legacy/scripts/standardpickup.py) | Similar to runwithpath; move_to_tcp_slow uses global speed/acceleration despite its name |
| [visitdemortde.py](../legacy/scripts/visitdemortde.py) | RTDE Cartesian path demo using hard-coded intermediate stations and repeated observations |
| [visitdemo.py](../legacy/scripts/visitdemo.py) | Vision/flipping helpers; the active main program only calls go_home |
| [fliptest.py](../legacy/scripts/fliptest.py) | Fixed insertion, release, regrasp and flipping sequence; no class-triggered loop |
| [Fulltest.py](../legacy/scripts/Fulltest.py) | Early urx/ROS2/transform experiment; main connects and prints pose |
| [ootest1.py](../legacy/scripts/ootest1.py) | Early vision/grasp draft without an active loop; transform shape problems |
| [cameratest.py](../legacy/scripts/cameratest.py) | RealsenseD435 wrapper recreates the pipeline for each capture without explicit stop |
| [imagete.py](../legacy/scripts/imagete.py) | Top-level inference from a hard-coded Linux image path |
| [onrobot.py](../legacy/scripts/onrobot.py) | VG TCP/serial Modbus wrapper, channel control and pressure registers |
| [VacuumOn.py](../legacy/scripts/VacuumOn.py) | Opens /tmp/ttyUR and starts vacuum at top level |
| [VacuumOff.py](../legacy/scripts/VacuumOff.py) | Opens /tmp/ttyUR and releases vacuum at top level |
| [util.py](../legacy/scripts/util.py) | Rotation-vector/matrix/RPY conversions with zero/pi singularities |
| [rtde.py](../legacy/scripts/rtde.py) | Old UR RTDE implementation, distinct from pip ur-rtde's rtde_control module |
| [serialize.py](../legacy/scripts/serialize.py) | Message types and serialization for that old RTDE implementation |
| [manipulation.py](../legacy/scripts/manipulation.py) | ROS1/urx/Robotiq two-finger helpers; different gripper from VGC10 |
| [urxtest.py](../legacy/scripts/urxtest.py) | Top-level urx connection and pose reading |
| [test.py](../legacy/scripts/test.py) | TCP/joint state and movement helpers; reads real state at top level |
| [test1.py](../legacy/scripts/test1.py) | RTDE/path blend format experiment; loads trajectories and connects at top level |
| [toc.py](../legacy/scripts/toc.py) | Reports PyTorch CUDA availability; not a training script |

[VacuumOnscript.sh](../legacy/scripts/VacuumOnscript.sh) and [VacuumOffscript.sh](../legacy/scripts/VacuumOffscript.sh) are historical Bash/socat chains containing global pkill socat. The maintained application uses remade.vacuum.

## Trajectory and gripper experiments

| File | Purpose |
|---|---|
| [trajectory_tools/convert_paths.py](../legacy/trajectory_tools/convert_paths.py) | Adds pi/2 to each waypoint's first joint |
| [trajectory_tools/start_to_high.py](../legacy/trajectory_tools/start_to_high.py) | Active code loads/prints trajectories; robot section is commented out |
| [trajectory_tools/start_to_low.py](../legacy/trajectory_tools/start_to_low.py) | urx execution of the low-value station path |
| [trajectory_tools/high_to_home.py](../legacy/trajectory_tools/high_to_home.py) | Executes the high-value return path |
| [trajectory_tools/low_to_home.py](../legacy/trajectory_tools/low_to_home.py) | Executes the low-value return path |
| [vacuum/onrobot.py](../legacy/vacuum/onrobot.py) | Another historical VG implementation |
| [vacuum/VacuumOn.py](../legacy/vacuum/VacuumOn.py) | Vacuum enable experiment |
| [vacuum/VacuumOff.py](../legacy/vacuum/VacuumOff.py) | Vacuum release experiment |
| [vacuum/demotest.py](../legacy/vacuum/demotest.py) | Calls Bash to enable vacuum, waits, then releases |
| [gripper_tests/demo.py](../legacy/gripper_tests/demo.py) | VG demonstration with TCP argument parsing |
| [gripper_tests/onrobot.py](../legacy/gripper_tests/onrobot.py) | Historical VG implementation copy |
| [gripper_tests/sockettest.py](../legacy/gripper_tests/sockettest.py) | Top-level robot socket experiment |
| [gripper_tests/test.py](../legacy/gripper_tests/test.py) | ROS2/urx/TCP and payload experiment |
| [gripper_tests/test111.py](../legacy/gripper_tests/test111.py) | VGC10 URScript wrapper with a property-argument defect |
| [gripper_tests/testgripper.py](../legacy/gripper_tests/testgripper.py) | Sends VGC10 grasp/release URScript through urx |
| [gripper_tests/testvacuum.py](../legacy/gripper_tests/testvacuum.py) | Channel A/B commands and feedback demonstration |

Shell scripts and the extensionless ros code file are also preserved. Every path appears in the migration manifest.

## Third-party references

| Reference | Structure and role |
|---|---|
| [UR5-control-with-RG2](../references/UR5-control-with-RG2/README.md) | test_main.py socket control; util.py rotation helpers; rtde.py/serialize.py historical protocol examples. Three original project tools matched these copies byte for byte |
| [UR5-robotiq85-D435_control_by_python](../references/UR5-robotiq85-D435_control_by_python/README.md) | UR_Robot.py combines arm/camera/Robotiq control; real/ contains camera, gripper, calibration and experiments |
| [arws](../references/arws/README.md) | ROS2 fruit-picking reference with UR3e, OAK-D Pro and RG2; not this project's D435i/VGC10 launch configuration |

In arws, camera_control_node publishes custom_camera; URCommand.msg defines string x/y/depth fields. The C++ ur_mover/src/master_node.cpp uses MoveIt for Cartesian planning/execution. gripper_control_node subscribes to commands and uses dashboard services.

arws also contains Universal Robots ROS2 Driver and Description sources: calibration, controllers, dashboard messages, MoveIt configuration, descriptions, meshes and launch files. They remain reference snapshots and were reviewed at architecture/interface level, without claiming line-by-line deployment certification.
