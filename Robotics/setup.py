from setuptools import find_packages, setup

package_name = 'gcs_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ali-othman',
    maintainer_email='ali-othman@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
            
        ],
    },
    entry_points={
        'console_scripts': [
            'vision_node = gcs_vision.vision_node:main',
            'motor_serial_node = gcs_vision.motor_serial_node:main',
            'fake_sensor_node = gcs_vision.fake_sensor_node:main'
        ],
    },
)
