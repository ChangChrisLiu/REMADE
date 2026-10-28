# 逐文件代码导览

## 正式维护模块

| 文件 | 主要接口 | 职责与边界 |
|---|---|---|
| [启动文件](../REMADEDEMO.py) | `main(argv)` | 兼容原入口名称，不包含控制流程 |
| [app](../remade/app.py) | `parser()`、`main(argv)` | 参数检查、资源创建、监测/分拣选择、退出码 |
| [monitor](../remade/monitor.py) | `run_monitor`、`StopRequested` | 主线程图像循环、单工作线程、最新帧策略、异常传递 |
| [vision](../remade/vision.py) | `RealSenseStream`、`Detector`、`OpenCVDisplay`、`DetectionFrame` | 硬件图像、推理、窗口接口 |
| [geometry](../remade/geometry.py) | `rotation_matrix`、`rotation_error`、`project_pixel_to_plane`、`detections_to_poses` | 可离线验证的数学逻辑 |
| [robot](../remade/robot.py) | `read_tcp_pose`、`URSocket`、`Sorter` | 带超时的通信与运动；一个目标一轮 |
| [vacuum](../remade/vacuum.py) | `VacuumController` | 两通道命令、Modbus 应答检查、受控桥接生命周期 |
| [config](../remade/config.py) | `Settings`、标定/类别常量 | 工位参数与运行配置集中定义 |

`remade/__init__.py` 只定义包说明与版本，`remade/__main__.py` 支持 `python -m remade`。模块导入不启动硬件。完整函数与类的行号见 [CODE_INDEX.md](CODE_INDEX.md)。

## 原始主线与实验（legacy/scripts）

以下文件保留原始源码内容，Git 仅可能规范文本行尾，作为研究历史和对照材料。它们不是新主流程依赖，也不纳入测试发现范围。部分文件在导入时就会操作设备；移动后原相对资源路径也不再构成可直接运行的环境。

| 原脚本 | 实际功能/区别 |
|---|---|
| [REMADE.py](../legacy/scripts/REMADE.py) | 固定六组检测坐标的分拣原型；虽然定义 YOLO 函数，`Image2TCP()` 实际使用固定矩阵 |
| [REMADEDEMO.py](../legacy/scripts/REMADEDEMO.py) | 本次维护主线的来源；单次真实拍照、阈值 0.9、整批抓取后结束 |
| [REMADETEST.py](../legacy/scripts/REMADETEST.py) | 连续拍照/分拣实验，阈值 0.8；还在顶层连接 `127.0.0.1` 的 RTDE 接口 |
| [runwithpath.py](../legacy/scripts/runwithpath.py) | `ur_rtde` 接口 + 已保存关节轨迹，持续分拣；修改轨迹行的缺陷已记录 |
| [standardpickup.py](../legacy/scripts/standardpickup.py) | 与 runwithpath 几乎相同；`move_to_tcp_slow` 使用全局速度/加速度，不能按函数名假设为低速 |
| [visitdemortde.py](../legacy/scripts/visitdemortde.py) | RTDE 笛卡尔路径演示；路径由源码里的中间工位构造，持续拍照分拣 |
| [visitdemo.py](../legacy/scripts/visitdemo.py) | 含翻转和视觉函数，当前启用的主程序只有 `go_home()`；多数演示动作被注释 |
| [fliptest.py](../legacy/scripts/fliptest.py) | 固定位置的插入、释放、重新抓取和翻转动作序列；未接入类别触发闭环 |
| [Fulltest.py](../legacy/scripts/Fulltest.py) | 早期 urx/ROS2/坐标变换实验，主程序连接并打印位姿；并非完整新主程序 |
| [ootest1.py](../legacy/scripts/ootest1.py) | 早期视觉与抓取函数草稿，无启用的主循环，变换形状存在问题 |
| [cameratest.py](../legacy/scripts/cameratest.py) | `RealsenseD435` 彩色相机封装；每次获取都新建管线，无明确停止 |
| [imagete.py](../legacy/scripts/imagete.py) | 从硬编码 Linux 路径读取图像并做检测，顶层执行 |
| [onrobot.py](../legacy/scripts/onrobot.py) | `VG` 的 TCP/串口 Modbus 封装、两通道开关和压力寄存器 |
| [VacuumOn.py](../legacy/scripts/VacuumOn.py) | 顶层打开 `/tmp/ttyUR` 并启动真空 |
| [VacuumOff.py](../legacy/scripts/VacuumOff.py) | 顶层打开 `/tmp/ttyUR` 并释放真空 |
| [util.py](../legacy/scripts/util.py) | 旋转向量、旋转矩阵、RPY 互转；零角和 π 附近存在奇异问题 |
| [rtde.py](../legacy/scripts/rtde.py) | 旧版 UR RTDE 协议实现；不是 pip 包 `ur-rtde` 的 `rtde_control` |
| [serialize.py](../legacy/scripts/serialize.py) | 上述旧 RTDE 的报文类型和数据序列化 |
| [manipulation.py](../legacy/scripts/manipulation.py) | ROS1 + urx + Robotiq 双指夹爪的动作帮助函数，与 VGC10 主线不同 |
| [urxtest.py](../legacy/scripts/urxtest.py) | urx 连接与位姿读取实验，顶层连接机器人 |
| [test.py](../legacy/scripts/test.py) | 机器人 TCP/关节状态读取和移动帮助函数，顶层读取真实状态 |
| [test1.py](../legacy/scripts/test1.py) | RTDE 连接与混合半径路径格式实验，顶层加载轨迹与连接设备 |
| [toc.py](../legacy/scripts/toc.py) | PyTorch CUDA 可用性输出，不是训练脚本 |

