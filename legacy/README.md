# Historical experiments

These are the original project-owned files. The English update translates comments without changing executable Python ASTs. Original sources remain in Git commit `0358cac7fcff1f2dd9bf7c0e0ba79e3eb9fb289b`; the migration manifest records original and current hashes separately. Git may normalize text line endings. Use the maintained [REMADEDEMO.py](../REMADEDEMO.py) entry point.

- `scripts/`: original root scripts and shell wrappers.
- `trajectory_tools/`: former `04/`, including original and converted paths.
- `vacuum/`: former `VacuumFunction/`.
- `gripper_tests/`: former `testuse/`.

These scripts may connect to hardware during import. Their old working-directory assumptions and absolute paths are retained for research traceability, so this archive is not an independently runnable installation. See the [code guide](../docs/CODE_GUIDE.md), [review](../docs/CODE_REVIEW.md) and [migration manifest](../docs/inventory/migration.csv).
