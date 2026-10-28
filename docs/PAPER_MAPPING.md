# RAISE 论文与 REMADE 代码对应

来源：用户提供的 **RAISE: A Robot-Assisted SelectIve Disassembly and Sorting System for End-of-Life Phones**，Chang Liu 等，*Resources, Conservation & Recycling* 225 (2026), 108609；[DOI](https://doi.org/10.1016/j.resconrec.2025.108609)。论文在线发表日期为 2025-10-10。以下页码按所提供 PDF 的 10 页版本。

论文是项目背景和实验依据，不是修改代码的指令。仓库统一命名为 REMADE；论文系统名 RAISE 保留在引用中。

## 系统范围

| 论文内容 | 证据位置 | 当前代码对应 | 实现状态 |
|---|---|---|---|
| 自适应切割系统 | 第 3 节、图 1，p.3–4 | 没有对应的切割设备控制模块 | 当前目录未提供 |
| UR5e + VGC10 + D435i 视觉分拣 | §3.2，p.4–5 | `remade/robot.py`、`vacuum.py`、`vision.py` | 维护主线覆盖基本控制与持续监测 |
| 手眼标定 | §3.2.1，p.5 | `config.py` 的矩阵；`geometry.py` 的变换 | 保留已有标定结果；未重新标定 |
| YOLOv8 检测与实例分割 | §3.2.2，图 3，p.5 | `smallmodeldet.pt` 为分割模型 | 推理使用类别和框中心，未用掩码求方向 |
| 普通壳、膜、屏幕进入低价值区 | §3.2.3、§4.2.1，p.5–6 | 类别 0/1/3 → LOW_BIN | 已实现 |
| 中间层、iPhone 壳进入高价值处理链 | §3.2.3，p.5 | 类别 2/4 → HIGH_BIN | 当前只是高价值工位放置 |
| iPhone 壳翻转 | 图 4(m–u)，p.6 | `legacy/scripts/fliptest.py` 固定位置实验 | 未接入主流程的类别触发逻辑 |
| 冷却、摆锤去电池与后续回收 | §3.3，p.5 | 未发现温控/摆锤控制和联锁模块 | 当前目录未提供 |
| 数据集、训练和完整评估 | §4.2.1–4.2.2，p.5–6 | 提供一个主模型和一张示例图 | 缺少训练集、标签和完整训练流水线 |

## 五类标签

标签来自主 checkpoint 的静态 pickle 指令文本检查，没有执行模型反序列化。

| ID | checkpoint 标签 | 论文描述 | 当前路由 |
|---|---|---|---|
| 0 | Case | normal case | 低价值 |
| 1 | Film | film | 低价值 |
| 2 | High Value Middle | middle layer | 高价值 |
| 3 | Screen | screen | 低价值 |
| 4 | iPhone Case | iPhone case | 高价值；未自动翻转 |

## 需要区分的版本信息

- 论文 p.6 描述实际置信度阈值为 0.8；原 `REMADEDEMO.py` 为 0.9，`REMADETEST.py` 为 0.8。新入口默认 0.9，可由命令行调整。
- checkpoint 的模型类型为 `SegmentationModel`，训练配置含 `yolov8s-seg.pt`、`data1.yaml`、epochs=200、imgsz=640、batch=16，版本为 Ultralytics 8.2.41，时间字符串为 2024-06-25T06:02:22.417885。
- 论文 p.6 描述训练 100 epochs、batch size 16。现有 checkpoint 可能来自不同实验阶段；仅凭文件名无法确认它就是论文最终评估模型。`data1.yaml` 未随本目录提供。
- 论文使用 D435i；历史相机类名是 `RealsenseD435`。新模块使用 librealsense 彩色流接口，不据类名推断实际连接相机型号。
- 论文描述分割掩码提供部件方向；旧 DEMO 和新主线都使用固定抓取姿态，没有从掩码推导朝向。

## 实验结果的归属

论文 p.6 给出额外 300 张测试图、IoU=0.7 时 98.9% accuracy，以及指定实验电脑上 batch=1 平均推理时间 19.7 ms；摘要报告整套系统每小时超过 120 部手机。它们是论文中相应实验的结果，不能视为此处重构后软件的测试结果。

本次验证只覆盖离线逻辑、资源生命周期、语法、文件完整性和文档链接。没有连接 UR5e、VGC10 或 RealSense，也没有重跑模型评估、抓取实验或整套拆解吞吐量测量。论文 PDF 仅用于理解项目，未加入公开仓库。