[VacuumOnscript.sh](../legacy/scripts/VacuumOnscript.sh) 和 [VacuumOffscript.sh](../legacy/scripts/VacuumOffscript.sh) 是旧式 Bash/socat 调用链，含全局 `pkill socat`；新主流程使用 `remade.vacuum`。

## 轨迹与夹具实验

| 文件 | 功能 |
|---|---|
| [trajectory_tools/convert_paths.py](../legacy/trajectory_tools/convert_paths.py) | 将每个路点的第一个关节加 π/2，输出转换轨迹 |
| [trajectory_tools/start_to_high.py](../legacy/trajectory_tools/start_to_high.py) | 当前启用代码只加载并打印轨迹，机器人部分被注释 |
| [trajectory_tools/start_to_low.py](../legacy/trajectory_tools/start_to_low.py) | urx 连接并逐点执行去低价值工位路径 |
| [trajectory_tools/high_to_home.py](../legacy/trajectory_tools/high_to_home.py) | 高价值工位返回路径执行 |
| [trajectory_tools/low_to_home.py](../legacy/trajectory_tools/low_to_home.py) | 低价值工位返回路径执行 |
| [vacuum/onrobot.py](../legacy/vacuum/onrobot.py) | 另一份历史 VG 实现，保留差异 |
| [vacuum/VacuumOn.py](../legacy/vacuum/VacuumOn.py) | 夹具开启实验 |
| [vacuum/VacuumOff.py](../legacy/vacuum/VacuumOff.py) | 夹具关闭实验 |
| [vacuum/demotest.py](../legacy/vacuum/demotest.py) | 调用 Bash 开真空，等待，再关闭 |
| [gripper_tests/demo.py](../legacy/gripper_tests/demo.py) | 带 TCP 参数解析的 VG 演示 |
| [gripper_tests/onrobot.py](../legacy/gripper_tests/onrobot.py) | 历史 VG 实现副本 |
| [gripper_tests/sockettest.py](../legacy/gripper_tests/sockettest.py) | 机器人 socket 通信试验，顶层运行 |
| [gripper_tests/test.py](../legacy/gripper_tests/test.py) | ROS2/urx/TCP 与载荷参数实验 |
| [gripper_tests/test111.py](../legacy/gripper_tests/test111.py) | VGC10 URScript 指令封装；含 property 参数错误 |
| [gripper_tests/testgripper.py](../legacy/gripper_tests/testgripper.py) | urx 发送 VGC10 抓取与释放 URScript |
| [gripper_tests/testvacuum.py](../legacy/gripper_tests/testvacuum.py) | A/B 两通道真空开关与反馈演示 |

其中 shell 脚本和无扩展名的 `ros code` 同样保留，逐个路径见迁移清单。

## 第三方参考（references）

| 参考项目 | 内部结构和作用 |
|---|---|
| [UR5-control-with-RG2](../references/UR5-control-with-RG2/README.md) | `test_main.py` 直接 socket 控制；`util.py` 旋转辅助；`rtde.py`/`serialize.py` 旧官方协议示例。原项目三份同名工具与该参考逐字节一致 |
| [UR5-robotiq85-D435_control_by_python](../references/UR5-robotiq85-D435_control_by_python/README.md) | `UR_Robot.py` 合并机械臂、相机与 Robotiq 控制；`real/` 包含相机、夹爪、标定和独立实验 |
| [arws](../references/arws/README.md) | 水果采摘 ROS2 参考系统：UR3e、OAK-D Pro、RG2；不能当作本项目 D435i/VGC10 的启动配置 |

arws 的 `camera_control_node` 发布 `custom_camera`，自定义 `URCommand.msg` 包含 string 类型的 x/y/depth；C++ `ur_mover/src/master_node.cpp` 使用 MoveIt 计算并执行笛卡尔路径；`gripper_control_node` 订阅夹爪指令并与 dashboard 服务配合。

arws 内还包含 Universal Robots ROS2 Driver 与 Description：驱动、标定、控制器、dashboard 消息、MoveIt 配置、机器人描述、网格和 launch 文件。它们保留在参考快照中，没有被复制进新的应用模块，也没有在本次任务中逐行认证为可部署驱动。
