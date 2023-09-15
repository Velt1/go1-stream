import cv2
import numpy as np
import signal
import time


# Flag for smooth closing
stop_signal = False

def signal_handler(signal, frame):
    global stop_signal
    stop_signal = True

signal.signal(signal.SIGINT, signal_handler)

# MJPEG Stream URLs
streams = [
    "udp://0.0.0.0:5011",
    "udp://0.0.0.0:5012",
    "udp://0.0.0.0:5013",
    "udp://0.0.0.0:5014",
    # ...
]

# placement of streams in grid
# format: (starting_row, starting_column, row number, column number)
stream_grid_specs = [
    (0, 0, 2, 2),  # Stream 1 starts top left(0,0) and is 2 row wide and 2 columns long (2,2)
    (0, 2, 2, 2),  # Stream 2
    (2, 0, 2, 2),  # Stream 3
    (2, 2, 2, 2),  # Stream 4
    # ...
]

capture_pipelines = [
    (
        f"udpsrc uri={url} ! "
        "image/jpeg, width=400, height=480, framerate=15/1, format=MJPG !"
        "jpegparse ! "
        "nvv4l2decoder mjpeg=1 ! "
        "nvvidconv ! "
        "video/x-raw,format=BGRx ! "
        "videoconvert ! "
        "video/x-raw,format=BGR ! "
        "appsink drop=1"
    )
    for url in streams
]
# capture_pipelines = [
#     (
#         f"udpsrc uri={url} ! "
#         "jpegparse ! "
#         "jpegdec ! "
#         "videoconvert ! "
#         "video/x-raw,format=BGR ! "
#         "appsink"
#     )
#     for url in streams
# ]

caps = [cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER) for pipeline in capture_pipelines]

# single frame size
frame_height, frame_width = 400, 480

# size for output stream (4x4 grid)
output_frame = np.zeros((frame_height * 4, frame_width * 4, 3), dtype=np.uint8)

gstreamer_pipeline = (
    "appsrc ! "
    "videoconvert ! "
    "video/x-raw,format=NV12 ! "
    "omxh264enc bitrate=8000000 preset-level=0 ! "  # 8 Mbps
    "rtspclientsink location=rtsp://192.168.123.161:8554/stream"
)


# Initialize VideoWriter
out = cv2.VideoWriter(gstreamer_pipeline, cv2.CAP_GSTREAMER, 0, 15, (frame_width * 4, frame_height * 4), True)

from concurrent.futures import ThreadPoolExecutor

def process_stream(idx, cap, output_frame, stream_grid_specs):
    if idx >= len(stream_grid_specs):
        return
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            start_row, start_col, row_span, col_span = stream_grid_specs[idx]
            resized_frame = cv2.resize(frame, (frame_width * col_span, frame_height * row_span))
            output_frame[
                start_row * frame_height:(start_row + row_span) * frame_height,
                start_col * frame_width:(start_col + col_span) * frame_width,
            ] = resized_frame
            
while not stop_signal:
    with ThreadPoolExecutor() as executor:
        executor.map(process_stream, range(len(caps)), caps, [output_frame]*len(caps), [stream_grid_specs]*len(caps))
    
    out.write(output_frame)

# release ressources
for cap in caps:
    cap.release()
out.release()

