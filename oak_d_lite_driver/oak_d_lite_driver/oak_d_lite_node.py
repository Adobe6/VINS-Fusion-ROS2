import rclpy
from rclpy.node import Node
import depthai as dai
from sensor_msgs.msg import Image, Imu
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from builtin_interfaces.msg import Time
import threading
import time

FPS = 30
IMU_FREQ = 100


class OAKDLiteNode(Node):
    def __init__(self):
        super().__init__('oak_d_lite_node')
        self.bridge = CvBridge()

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.pub_left  = self.create_publisher(Image, '/cam0/image_raw', qos)
        self.pub_right = self.create_publisher(Image, '/cam1/image_raw', qos)
        self.pub_imu   = self.create_publisher(Imu, '/imu', qos)

        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while self.running and rclpy.ok():
            try:
                self._run_pipeline()
            except Exception as e:
                self.get_logger().error(f'Error: {e}, retrying in 3s...')
                time.sleep(3.0)

    def _run_pipeline(self):
        pipeline = dai.Pipeline()

        # 左目
        left = pipeline.create(dai.node.MonoCamera)
        left.setBoardSocket(dai.CameraBoardSocket.CAM_B)
        left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
        left.setFps(FPS)

        # 右目
        right = pipeline.create(dai.node.MonoCamera)
        right.setBoardSocket(dai.CameraBoardSocket.CAM_C)
        right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
        right.setFps(FPS)

        # 立体校正
        stereo = pipeline.create(dai.node.StereoDepth)
        stereo.setRectification(True)
        stereo.setRectifyEdgeFillColor(0)
        stereo.initialConfig.setLeftRightCheck(False)
        stereo.initialConfig.setSubpixel(False)
        left.out.link(stereo.left)
        right.out.link(stereo.right)

        # 用 createOutputQueue 替代 XLinkOut
        q_left  = stereo.rectifiedLeft.createOutputQueue(30, False)
        q_right = stereo.rectifiedRight.createOutputQueue(30, False)

        # IMU
        imu = pipeline.create(dai.node.IMU)
        imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_FREQ)
        imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, IMU_FREQ)
        imu.setBatchReportThreshold(1)
        imu.setMaxBatchReports(5)
        q_imu = imu.out.createOutputQueue(100, False)

        self.get_logger().info('Connecting to OAK-D Lite...')
        pipeline.build()
        pipeline.start()
        self.get_logger().info('Connected!')

        while self.running and rclpy.ok():
            self._process_images(q_left, q_right)
            self._process_imu(q_imu)
            time.sleep(0.001)

        pipeline.stop()

    def _process_images(self, q_left, q_right):
        while True:
            left_in  = q_left.tryGet()
            right_in = q_right.tryGet()
            if left_in is None or right_in is None:
                break

            left_cv  = left_in.getCvFrame()
            right_cv = right_in.getCvFrame()
            ts = self._to_ros_time(left_in.getTimestamp())

            left_msg = self.bridge.cv2_to_imgmsg(left_cv, 'mono8')
            left_msg.header.stamp = ts
            left_msg.header.frame_id = 'oak_left_camera'
            self.pub_left.publish(left_msg)

            right_msg = self.bridge.cv2_to_imgmsg(right_cv, 'mono8')
            right_msg.header.stamp = ts
            right_msg.header.frame_id = 'oak_right_camera'
            self.pub_right.publish(right_msg)

    def _process_imu(self, q_imu):
        imu_data_list = q_imu.tryGetAll()
        for imu_data in imu_data_list:
            for packet in imu_data.packets:
                accel = packet.acceleroMeter
                gyro = packet.gyroscope
                if accel is None or gyro is None:
                    continue
                msg = Imu()
                ts = self._to_ros_time(accel.getTimestamp())
                msg.header.stamp = ts
                msg.header.frame_id = 'oak_imu_frame'
                msg.linear_acceleration.x = accel.x
                msg.linear_acceleration.y = accel.y
                msg.linear_acceleration.z = accel.z
                msg.angular_velocity.x = gyro.x
                msg.angular_velocity.y = gyro.y
                msg.angular_velocity.z = gyro.z
                self.pub_imu.publish(msg)

    @staticmethod
    def _to_ros_time(ts):
        sec = int(ts.total_seconds())
        nsec = int((ts.total_seconds() - sec) * 1e9)
        t = Time()
        t.sec = sec
        t.nanosec = nsec
        return t

    def destroy_node(self):
        self.running = False
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = OAKDLiteNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
