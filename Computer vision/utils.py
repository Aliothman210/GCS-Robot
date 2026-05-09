# utils.py

# Import Libiraries

from ultralytics import YOLO
import cv2
import time
import serial
from config import RECYCLABLE_CLASSES, NON_RECYCLABLE_CLASSES



# ------------------ Helper Functions ------------------ #

def load_model(model_path: str):
    """Load YOLO model from file."""
    return YOLO(model_path)


def open_camera(index=0, width=640, height=480):
    """Initialize and configure camera."""

    cap = cv2.VideoCapture(index) # Capture the video
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def get_waste_type(class_name: str):
    if class_name in RECYCLABLE_CLASSES:
        return "Recyclable"
    elif class_name in NON_RECYCLABLE_CLASSES:
        return "Non-Recyclable"
    else:
        return None



def draw_allowed_boxes(frame, results, model):
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            waste_type = get_waste_type(class_name)
            if waste_type is None:
                continue

            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            label = f"{waste_type} ({class_name}) {confidence:.2f}"

            color = (0, 255, 0) if waste_type == "Recyclable" else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
    return frame


def decide_waste(results, model):
    recyclable_count = 0
    non_recyclable_count = 0

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            if class_name in RECYCLABLE_CLASSES:
                recyclable_count += 1
            elif class_name in NON_RECYCLABLE_CLASSES:
                non_recyclable_count += 1

    if recyclable_count > non_recyclable_count and recyclable_count > 0:
        return 'Y'
    elif non_recyclable_count > recyclable_count and non_recyclable_count > 0:
        return 'N'
    else:
        return "X"
    
# Function to get the center x-coordinate of the detected object
def get_object_center(results, model):
    if results is None:
        return None, None, None, None

    best_box = None
    best_conf = 0.0
    best_class = None

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            if class_name in RECYCLABLE_CLASSES or class_name in NON_RECYCLABLE_CLASSES:
                conf = float(box.conf[0])
                if conf > best_conf:
                    best_conf = conf
                    best_box = box
                    best_class = class_name

    if best_box is None:
        return None, None, None, None

    x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()

    center_x = int((x1 + x2) / 2)
    box_width = int(x2 - x1)

    return center_x, box_width, best_conf, best_class


def decide_movement(object_center_x, frame_width, threshold=40):
    frame_center = frame_width // 2
    error = object_center_x - frame_center

    if error > threshold:
        return "R"
    elif error < -threshold:
        return "L"
    else:
        return "F"


def calculate_fps(prev_time):
    """Calculate FPS based on time difference."""
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    return fps, current_time

