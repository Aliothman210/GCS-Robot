# config.py

MODEL_PATH = "yolov8n.pt"
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
IMG_SIZE = 480
DETECT_EVERY_N_FRAMES = 5
STATE_SEARCH = "SEARCH"
STATE_MOVE   = "MOVE"
STATE_SORT   = "SORT"



RECYCLABLE_CLASSES = [
    "bottle", "cup", "fork", "knife",
    "spoon", "bowl", "book"
]

NON_RECYCLABLE_CLASSES = [
    "banana", "apple", "sandwich",
    "broccoli", "carrot", "orange",
    "hot dog", "pizza", "donut", "cake"
]
