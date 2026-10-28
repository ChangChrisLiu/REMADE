# REMADE：废旧手机部件视觉监测与机器人分拣

[English](README.md) · [完整文档导航](docs/README.md)

本项目把相机看到的废旧手机部件转成机械臂可执行的抓取位置，再根据部件类别送往高价值或低价值区域。当前维护入口是 **`REMADEDEMO.py`**，原有实验脚本已归档，完整代码拆分在 `remade/` 中。

## 当前主流程

1. 启动一次 RealSense 彩色图像流，保持 1920×1080 分辨率。
2. 加载一次现有 YOLO 权重，持续检测并显示类别、置信度、检测框和实际循环 FPS。
3. 默认只监测；加 `--sort` 后，工作线程执行归位和分拣，主线程继续刷新画面。
4. 每次只取当前图像中的一个有效目标，抓取、分类放置、归位。
5. 丢弃动作期间缓存的图像，再采集新图像决定下一个目标，适用于需要逐层重新观察的场景。

主流程使用检测框中心和标定平面计算抓取位置；没有使用深度图直接恢复物体高度，也没有利用分割掩码估计抓取朝向。

## 启动方式

```bash
python -m pip install -r requirements.txt
python REMADEDEMO.py
```

启动实时监测窗口。按 Q、Esc 或关闭窗口退出。需要机械臂参与时：

```bash
python REMADEDEMO.py --sort --robot-ip 10.125.145.89
```

安装、硬件条件、参数、退出行为和故障排查见[运行说明](docs/OPERATIONS.md)。当前环境没有连接实验设备，因此离线测试通过不代表实机分拣已经验证。

## 代码结构

| 位置 | 职责 |
|---|---|
| [`REMADEDEMO.py`](REMADEDEMO.py) | 保留熟悉的启动文件名，转交给应用层 |
| [`remade/app.py`](remade/app.py) | 命令行参数、组件组装、启动失败处理 |
| [`remade/monitor.py`](remade/monitor.py) | 持续监测、单任务调度、退出和异常清理 |
| [`remade/vision.py`](remade/vision.py) | 相机流、YOLO 推理、OpenCV 窗口 |
| [`remade/geometry.py`](remade/geometry.py) | 旋转、相机/机械臂/标定平面的坐标变换 |
| [`remade/robot.py`](remade/robot.py) | TCP 报文读取、运动等待、单部件抓取放置 |
| [`remade/vacuum.py`](remade/vacuum.py) | Modbus 真空控制、串口桥接进程管理 |
| [`remade/config.py`](remade/config.py) | 类别、标定矩阵、固定工位、默认参数 |
| [`assets/`](assets/) | 模型、样例图、原有运行轨迹 |
| [`legacy/`](legacy/) | 原始研究实验和旧版入口，原始文件内容保留 |
| [`references/`](references/) | 三个第三方参考项目，保留来源和原有声明 |
| [`tests/`](tests/) | 与硬件隔离的自动化测试 |

## 与旧版相比

- 单次拍照改为持续采集、检测、显示；分拣执行不会同步阻塞画面。
- 相机和模型各初始化一次，退出时明确关闭。
- 模块导入不会连接机器人，默认运行也不会连接机器人。
- TCP 按报文长度读取，断开连接、非法报文和运动超时会报错。
- 先完成放置运动，再释放真空；Modbus 错误不再被忽略。
- 位姿和目标使用副本，避免改变共享工位数据。
- 真空桥接只管理本进程创建的 `socat`，不再执行全局 `pkill socat`。
- 默认速度设为 0.2 m/s、加速度 0.5 m/s²，采用旧代码注释中的较低参数；真空目标为可配置的 60%，替代旧脚本中含义不清的 `0xff`。这些新默认值仍需要实验验证。

## 研究范围

论文中的系统叫 **RAISE**，包含切割、视觉分拣和电池去除三个子系统。本仓库主要覆盖视觉分拣实验，另有翻转实验与离线轨迹文件。切割控制、冷却/敲击设备控制、完整训练数据和训练流水线没有包含在当前目录中。

论文阈值为 0.8，旧 `REMADEDEMO.py` 为 0.9；当前默认沿用 0.9，也可通过 `--confidence 0.8` 调整。论文中的性能数据与此处现有权重、重构代码之间不能直接画等号，详见[论文与代码对应表](docs/PAPER_MAPPING.md)。

建议阅读顺序：[项目架构](docs/ARCHITECTURE.md) → [代码导览](docs/CODE_GUIDE.md) → [运行说明](docs/OPERATIONS.md) → [代码审查](docs/CODE_REVIEW.md) → [资产与依赖](docs/ASSETS_AND_DEPENDENCIES.md)。
