import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class FakeSensorNode(Node):
    def __init__(self):
        super().__init__('fake_sensor_node')
        self.get_logger().info("Fake Sensor Node Started")
        self.get_logger().info("Press:")
        self.get_logger().info("  m → Front reached")
        self.get_logger().info("  s → Sort done")

        self.front_pub = self.create_publisher(Bool, '/front_reached', 10)
        self.sort_pub = self.create_publisher(Bool, '/sort_done', 10)

        self.timer = self.create_timer(0.1, self.read_input)

    def read_input(self):
        try:
            key = input().strip().lower()
        except EOFError:
            return

        if key == 'm':
            msg = Bool()
            msg.data = True
            self.front_pub.publish(msg)
            self.get_logger().info("Fake FRONT_REACHED sent")

        elif key == 's':
            msg = Bool()
            msg.data = True
            self.sort_pub.publish(msg)
            self.get_logger().info("Fake SORT_DONE sent")


def main(args=None):
    rclpy.init(args=args)
    node = FakeSensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
