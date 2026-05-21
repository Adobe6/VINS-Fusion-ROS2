# VINS-Fusion

## VINS-Fusion 的 ROS2 版本

### 注意事项
- 代码已更新，vins 包可通过 `ros2 run` 或 `ros2 launch` 执行
- 但 Rviz 配置因某些问题无法保存，仍在修复中
- GPU 启用/禁用功能也已添加：参考 [EuRoC 配置](https://github.com/zinuok/VINS-Fusion-ROS2/blob/main/config/euroc/euroc_stereo_imu_config.yaml#L19-L21)（参考来源：[此处](https://github.com/pjrambo/VINS-Fusion-gpu) 和 [此处](https://github.com/pjrambo/VINS-Fusion-gpu/issues/33#issuecomment-1097642597)）
  - GPU 版本有一些 CUDA 库[依赖：带 CUDA 的 OpenCV](https://github.com/zinuok/VINS-Fusion-ROS2/blob/main/vins/src/featureTracker/feature_tracker.h#L21-L23)。因此，如果你觉得麻烦且只需要 CPU 版本，请在 `feature_tracker.h` 第 14 行注释掉以下编译宏：
  ```bash
  #define GPU_MODE 1
  ```

### 前置依赖
- **系统**
  - Ubuntu 20.04
  - ROS2 Foxy
- **库**
  - OpenCV 3.4.1（可选启用 CUDA）
  - OpenCV 3.4.1-contrib
  - [Ceres Solver-2.1.0](http://ceres-solver.org/installation.html)（可参考[此处](https://github.com/zinuok/VINS-Fusion#-ceres-solver-1)；安装时只需将 1.14.0 改为 2.1.0）
  - [Eigen-3.3.9](https://github.com/zinuok/VINS-Fusion#-eigen-1)

### 传感器设置
- 相机：Intel RealSense D435i
- 使用以下 Shell 脚本可以安装带 ROS2 包的 RealSense SDK：
```bash
chmod +x realsense_install.sh
bash realsense_install.sh
```

### 编译构建
```bash
cd $(PATH_TO_YOUR_ROS2_WS)/src
git clone https://github.com/zinuok/VINS-Fusion-ROS2
cd ..
colcon build --symlink-install && source ./install/setup.bash && source ./install/local_setup.bash
```

### 运行
```bash
# vins
ros2 run vins $(PATH_TO_YOUR_VINS_CONFIG_FILE)

# Rviz2 可视化
ros2 launch vins vins_rviz.launch.xml
```

## 播放 ROS1 录制的 bag 文件
不幸的是，你不能直接播放 ROS1 录制的 bag 文件。
这是因为 bag 文件的文件系统结构发生了显著变化。
ROS2 的 bag 文件需要为每个 bag 文件准备包含元数据的文件夹，可通过以下命令完成：
- 你需要安装[这个包](https://gitlab.com/ternaris/rosbags)
```bash
pip install rosbags
```

- 运行
```bash
export PATH=$PATH:~/.local/bin
rosbags-convert foo.bag --dst /path/to/bar
```

## 原始 README：

## 8. 致谢
我们使用了 [Ceres Solver](http://ceres-solver.org/) 进行非线性优化，[DBoW2](https://github.com/dorian3d/DBoW2) 进行回环检测，以及通用[相机模型](https://github.com/hengli/camodocal)和 [GeographicLib](https://geographiclib.sourceforge.io/)。

## 9. 许可证
源代码基于 [GPLv3](http://www.gnu.org/licenses/) 许可证发布。

我们仍在努力提高代码的可靠性。如有任何技术问题，请联系 Tong Qin <qintonguavATgmail.com>。

商业咨询请联系 Shaojie Shen <eeshaojieATust.hk>。
