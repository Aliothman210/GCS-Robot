import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import serial


class MotorSerialNode(Node):
    def __init__(self):
        super().__init__('motor_serial_node')
        self.get_logger().info("Motor Serial Node Started")

        # ================= SERIAL =================
        try:
            self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            self.serial_enabled = True
            self.get_logger().info("Serial connected to Arduino")
        except Exception as e:
            self.ser = None
            self.serial_enabled = False
            self.get_logger().warn(f"Serial NOT connected: {e}")

        # ================= SUBSCRIBERS =================
        self.move_sub = self.create_subscription(
            String,
            '/cmd_move',
            self.move_callback,
            10
        )

        self.sort_sub = self.create_subscription(
            String,
            '/cmd_sort',
            self.sort_callback,
            10
        )

        # ================= PUBLISHERS =================
        self.front_pub = self.create_publisher(
            Bool,
            '/front_reached',
            10
        )

        self.sort_done_pub = self.create_publisher(
            Bool,
            '/sort_done',
            10
        )

    # ================= CALLBACKS =================
    def move_callback(self, msg):
        command = msg.data
        self.get_logger().info(f"Move command received: {command}")

        # Send to Arduino
        if self.serial_enabled:
            try:
                self.ser.write(command.encode())
            except Exception as e:
                self.get_logger().error(f"Serial write failed: {e}")

        # TEMP: simulate front sensor reached
        #if command == "F":
           # self.publish_front_reached()

    def sort_callback(self, msg):
        decision = msg.data
        self.get_logger().info(f"Sort command received: {decision}")

        # Send to Arduino
        if self.serial_enabled:
            try:
                self.ser.write(decision.encode())
            except Exception as e:
                self.get_logger().error(f"Serial write failed: {e}")

        # TEMP: simulate sort done
        #self.publish_sort_done()

    # ================= PUBLISH HELPERS =================
    def publish_front_reached(self):
        msg = Bool()
        msg.data = True
        self.front_pub.publish(msg)
        self.get_logger().info("Front sensor reached (simulated)")

    def publish_sort_done(self):
        msg = Bool()
        msg.data = True
        self.sort_done_pub.publish(msg)
        self.get_logger().info("Sorting done (simulated)")


def main(args=None):
    rclpy.init(args=args)
    node = MotorSerialNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
