# 资产、依赖与来源

## 模型与图像

| 路径 | 内容 | 主线使用 |
|---|---|---|
| `assets/models/smallmodeldet.pt` | 23,850,851 字节的原有分割 checkpoint | 是 |
| `assets/images/001_Color.png` | 原实验样例彩色图 | 文档/离线材料；主线使用实时相机 |
| `references/arws/yolov8n.pt` | 水果采摘参考目录内的模型 | 否 |
| `references/arws/src/camera_control/camera_control/scripts/yolov8n.pt` | 参考模型的另一份副本 | 否 |

主模型虽然名为 `smallmodeldet.pt`，静态元数据标识为 Ultralytics `SegmentationModel`。现有主线只使用 bounding boxes。训练数据、`data1.yaml`、训练命令和最终论文评估权重身份没有在当前目录中闭合，不能只凭文件名认定可完整复现训练。

[assets.csv](inventory/assets.csv) 记录 `.pt`、`.pkl` 和原样例图的大小与 SHA-256。检查仅读取字节，不执行 pickle 或 PyTorch 反序列化。

## 轨迹

- `assets/trajectories/runtime/`：原根目录 `paths_for_demo/`，包含 start_to_high、start_to_low、high_to_home、low_to_home 四个文件。
- `legacy/trajectory_tools/original_paths/`：原始轨迹。
- `legacy/trajectory_tools/paths_for_demo/`：原 `04/` 内的转换轨迹副本。
- `legacy/trajectory_tools/convert_paths.py` 的转换规则：每个路点的第一个关节加 π/2，其余保持。

旧函数注释称轨迹来自 MPNet，但没有包含 MPNet 模型、训练代码、规划器或碰撞环境。当前维护入口走旧 DEMO 的笛卡尔抓取流程，不读取这些 pickle 轨迹。不要把“轨迹文件存在”解释为“本项目已提供完整规划系统”。

## 主线依赖

| 依赖 | 用途 | 版本决策 |
|---|---|---|
| NumPy | 数值与坐标变换 | 1.24 到 2.0 之前，兼容历史栈 |
| OpenCV | 框图显示、窗口和键盘输入 | 使用有 GUI 的 opencv-python；版本范围见 requirements |
| Ultralytics | YOLO checkpoint 推理 | 固定 8.2.41，与 checkpoint 元数据一致 |
| PyTorch / torchvision | 模型执行 | 候选匹配范围分别 2.2–2.5 / 0.17–0.20；并非原环境精确锁定 |
| pyrealsense2 | RealSense 彩色流 | 2.x SDK；实际设备支持需验证 |
| pymodbus | VGC10 Modbus RTU | 2.5.3；保留 `pymodbus.client.sync` 接口 |
| pyserial | 串口实现 | 3.x |
| socat（系统程序） | TCP 工具串口桥接 | 自动桥接模式在 Linux 使用 |

候选依赖使用历史版本以兼容既有模型，不承诺是最新软件组合。PyTorch 新版 checkpoint 加载行为有变化，后续迁移应验证模型格式与版本，不应通过全局关闭校验来绕过兼容性问题。

监测显示使用 BGR 图像；Ultralytics 的 NumPy 输入和 plot 输出约定见[官方推理说明](https://docs.ultralytics.com/modes/predict/)。RealSense 管线生命周期依据 [librealsense Python pipeline 定义](https://github.com/realsenseai/librealsense/blob/master/wrappers/python/pyrs_pipeline.cpp)。

## 历史依赖

urx、ur-rtde、ROS1 `rospy`、ROS2 `rclpy`/MoveIt、DepthAI、supervision、SciPy、scikit-learn 等只出现在历史实验或参考系统中，不应为了运行新 DEMO 将它们全部混装进一个环境。参考 ROS2 项目使用不同硬件与独立工作区，按其 README 另行理解。

## 保存策略

旧本地目录不是主 Git 仓库；原远端只有一个 README 提交。现在以该提交为父历史导入项目，保留原仓库身份。461 个原始可发布文件均在[迁移清单](inventory/migration.csv)中记录：旧路径、新路径、原字节 hash、跨平台文本规范化 hash。编辑器配置、字节码缓存和嵌套 `.git` 历史留在本地，不纳入源码快照。

参考仓库同时包含上游内容和原来尚未提交的本地修改；它们都作为文件快照保存，原上游提交和修改状态记录在 [references.json](inventory/references.json) 中。没有把修改直接提交到第三方仓库，也没有创建指向未知本地提交的 gitlink。
