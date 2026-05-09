import rclpy
from rclpy.node import Node
import socket
import threading
from std_msgs.msg import String, Bool


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.get_logger().info("Vision node started (TCP server)")

        # ================= TCP SERVER =================
        thread = threading.Thread(target=self.tcp_server, daemon=True)
        thread.start()

        # ================= Publishers =================
        self.cmd_move_pub = self.create_publisher(String, '/cmd_move', 10)
        self.cmd_sort_pub = self.create_publisher(String, '/cmd_sort', 10)

        # ================= Subscribers =================
        self.front_sub = self.create_subscription(
            Bool,
            '/front_reached',
            self.front_reached_callback,
            10
        )

        self.sort_sub = self.create_subscription(
            Bool,
            '/sort_done',
            self.sort_done_callback,
            10
        )

        # ================= FSM =================
        self.state = "SEARCH"

        # ================= YOLO DATA =================
        self.center_x = None
        self.box_width = None
        self.confidence = 0.0
        self.waste_type = None

        # FSM tick (SEARCH only)
        self.timer = self.create_timer(0.1, self.fsm_step)

    # ================= TCP =================
    def tcp_server(self):
        HOST = "127.0.0.1"
        PORT = 5005

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(1)

        self.get_logger().info("TCP server waiting for YOLO...")
        conn, addr = server.accept()
        self.get_logger().info(f"YOLO connected from {addr}")

        while rclpy.ok():
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode().strip()
            waste, cx, bw, conf = msg.split(",")

            self.waste_type = waste if waste != "None" else None
            self.center_x = int(cx)
            self.box_width = int(bw)
            self.confidence = float(conf)

        conn.close()

    # ================= Callbacks =================
    def front_reached_callback(self, msg):
        if msg.data and self.state == "MOVE":
            self.get_logger().info("Front reached → SORT")
            self.state = "SORT"

            # send the descition 
            sort_msg = String()
            sort_msg.data = self.current_sort_decision
            self.cmd_sort_pub.publish(sort_msg)

    def sort_done_callback(self, msg):
        if msg.data and self.state == "SORT":
            self.get_logger().info("Sort done → SEARCH")

            # Reset state
            self.state = "SEARCH"
            self.waste_type = None
            self.center_x = None

    # ================= Logic =================
    def decide_movement(self, threshold=40):
        if self.center_x is None:
            return "S"

        frame_center = 640 // 2
        error = self.center_x - frame_center

        if error > threshold:
            return "R"
        elif error < -threshold:
            return "L"
        else:
            return "F"

    def fsm_step(self):
        # ================= SEARCH =================
        if self.state == "SEARCH":
            if self.waste_type is None:
                return

            movement = self.decide_movement()
            self.get_logger().info(f"SEARCH | movement: {movement}")

            move_msg = String()
            move_msg.data = movement
            self.cmd_move_pub.publish(move_msg)

            if movement == "F": 
                self.state = "MOVE"
                self.current_sort_decision = self.waste_type


def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
