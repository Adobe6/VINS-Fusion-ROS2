# VINS-Fusion-ROS2 — OAK-D Lite 适配版

基于 [VINS-Fusion-ROS2](https://github.com/zinuok/VINS-Fusion-ROS2) 修改，适配 **Ubuntu 22.04 / ROS2 Humble** 和 **Luxonis OAK-D Lite 相机**。

---

## 项目结构

```
ros2_ws/src/VINS-Fusion-ROS2/
├── vins/                          # VIO 估计节点
│   ├── src/
│   │   ├── estimator/             # 核心状态估计器
│   │   ├── featureTracker/        # 特征追踪（光流）
│   │   ├── factor/                # Ceres 优化因子
│   │   ├── initial/               # 初始化（SFM + IMU对齐）
│   │   ├── utility/               # 可视化工具
│   │   ├── rosNodeTest.cpp        # 主节点（订阅图像+IMU）
│   │   ├── KITTIOdomTest.cpp      # KITTI 离线测试
│   │   └── KITTIGPSTest.cpp       # KITTI GPS 测试
│   └── launch/
│       ├── euroc.launch.py        # EuRoC 数据集启动
│       └── vins_rviz.launch.py    # RViz2 可视化启动
│
├── loop_fusion/                   # 回环检测节点
│   ├── src/
│   │   ├── pose_graph.cpp         # 位姿图优化（4DoF/6DoF）
│   │   ├── pose_graph_node.cpp    # 回环检测主节点
│   │   ├── keyframe.cpp           # 关键帧管理
│   │   └── ThirdParty/            # DBoW2 + BRIEF 词库
│   └── support_files/             # 词库文件（已安装到 install 目录）
│
├── global_fusion/                 # GPS+VIO 全局融合（本适配未使用）
│
├── camera_models/                 # 相机标定模型库（camodocal）
│
├── oak_d_lite_driver/             # OAK-D Lite Python 驱动（新增）
│   ├── oak_d_lite_driver/
│   │   └── oak_d_lite_node.py     # 相机+IMU 数据发布节点
│   └── launch/
│       └── oak_d_lite_vins.launch.py  # 一键启动所有节点
│
├── config/
│   ├── oak_d_lite/                # OAK-D Lite 配置（新增）
│   │   ├── oak_d_lite_config.yaml # VINS 主配置文件
│   │   ├── cam0_pinhole.yaml      # 左目相机内参
│   │   └── cam1_pinhole.yaml      # 右目相机内参
│   ├── euroc/                     # EuRoC 数据集配置（参考）
│   ├── realsense_d435i/           # RealSense D435i 配置（参考）
│   ├── kitti_odom/                # KITTI 数据集配置（参考）
│   └── vins_rviz_config.rviz      # RViz 可视化配置
│
├── scripts/
│   └── extract_oak_calib.py       # OAK-D Lite 标定提取脚本（一次性）
│
└── support_files/                 # 回环检测词库文件
    ├── brief_k10L6.bin            # DBoW2 视觉词库（60MB）
    └── brief_pattern.yml          # BRIEF 特征模板
```

---

## 前置依赖

| 软件 | 版本 |
|------|------|
| Ubuntu | 22.04 |
| ROS2 | Humble |
| OpenCV | 系统自带 4.5.4 |
| Ceres Solver | 系统自带 2.0.0（已做代码兼容） |
| Eigen | 系统自带 3.4.0 |
| depthai Python | 3.6.1（pip 安装） |

```bash
# 安装 ROS2 依赖
sudo apt install ros-humble-cv-bridge ros-humble-image-transport

# 安装 depthai Python 包
pip install depthai
```

---

## 编译

```bash
# 1. 创建工作空间（已有则跳过）
mkdir -p ~/ros2_ws/src

# 2. 克隆本仓库
cd ~/ros2_ws/src
git clone https://github.com/Adobe6/VINS-Fusion-ROS2.git

# 3. 编译
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install

# 4. source 环境
source ~/ros2_ws/install/setup.bash
```

---

## 使用方式

### 1. 连接 OAK-D Lite 真机运行

```bash
source ~/ros2_ws/install/setup.bash

# 一键启动（驱动 + VINS + 回环检测 + RViz）
ros2 launch oak_d_lite_driver oak_d_lite_vins.launch.py
```

### 2. KITTI 数据集离线测试

```bash
# 先下载 KITTI Odometry 数据集
# https://www.cvlibs.net/datasets/kitti/eval_odometry.php

# 运行测试
ros2 run vins kitti_odom_test \
  ~/ros2_ws/src/VINS-Fusion-ROS2/config/kitti_odom/kitti_config00-02.yaml \
  /path/to/kitti/odometry/sequences/00/
```

### 3. EuRoC 数据集测试

```bash
# 下载 EuRoC MAV 数据集 bag 文件
# https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets

ros2 launch vins euroc.launch.py
# 另开终端播放 bag
ros2 bag play euroc_mav_bag.bag
```

---

## 配置说明

### OAK-D Lite 配置文件

`config/oak_d_lite/oak_d_lite_config.yaml` 中关键参数：

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `imu_topic` | `/imu` | IMU 数据话题 |
| `image0_topic` | `/cam0/image_raw` | 左目相机话题 |
| `image1_topic` | `/cam1/image_raw` | 右目相机话题 |
| `estimate_extrinsic` | 1 | 在线优化 IMU-相机外参 |
| `estimate_td` | 1 | 在线估计时间偏移 |
| `acc_n` | 0.08 | 加速度计噪声密度 |
| `gyr_n` | 0.004 | 陀螺仪噪声密度 |

### 相机驱动频率

`oak_d_lite_driver/oak_d_lite_driver/oak_d_lite_node.py` 顶部可调：

```python
FPS = 30       # 相机帧率
IMU_FREQ = 100 # IMU 频率 (Hz)
```

### 点云密度调整

`config/oak_d_lite/oak_d_lite_config.yaml` 中修改：

| 参数 | 当前值 | 调大密度建议 | 说明 |
|------|--------|-------------|------|
| `max_cnt` | 150 | **300 ~ 500** | 最大追踪特征点数，越大点云越密 |
| `min_dist` | 30 | **15 ~ 20** | 特征点最小间距（像素），越小点分布越密 |

示例（密度提升 2~4 倍）：
```yaml
max_cnt: 300
min_dist: 15
```

注意：点云越密，CPU 负载越高，`max_solver_time: 0.04` 限制了每次优化时间，特征过多时可能会跳过部分优化。

---

## 已修复的兼容性问题

本仓库已在 Ubuntu 22.04 / ROS2 Humble 环境下修复了以下问题：

| 问题 | 原因 | 修复方式 |
|------|------|---------|
| `rclcpp::Duration(0, 0)` 编译错误 | Humble 移除了该构造函数 | 改为 `Duration::from_nanoseconds(0)` |
| `ceres::Manifold` 不存在 | apt 安装的是 Ceres 2.0 | 改为 `LocalParameterization` API |
| `ceres::CUDA` 不存在 | Humble 的 Ceres 不含 CUDA | 改为 `ceres::EIGEN` |
| `cv_bridge.hpp` 找不到 | Humble 使用 `.h` 后缀 | depthai-ros 中改为 `cv_bridge.h` |
| 回环检测词库未安装 | CMakeLists 缺少 install 规则 | 添加 support_files 安装 |

---

## RViz 可视化

启动 RViz 后默认显示：

| 面板 | 话题 | 说明 |
|------|------|------|
| `tracked_image` | `/image_track` | 特征追踪可视化 |
| `raw_image` | `/cam0/image_raw` | 原始左目画面 |
| `Path` | `/path` | VIO 轨迹路径 |
| 点云 | `/point_cloud` | 当前特征点云 |
| TF | — | 坐标系（world → body → camera） |

回环检测话题（需 `loop_fusion_node` 运行）：

| 话题 | 说明 |
|------|------|
| `/pose_graph/pose_graph_path` | 全局优化轨迹 |
| `/pose_graph/match_image` | 回环匹配图像 |
| `/pose_graph/camera_pose_visual` | 关键帧位姿 |

---

## 已知限制

- OAK-D Lite 相机帧率受 USB 带宽影响，实际可能低于设定值
- 回环检测需要走同一区域两次才能触发
- `global_fusion` 节点需要 GPS 硬件，本配置不含
- Ubuntu 22.04 / ROS2 Humble 上编译后有少量 deprecated API 警告，不影响运行

---

## 快速启动（终端命令速查）

### 一键启动（OAK-D Lite 真机 + VINS + 回环 + RViz）

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch oak_d_lite_driver oak_d_lite_vins.launch.py
```

### 分别启动（调试用）

```bash
# 终端 1 — 相机驱动
source ~/ros2_ws/install/setup.bash
ros2 run oak_d_lite_driver oak_d_lite_node

# 终端 2 — VINS 定位
source ~/ros2_ws/install/setup.bash
ros2 run vins vins_node \
  ~/ros2_ws/src/VINS-Fusion-ROS2/config/oak_d_lite/oak_d_lite_config.yaml

# 终端 3 — 回环检测
source ~/ros2_ws/install/setup.bash
ros2 run loop_fusion loop_fusion_node \
  ~/ros2_ws/src/VINS-Fusion-ROS2/config/oak_d_lite/oak_d_lite_config.yaml

# 终端 4 — RViz 可视化
source ~/ros2_ws/install/setup.bash
ros2 launch vins vins_rviz.launch.py
```

### KITTI 数据集离线测试

```bash
source ~/ros2_ws/install/setup.bash
ros2 run vins kitti_odom_test \
  ~/ros2_ws/src/VINS-Fusion-ROS2/config/kitti_odom/kitti_config00-02.yaml \
  /path/to/kitti/odometry/sequences/00/
```
