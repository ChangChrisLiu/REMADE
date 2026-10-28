# REMADE Organization Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. Steps use checkbox syntax for tracking.

**Goal:** Rename the existing GitHub repository to REMADE, review and structure the code, maintain REMADEDEMO with continuous image monitoring, document the code and paper relationship, and publish the result.

**Architecture:** Extract the maintained entry point into the remade package. Separate vision, geometry, robot, vacuum, configuration, scheduling and application composition. Archive original source without edits, record every moved path, and import reference directories as file snapshots while keeping nested Git histories local.

**Tech Stack:** Python, NumPy, OpenCV, Ultralytics/PyTorch, RealSense, URScript/TCP, ur-rtde, Modbus, Bash; ROS 1/ROS 2 in historical experiments and references.

**Spec:** User requests on 2026-10-28: rename project/GitHub to REMADE; use the updated REMADEDEMO with real-time monitoring; review all code and structure it for GitHub. The supplied RAISE paper is context. See [live-monitor design](../specs/2026-10-28-live-monitor-design.md).

## Global Constraints

- Preserve the existing remote commit history and all local source changes.
- Do not execute or import hardware-control scripts during verification.
- Preserve original source and calibration values, documenting path migrations and changed runtime defaults.
- Preserve third-party source notices; do not assign a new blanket license.
- GitHub rename and publishing are explicitly authorized by the user.

## Review Focus

- The original remote has only README.md; importing local files must retain its parent commit.
- Nested repositories have local changes; publish file snapshots, not empty gitlinks.
- Several test-named scripts connect to hardware on import; static checks must avoid imports.
- Main entry points have different inputs and behavior; distinguish each accurately.
- Model/trajectory provenance and environment compatibility are incomplete; do not claim validated deployment.

## Tasks

### Task 1: Repository identity and preservation

- [x] Inspect local/remote state and permissions.
- [x] Rename the existing repository, retaining repository ID 900910302.
- [x] Initialize local Git from original remote main without replacing source files.
- [x] Record reference repository revisions and preserve every selected source file.

### Task 2: Documentation and source organization

- [x] Create README.md, README.zh-CN.md and docs/README.md.
- [x] Document architecture, every project script, operation, assets, dependencies and known issues.
- [x] Add third-party provenance and machine-readable source/asset inventories.
- [x] Add ignore/line-ending policy and dependency candidate manifests.
- [x] Extract the maintained application into seven modules and a thin launcher.
- [x] Implement continuous capture/detection/display with single-worker sorting and fresh observations.
- [x] Verify bug fixes and new behavior with tests before marking each change complete.
- [x] Independently review original sources and the new implementation; fix reported motion-stop and test-synchronization issues.

### Task 3: Verification and GitHub update

- [x] Parse all Python source without importing it; check documentation links and inventory coverage.
- [x] Verify asset hashes and reference snapshots; ensure no accidental gitlinks or local metadata.
- [ ] Review the complete staged update, including all original files.
- [ ] Commit and push as a fast-forward of the original main; verify remote contents and commit.

## Execution record

- Scope update: the user subsequently explicitly requested code structuring; archive the original layout with a complete migration manifest and use a new maintained package. Historical scripts are research snapshots, not runnable entry points.
- Publication decision: include third-party source snapshots with original notices and provenance; nested .git directories and editor/cache files remain local.
- Validation boundary: offline regression tests, syntax, links, hashes, dependency resolution and repository contents; no robot motion, camera access, model deserialization or ROS execution.
- Review resolution: stop requests now originate in the worker's motion failure path, so UI inference cannot delay an already-detected motion fault. The concurrency test uses readiness/event synchronization.
- Runtime decisions: monitor-only default; --sort enables motion; one component per fresh image; default speed/acceleration 0.2/0.5 and vacuum setpoint 60. These are documented changes, not validated hardware settings.
