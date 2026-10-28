# Code review record

Review date: October 28, 2026. Baseline scope covered all 39 project-owned Python files (7,820 lines), shell invocation chains, complete file/asset inventories, reference architecture and the new remade runtime. All Python source was parsed. Third-party ROS drivers were inspected at architecture/interface level; this is not a claim that every C++, launch and configuration line was certified for deployment.

Independent baseline and maintained-runtime reviews were followed by a connection-workflow review. Runtime checks execute only tests/. Historical device scripts were not imported, models were not loaded and hardware was not connected.

## Findings addressed in the maintained runtime

| Original issue | Consequence | Resolution |
|---|---|---|
| Single recv followed by unpacking | TCP fragmentation truncates state | Read header-sized packets completely; reject invalid sizes, disconnection and non-finite values |
| New socket for each state read | Connection churn and stale data | Reuse the socket and drain queued state packets |
| Unbounded connection/motion waits | Device failures can hang the session | Socket timeouts and motion deadlines |
| Deadline applied once to a fragmented packet | A late fragment can extend the total wait | Clamp every recv to the remaining absolute deadline and check cancellation between fragments |
| Motion errors wait for UI cleanup | Slow inference delays stopping | Worker attempts stopl immediately and preserves the original error |
| Vacuum released 10 ms after descent command | Release before reaching the destination | Confirm arrival before vacuum.off |
| Ignored shell/Modbus failures | Sorting continues without working vacuum | Validate connection and Modbus responses; propagate failure |
| Global pkill socat | Terminates unrelated sessions | Only terminate the owned bridge |
| Camera pipeline recreated per capture | Initialization overhead and resource ambiguity | One continuous pipeline with explicit close |
| Model recreated per image | Repeated weight loading | One persistent Detector/model |
| One-shot capture and blocking motion | Frozen monitoring during sorting | Continuous main-thread vision and one robot worker |
| Whole batch based on one old image | Stale targets after objects move | Pick one, return home, discard buffers and observe again |
| Shared pose arrays modified in place | Station/target corruption | Explicit pose copies |
| Zero/pi rotation singularities and angle wrap | NaN or incorrect arrival waits | Rodrigues handling and relative-matrix angle distance |
| Top-level hardware connections | Imports/tests operate equipment | Side-effect-free maintained imports and explicit --sort |
| Scattered paths, confidence and IP | Configuration is hard to trace | CLI, central Settings and project-root asset resolution |
| Replaced model changes class meanings | Wrong destinations | Validate class IDs/names in sorting mode |
| Initial movement precedes camera/inference/vacuum validation | Startup failures appear after motion begins | Validate first frame/inference/display, robot state and a read-only vacuum response before the first movel |
| Ctrl+C while waiting for worker shutdown skips cleanup | Connections/camera/window remain open | Defer interruption until worker termination, then close resources and propagate it |

A scheduling test originally assumed that the worker had started by frame two. Event synchronization now ties it to actual readiness. Linux CI also exposed platform-dependent Path ordering in the source index; sorting by POSIX relative-path strings and a case-sensitive filename regression fixed that discrepancy.

The English update translates documentation and archived comments. Seventeen Python files retain identical executable ASTs; the bilingual reference README is consolidated with attribution retained. Original and translated hashes are separately recorded.

## Historical defects retained

Translation does not repair archived behaviour. These scripts are not the maintained runtime:

- runwithpath.py and standardpickup.py append motion parameters to shared waypoint rows; repeated use grows six/nine fields into invalid longer rows.
- REMADETEST.py mixes laboratory and localhost RTDE connections.
- Fulltest.py and ootest1.py use translation-vector shapes inconsistent with their two-dimensional indexing.
- util.py incompletely handles zero and half-turn rotations.
- gripper_tests/test111.py defines a property that requires a channel argument.
- rtde.py mixes older Python text/bytes assumptions.
- imagete.py and other experiments retain original absolute paths and working-directory assumptions.
- Several scripts retain high speeds, fixed IPs/TCP/stations and import-time equipment access. A filename containing test does not make them offline-safe.

## Verification and remaining limits

The reproducible commands are in [operations](OPERATIONS.md); application-level evidence is in [connection workflow](CONNECTION_WORKFLOW.md). CI runs the offline suite and repository validator on Python 3.10, 3.11 and 3.12. See [GitHub Actions](https://github.com/ChangChrisLiu/REMADE/actions/workflows/checks.yml).

Checks cover syntax, all 461 original-file records, 16 model/trajectory/sample asset records, English repository text, maintained documentation links and the generated source index. Runtime dependency resolution was dry-run, without installing or executing the full model stack.

Remaining laboratory validation:

1. Calibration, TCP, camera mount, pick height, negative z and station clearance match the original bench; none was remeasured or collision-checked.
2. The new defaults of 0.2 m/s, 0.5 m/s squared and 60% vacuum differ from some original DEMO settings.
3. A Modbus acknowledgement does not prove suction, grasp success or part retention; pressure feedback/retry/drop detection are absent.
4. TCP state decoding assumes the original controller's 444:492 pose field on port 30003; verify against actual UR firmware.
5. RealSense 1920 x 1080 at 30 FPS, USB stability, GUI latency and GPU inference throughput were not measured here.
6. Flipping, obstacle avoidance, trajectory planning and cutting/cooling/hammer interlocks are not integrated.
7. The checkpoint and candidate dependencies need laboratory reproduction; recognition performance needs separate evaluation.

Offline checks establish software behaviour under simulated boundaries. They do not replace physical commissioning.
