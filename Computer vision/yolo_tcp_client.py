import socket
import cv2

from utils import (
    load_model,
    open_camera,
    get_object_center,
    draw_allowed_boxes,
    get_waste_type
)
from config import (
    MODEL_PATH,
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    IMG_SIZE,
    DETECT_EVERY_N_FRAMES
)

# ================= TCP =================
HOST = "127.0.0.1"
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Connected to ROS TCP server")

# ================= YOLO =================
model = load_model(MODEL_PATH)
cap = open_camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)

frame_count = 0
last_results = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # ================= YOLO DETECTION =================
    if frame_count % DETECT_EVERY_N_FRAMES == 0:
        last_results = model(frame, imgsz=IMG_SIZE, verbose=False)

        center_x, box_width, conf, class_name = get_object_center(
            last_results, model
        )

        waste_type = get_waste_type(class_name)

        # Build TCP payload
        if waste_type is not None and center_x is not None:
            payload = f"{waste_type},{center_x},{box_width},{conf:.2f}\n"
        else:
            payload = "None,-1,-1,0.0\n"

        # Send to ROS
        try:
            client.send(payload.encode())
            print(f"Sent: {payload.strip()}")
        except BrokenPipeError:
            print("ROS disconnected. Stopping YOLO client.")
            break

    # ================= DRAW =================
    if last_results is not None:
        frame = draw_allowed_boxes(frame, last_results, model)

    cv2.imshow("YOLO (Local)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
client.close()
cv2.destroyAllWindows()
