# Third-party source and provenance

REMADE includes historical experiments and reference material from multiple sources. This reorganization preserves the notices already present and does not apply a new license across the combined repository.

| Material | Evidence / retained attribution |
|---|---|
| [UR5-control-with-RG2](references/UR5-control-with-RG2/README.md) | Existing local remote: gouxiangchen/UR5-control-with-RG2. Its README credits starter code by MengHao666 |
| [UR5-robotiq85-D435_control_by_python](references/UR5-robotiq85-D435_control_by_python/README.md) | Existing local remote: littlefiveRobot/UR5-robotiq85-D435_control_by_python |
| [arws](references/arws/README.md) | Existing local remote: Now4czyk/arws. Its README names Patryk Marczak and Kacper Nowaczyk |
| [UR ROS2 Driver license](references/arws/src/Universal_Robots_ROS2_Driver/LICENSE) | Preserved upstream license file and per-file notices |
| [UR ROS2 Description license](references/arws/src/Universal_Robots_ROS2_Description/LICENSE) | Preserved upstream license file; meshes may carry additional terms |
| [UR20 mesh license](references/arws/src/Universal_Robots_ROS2_Description/meshes/ur20/LICENSE.txt) | Preserved asset-specific notice |
| `legacy/scripts/rtde.py`, `serialize.py` | Copyright 2016 Universal Robots A/S and redistribution conditions remain in source headers; exact duplicates of the RG2 reference copies |
| `legacy/scripts/util.py` | Exact duplicate of the RG2 reference file; retained as an archive, not used by the new geometry module |
| `assets/models/smallmodeldet.pt` | Checkpoint metadata identifies Ultralytics 8.2.41, a segmentation model, and an AGPL-3.0 license string; see the asset documentation |

Base revisions and existing local changes are recorded in [references.json](docs/inventory/references.json). Some historical scripts have no explicit authorship/license information in the supplied files; their provenance remains incomplete. No claim of original authorship is made for those files.

The user supplied the RAISE paper as project context. This repository cites its DOI and summarizes its relationship to the code; the supplied PDF is not republished here. The paper's publication license does not assign a license to this software collection.
