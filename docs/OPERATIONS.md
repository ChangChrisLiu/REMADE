# 安装与运行

## 环境

维护主线使用 Python、NumPy、OpenCV、Ultralytics/PyTorch、RealSense SDK 和 pymodbus。建议在实验电脑使用 Python 3.10/3.11 的独立虚拟环境；测试还覆盖 Python 3.12。完整 runtime 依赖是根据模型元数据和旧 API 形成的候选版本范围，不是原实验环境的 lockfile。

```bash
python -m venv .venv
```

Linux 激活：`source .venv/bin/activate`。Windows PowerShell 激活：`.\.venv\Scripts\Activate.ps1`。然后：

```bash
python -m pip install -r requirements.txt
python REMADEDEMO.py --help
```

显示窗口需要桌面环境和 `opencv-python`，不能仅安装 headless 变体。RealSense 相机还需要可用的设备权限、USB 连接和支持的流配置。自动真空桥接使用 Linux 的 `socat`；Ubuntu 可通过 `sudo apt-get install socat` 安装。

## 实时监测

```bash
python REMADEDEMO.py
python -m remade --confidence 0.8 --fps 30
```

默认只使用相机和模型，不建立机器人或真空连接。画面显示检测框、类别、置信度和当前循环 FPS。请求的相机 FPS 与推理后可见 FPS 不同，实际速度由设备、USB、CPU/GPU 和模型决定。

模型通过相对项目根目录的绝对路径定位，所以从其他工作目录调用启动脚本也可找到默认权重。指定 `--weights` 时使用给出的路径。分拣模式还会核对模型的类别编号和名称是否与配置一致；替换模型时必须同步检查分拣路由。相机固定为 1920×1080，以匹配保留的标定内参；修改分辨率需要重新核对标定，而不是只调整显示窗口。

## 分拣模式

```bash
python REMADEDEMO.py --sort --robot-ip 10.125.145.89
```

需要 UR 控制器允许外部脚本控制、电脑可以访问 TCP 30003，以及 VGC10 工具串口可通过 54321 访问。程序为本次会话建立临时串口路径和独立 `socat` 进程。若已有串口连接，可指定：

```bash
python REMADEDEMO.py --sort --serial-device /dev/ttyUSB0
```

启动后先归位；每次检测选择首个有效类别目标，完成抓取、分类放置和归位，再观察下一个。动作期间仍有连续监测。单个目标完成后重新检测，可以避免沿用上一帧的整批位姿。

机械臂的基座、相机安装、TCP、夹具、工作台及放置工位必须与 [config.py](../remade/config.py) 中的标定对应。程序不提供在线避障、工件存在传感确认、真空吸附成功判定或相机外参自动更新。Modbus 应答只表示控制器接受了命令。

## 参数与变化

| 参数 | 默认 | 含义 |
|---|---|---|
| `--weights` | `assets/models/smallmodeldet.pt` | 原有模型 |
| `--confidence` | 0.9 | 沿用旧 DEMO；论文描述为 0.8 |
| `--fps` | 30 | 请求相机帧率，具体支持情况由相机决定 |
| `--robot-ip` | 10.125.145.89 | 原实验控制器地址 |
| `--speed` | 0.2 | m/s；旧 DEMO 普通动作使用 2.5 |
| `--acceleration` | 0.5 | m/s²；旧 DEMO 普通动作使用 2.5 |
| `--vacuum-percent` | 60 | 两通道目标百分比，范围 1–80 |
| `--serial-device` | 自动桥接 | 已存在的串口设备 |

速度/加速度采用旧脚本注释中的较低值；60% 真空取值与历史夹具实验一致，取代旧 VG 代码中的 `0xff` 指令值。这些设置没有经过本次实机验证。若恢复旧实验速度，应以重新验证的工位和设备限制为依据。

## 退出和错误

Q、Esc、关闭窗口或 Ctrl+C 触发结束。程序停止提交目标，要求工作线程停止，向机器人发送 `stopl`，关闭串口和桥接、相机与窗口。不会主动释放可能在途的工件。软件停止受连接与驱动状态影响，不能替代设备急停。

| 现象 | 检查位置 |
|---|---|
| 找不到模型 | `--weights` 路径和 assets 校验清单 |
| 相机流配置失败或收不到帧 | USB、设备权限、被其他程序占用、`--fps` 支持情况 |
| OpenCV 窗口失败 | 是否有桌面环境，是否误装 headless 包 |
| 模型加载兼容性错误 | checkpoint 的 Ultralytics 8.2.41 与实际安装版本；不要直接升级所有依赖 |
| 无法导入 `pymodbus.client.sync` | 主线使用 pymodbus 2.5.3 API，不兼容直接替换为 3.x |
| 真空桥接失败 | Linux/socat、控制器工具串口转发、54321 端口、串口权限 |
| 机器人未到位超时 | 设备状态、外部控制权限、工位坐标、保护停止；程序停止新动作并报错 |

## 离线验证

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python tools/check_repository.py
```

不要在仓库根目录导入或执行所有名字带 `test` 的文件来验证项目：`legacy/` 与 `references/` 中这些文件通常是设备实验。`pytest.ini` 同样将 pytest 发现范围限制在 `tests/`。
