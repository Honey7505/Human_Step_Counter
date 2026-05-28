import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from collections import deque
from flask import Flask, render_template, request
import os
import time

# ---------------- Flask ----------------
app = Flask(__name__, static_folder="static")

# ---------------- Folders ----------------
upload_fol = "video_upload"
static_fol = "static"

os.makedirs(upload_fol, exist_ok=True)
os.makedirs(static_fol, exist_ok=True)

# ---------------- Load MoveNet ----------------
model = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
movenet = model.signatures['serving_default']

# ---------------- Pose Detection ----------------
def detect_pose(frame):

    img = cv2.resize(frame, (192, 192))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = np.expand_dims(img, axis=0)

    img = tf.cast(img, dtype=tf.int32)

    outputs = movenet(img)

    return outputs['output_0'].numpy()

# ---------------- Draw Keypoints ----------------
def draw_keypoints(frame, keypoints, threshold=0.3):

    h, w, _ = frame.shape

    shaped = np.squeeze(keypoints)

    for kp in shaped:

        y, x, conf = kp

        if conf > threshold:

            cx = int(x * w)
            cy = int(y * h)

            cv2.circle(
                frame,
                (cx, cy),
                5,
                (0, 255, 0),
                -1
            )

# ---------------- Draw Skeleton ----------------
EDGES = [
    (5,7),(7,9),
    (6,8),(8,10),
    (5,6),
    (5,11),(6,12),
    (11,12),
    (11,13),(13,15),
    (12,14),(14,16)
]

def draw_connections(frame, keypoints, edges, threshold=0.3):

    h, w, _ = frame.shape

    shaped = np.squeeze(keypoints)

    for p1, p2 in edges:

        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if c1 > threshold and c2 > threshold:

            pt1 = (int(x1 * w), int(y1 * h))
            pt2 = (int(x2 * w), int(y2 * h))

            cv2.line(
                frame,
                pt1,
                pt2,
                (255, 0, 0),
                2
            )

# ---------------- Process Video ----------------
def process_video(video_path):

    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if fps <= 0:
        fps = 30

    # ---------------- Output Names ----------------
    timestamp = int(time.time())

    avi_name = f"output_{timestamp}.avi"
    mp4_name = f"output_{timestamp}.mp4"

    avi_path = os.path.join(static_fol, avi_name)
    mp4_path = os.path.join(static_fol, mp4_name)

    # ---------------- AVI Writer ----------------
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    out = cv2.VideoWriter(
        avi_path,
        fourcc,
        fps,
        (width, height)
    )

    # ---------------- Step Variables ----------------
    step_count = 0

    frame_count = 0

    last_step_frame = 0

    prev_left = 0

    energy_window = deque(maxlen=8)

    MIN_FRAMES = 6

    ENERGY_THRESHOLD = 0.015

    # ---------------- Main Loop ----------------
    while True:

        ret, frame = cap.read()

        if not ret:
            break

        keypoints = detect_pose(frame)

        kp = keypoints[0][0]

        # ---------------- Draw ----------------
        draw_connections(frame, keypoints, EDGES)

        draw_keypoints(frame, keypoints)

        frame_count += 1

        # ---------------- Step Detection ----------------
        if kp[15][2] > 0.3:

            hip_y = (kp[11][0] + kp[12][0]) / 2

            left_y = kp[15][0] - hip_y

            diff = abs(left_y - prev_left)

            prev_left = left_y

            energy_window.append(diff)

            avg_energy = sum(energy_window) / len(energy_window)

            if avg_energy > ENERGY_THRESHOLD:

                if frame_count - last_step_frame > MIN_FRAMES:

                    step_count += 1

                    last_step_frame = frame_count

                    energy_window.clear()

        # ---------------- Counter ----------------
        text = f"Steps: {step_count}"

        (text_w, text_h), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            3
        )

        x = width - text_w - 20
        y = height - 30

        # Background Box
        cv2.rectangle(
            frame,
            (x - 15, y - text_h - 15),
            (x + text_w + 15, y + 15),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 255),
            3
        )

        # ---------------- Write Frame ----------------
        out.write(frame)

    # ---------------- Release ----------------
    cap.release()

    out.release()

    # ---------------- Convert AVI → MP4 ----------------
    convert_command = (
        f'ffmpeg -y -i "{avi_path}" '
        f'-vcodec libx264 '
        f'"{mp4_path}"'
    )

    os.system(convert_command)

    print("Saved MP4:", mp4_path)

    return step_count, mp4_path

# ---------------- Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():

    step_count = None

    video_path = None

    if request.method == "POST":

        if "video" not in request.files:

            return render_template(
                "index.html",
                step_count=None,
                video_path=None
            )

        video = request.files["video"]

        if video.filename == "":

            return render_template(
                "index.html",
                step_count=None,
                video_path=None
            )

        # ---------------- Save Upload ----------------
        save_path = os.path.join(
            upload_fol,
            video.filename
        )

        video.save(save_path)

        # ---------------- Process ----------------
        step_count, output_path = process_video(save_path)

        video_path = "/" + output_path

    return render_template(
        "index.html",
        step_count=step_count,
        video_path=video_path
    )

# ---------------- Main ----------------
if __name__ == "__main__":

    app.run(debug=True)
