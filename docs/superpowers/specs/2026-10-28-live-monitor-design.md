# REMADEDEMO live-monitor design

The user selected REMADEDEMO as the maintained entry point and required real-time image monitoring. The original captured once, blocked during sorting and connected to the robot at import time.

Keep the existing Python/OpenCV/RealSense/YOLO stack. Capture, inference and display run on the main thread; one worker serializes homing and sorting. Start the camera once and load the model once. Continue displaying frames during motion, discard buffered frames after homing and obtain a new observation before selecting another target.

A simple loop alone would still block during motion. A separate process would add state and shutdown coordination. A single worker thread meets the present scope.

Default to monitoring. Only --sort enables robot connections and motion. Q, Esc and window closure request shutdown; the worker stops cooperatively, and cleanup retains vacuum state rather than releasing a potentially held component. Software stopping does not replace an equipment emergency stop.

Retain the original calibration, classes and stations. Use the historical lower motion settings of 0.2 m/s and 0.5 m/s squared, and the historical gripper experiment's 60% vacuum target. These implementation choices need laboratory validation. Camera, inference and robot failures stop new work and close resources. Display measured FPS without claiming hard real-time performance.

The user subsequently requested a complete review and structured code. Split the runtime into config, geometry, robot, vacuum, vision, monitor and app modules. Archive originals with a migration record. Pick one target per observation and return home before recapturing to avoid stale targets in stacked scenes.

The English/workflow update adds a first-frame inference/display check and read-only robot/vacuum connection checks before initial motion. The preparation image never becomes a pick target. Documentation and archived comments are English; original snapshots remain in Git with separate original/current hashes.

Offline tests cover continuous display, serialized motion, fresh frames, empty detections, error propagation, cancellation, cleanup, complete TCP packet reads and application-level integration through simulated device boundaries. Physical calibration, grasping and latency measurements require laboratory equipment.
