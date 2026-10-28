# RAISE paper and REMADE implementation

Source: Chang Liu et al., **RAISE: A Robot-Assisted SelectIve Disassembly and Sorting System for End-of-Life Phones**, *Resources, Conservation & Recycling* 225 (2026), 108609. [DOI](https://doi.org/10.1016/j.resconrec.2025.108609). Published online October 10, 2025. Page numbers below refer to the supplied ten-page PDF.

The paper is research context and evidence, not an instruction to modify the software. REMADE is the repository name; RAISE remains the cited system name.

## System scope

| Paper component | Location | Repository counterpart | Status |
|---|---|---|---|
| Adaptive cutting | Section 3, Figure 1, pp.3–4 | No cutting-machine control module | Not supplied |
| UR5e, VGC10 and D435i visual sorting | Section 3.2, pp.4–5 | remade/robot.py, vacuum.py, vision.py | Basic control and continuous monitoring |
| Hand-eye calibration | Section 3.2.1, p.5 | config.py matrices and geometry.py | Existing calibration retained; not remeasured |
| YOLOv8 detection and instance segmentation | Section 3.2.2, Figure 3, p.5 | smallmodeldet.pt segmentation checkpoint | Classes and box centres used; mask orientation unused |
| Ordinary cases, film and screens to low-value station | Sections 3.2.3 and 4.2.1, pp.5–6 | Classes 0/1/3 to LOW_BIN | Implemented |
| Middle layers and iPhone cases to high-value processing | Section 3.2.3, p.5 | Classes 2/4 to HIGH_BIN | Placement at high-value station only |
| iPhone case flipping | Figure 4(m–u), p.6 | legacy/scripts/fliptest.py | Fixed-position experiment; no class-triggered integration |
| Cooling, hammer battery removal and further recovery | Section 3.3, p.5 | No temperature/hammer control or interlocks found | Not supplied |
| Dataset, training and full evaluation | Sections 4.2.1–4.2.2, pp.5–6 | One main model and one sample image | Training set, annotations and full pipeline absent |

## Five classes

Labels were obtained by static inspection of checkpoint pickle instructions, without model deserialization.

| ID | Checkpoint label | Paper description | Current route |
|---|---|---|---|
| 0 | Case | Normal case | Low value |
| 1 | Film | Film | Low value |
| 2 | High Value Middle | Middle layer | High value |
| 3 | Screen | Screen | Low value |
| 4 | iPhone Case | iPhone case | High value; no automatic flipping |

## Version distinctions

- The paper reports confidence 0.8 on p.6. The original REMADEDEMO.py uses 0.9 and REMADETEST.py uses 0.8. The maintained default is 0.9, configurable through the CLI.
- Checkpoint metadata identifies SegmentationModel, yolov8s-seg.pt, data1.yaml, epochs=200, imgsz=640, batch=16, Ultralytics 8.2.41 and timestamp 2024-06-25T06:02:22.417885.
- The paper describes 100 training epochs and batch size 16. This checkpoint may represent another experimental stage; its filename does not prove it is the final evaluated model. data1.yaml is absent.
- The paper identifies a D435i; the historical class is named RealsenseD435. The maintained module uses the librealsense colour-stream interface and does not infer the connected camera model from that historical name.
- The paper describes orientation from segmentation masks. Both the original DEMO and maintained sorter use a fixed grasp orientation.

## Reported results and validation boundary

On p.6 the paper reports 300 additional test images, 98.9% accuracy at IoU=0.7 and mean batch-one inference of 19.7 ms on the specified experimental computer. The abstract reports over 120 phones per hour for the complete system. These are paper results, not measurements of the refactored repository.

Repository verification covers offline logic, resource lifecycle, syntax, content integrity, documentation links and simulated connection workflow. No UR5e, VGC10 or RealSense was connected. Model evaluation, grasp experiments and complete-system throughput were not reproduced. The supplied PDF informed this mapping and is not republished.
