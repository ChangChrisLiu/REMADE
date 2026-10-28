# Third-party references

This directory contains the existing local source snapshots of three reference repositories, including local edits that predated the REMADE reorganization. Source notices and license files are retained. The English update translates comments and consolidates the bilingual RG2 README; original text remains in Git commit `0358cac7fcff1f2dd9bf7c0e0ba79e3eb9fb289b`. The migration manifest records these editorial transformations separately.

| Snapshot | Upstream |
|---|---|
| `arws/` | https://github.com/Now4czyk/arws |
| `UR5-control-with-RG2/` | https://github.com/gouxiangchen/UR5-control-with-RG2 |
| `UR5-robotiq85-D435_control_by_python/` | https://github.com/littlefiveRobot/UR5-robotiq85-D435_control_by_python |

These are ordinary tracked file snapshots, not submodules. Nested local Git histories are excluded from publication. The [reference manifest](../docs/inventory/references.json) records base revisions and pre-existing changes. The maintained `remade` package does not import this directory.
