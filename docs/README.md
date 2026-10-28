# Project documentation

| Document | What it explains |
|---|---|
| [Architecture and data flow](ARCHITECTURE.md) | How capture, detection, coordinates, motion and vacuum control work together |
| [Connection workflow](CONNECTION_WORKFLOW.md) | The launch-to-shutdown chain, connection checks and integration evidence |
| [File-by-file code guide](CODE_GUIDE.md) | Each maintained module and historical experiment |
| [Setup and operation](OPERATIONS.md) | Installation, live monitoring, sorting and troubleshooting |
| [Code review](CODE_REVIEW.md) | Findings, fixes, remaining limitations and validation scope |
| [Assets and dependencies](ASSETS_AND_DEPENDENCIES.md) | Models, trajectories, dependencies and provenance |
| [Paper-to-code mapping](PAPER_MAPPING.md) | Which parts of RAISE are implemented here |
| [Python source index](CODE_INDEX.md) | Classes and functions in every Python file |
| [Migration manifest](inventory/migration.csv) | Original paths, current paths and content hashes |
| [Asset manifest](inventory/assets.csv) | Model, trajectory and sample-image sizes and hashes |
| [Reference manifest](inventory/references.json) | Upstream revisions and pre-existing changes |
| [Third-party notices](../THIRD_PARTY_NOTICES.md) | Attribution and source ownership |

Start with [REMADEDEMO.py](../REMADEDEMO.py). Design history is recorded in the [live-monitor design](superpowers/specs/2026-10-28-live-monitor-design.md) and [organization plan](superpowers/plans/2026-10-28-remade-organization.md).
