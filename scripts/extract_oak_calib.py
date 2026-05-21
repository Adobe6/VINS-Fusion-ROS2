#!/usr/bin/env python3
"""从 OAK-D Lite 工厂标定提取参数，生成 VINS-Fusion 配置文件。
depthai-ros 发布的 left/right/image_rect 已是校正后图像，畸变系数全部设为零。"""

import depthai as dai
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "config", "oak_d_lite")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 640, 480

CAM_LEFT  = dai.CameraBoardSocket.CAM_B
CAM_RIGHT = dai.CameraBoardSocket.CAM_C

def mat4_to_list(m):
    m = np.asarray(m, dtype=np.float64)
    return [float(v) for v in m.flatten()[:16]]

def write_pinhole_yaml(path, name, K, w, h):
    fx, fy = K[0,0], K[1,1]
    cx, cy = K[0,2], K[1,2]
    with open(path, "w") as f:
        f.write("%YAML:1.0\n---\n")
        f.write(f"model_type: PINHOLE\n")
        f.write(f"camera_name: {name}\n")
        f.write(f"image_width: {w}\n")
        f.write(f"image_height: {h}\n")
        f.write("distortion_parameters:\n")
        f.write("   k1: 0.0\n")
        f.write("   k2: 0.0\n")
        f.write("   p1: 0.0\n")
        f.write("   p2: 0.0\n")
        f.write("projection_parameters:\n")
        f.write(f"   fx: {fx:.15f}\n")
        f.write(f"   fy: {fy:.15f}\n")
        f.write(f"   cx: {cx:.15f}\n")
        f.write(f"   cy: {cy:.15f}\n")
    print(f"  -> {os.path.relpath(path)}")

print("正在连接 OAK-D Lite ...")
with dai.Device() as device:
    calib = device.readCalibration()
    print(f"  已连接 (depthai {dai.__version__})")
    sensors = device.getConnectedCameraFeatures()
    for s in sensors:
        print(f"    传感器: {s.sensorName}")

    # ---- 1. 内参 ----
    K_left  = np.array(calib.getCameraIntrinsics(CAM_LEFT, W, H), dtype=np.float64)
    K_right = np.array(calib.getCameraIntrinsics(CAM_RIGHT, W, H), dtype=np.float64)

    # ---- 2. 外参 IMU → Camera (body_T_cam) ----
    try:
        body_T_cam0 = np.array(calib.getImuToCameraExtrinsics(CAM_LEFT), dtype=np.float64)
    except Exception as e:
        print(f"  body_T_cam0 读取失败: {e}")
        body_T_cam0 = np.eye(4)
    try:
        body_T_cam1 = np.array(calib.getImuToCameraExtrinsics(CAM_RIGHT), dtype=np.float64)
    except Exception as e:
        print(f"  body_T_cam1 读取失败: {e}")
        body_T_cam1 = np.eye(4)

    baseline_mm = calib.getBaselineDistance()

    # ---- 3. 打印 ----
    print(f"\n基线距离: {baseline_mm} mm\n")
    print("【左目】")
    print(K_left)
    print("\n【右目】")
    print(K_right)
    print("\n【body_T_cam0 (IMU→左目)】")
    print(body_T_cam0)
    print("\n【body_T_cam1 (IMU→右目)】")
    print(body_T_cam1)

    # ---- 4. 写文件 ----
    print("\n生成配置文件:")
    write_pinhole_yaml(os.path.join(OUTPUT_DIR, "cam0_pinhole.yaml"),
                       "left", K_left, W, H)
    write_pinhole_yaml(os.path.join(OUTPUT_DIR, "cam1_pinhole.yaml"),
                       "right", K_right, W, H)

    cfg = os.path.join(OUTPUT_DIR, "oak_d_lite_config.yaml")
    with open(cfg, "w") as f:
        f.write("%YAML:1.0\n\n")
        f.write("imu: 1\n")
        f.write("num_of_cam: 2\n\n")
        f.write('imu_topic: "/oak/imu/data"\n')
        f.write('image0_topic: "/oak/left/image_rect"\n')
        f.write('image1_topic: "/oak/right/image_rect"\n')
        f.write('output_path: "~/.ros/output/"\n\n')
        f.write('cam0_calib: "cam0_pinhole.yaml"\n')
        f.write('cam1_calib: "cam1_pinhole.yaml"\n')
        f.write(f"image_width: {W}\n")
        f.write(f"image_height: {H}\n\n")
        f.write("use_gpu         : 0\n")
        f.write("use_gpu_acc_flow: 0\n")
        f.write("use_gpu_ceres   : 0\n\n")
        f.write("estimate_extrinsic: 0\n")
        f.write("body_T_cam0: !!opencv-matrix\n")
        f.write("   rows: 4\n   cols: 4\n   dt: d\n")
        f.write(f"   data: [{', '.join(f'{v:.15f}' for v in mat4_to_list(body_T_cam0))}]\n\n")
        f.write("body_T_cam1: !!opencv-matrix\n")
        f.write("   rows: 4\n   cols: 4\n   dt: d\n")
        f.write(f"   data: [{', '.join(f'{v:.15f}' for v in mat4_to_list(body_T_cam1))}]\n\n")
        f.write("multiple_thread: 1\n\n")
        f.write("max_cnt: 150\n")
        f.write("min_dist: 30\n")
        f.write("freq: 10\n")
        f.write("F_threshold: 1.0\n")
        f.write("show_track: 1\n")
        f.write("flow_back: 1\n\n")
        f.write("max_solver_time: 0.04\n")
        f.write("max_num_iterations: 8\n")
        f.write("keyframe_parallax: 10.0\n\n")
        f.write("acc_n: 0.08\n")
        f.write("gyr_n: 0.004\n")
        f.write("acc_w: 0.001\n")
        f.write("gyr_w: 0.0001\n")
        f.write("g_norm: 9.805\n\n")
        f.write("estimate_td: 0\n")
        f.write("td: 0.0\n\n")
        f.write("load_previous_pose_graph: 0\n")
        f.write('pose_graph_save_path: "~/.ros/output/pose_graph/"\n')
        f.write("save_image: 0\n")

    print(f"  -> config/oak_d_lite/oak_d_lite_config.yaml")
    print(f"\n所有文件已生成: {OUTPUT_DIR}/")
