from setuptools import setup
from glob import glob

package_name = 'oak_d_lite_driver'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/launch',
            glob('launch/*.launch.py')),
        ('share/' + package_name,
            ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Python ROS2 driver for OAK-D Lite camera',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'oak_d_lite_node = oak_d_lite_driver.oak_d_lite_node:main',
        ],
    },
)
