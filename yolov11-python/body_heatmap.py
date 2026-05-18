'''import cv2
import numpy as np

# Create Blank Canvas
canvas = np.zeros(
    (800, 500, 3),
    dtype=np.uint8
)

# Body Joints Position
body_points = {
    "head": (250,120),
    "shoulder": (250,220),
    "right_elbow": (330, 320),
    "right_wrist": (390, 430),
    "left_elbow": (170, 320),
    "left_wrist": (110, 430),
    "hip": (250, 420),
    "right_knee": (310, 580),
    "left_knee": (190, 580),
    "right_ankle": (340, 730),
    "left_ankle": (160, 730)
}

# Skeleton Connection
connections = [
("head", "shoulder"),
("shoulder", "right_elbow"),
("right_elbow","right_wrist"),
("shoulder","left_elbow"),
("left_elbow","left_wrist"),
("shoulder","hip"),
("hip","right_knee"),
("right_knee","right_ankle"),
("hip","left_knee"),
("left_knee","left_ankle")
]

# Draw Skeleton
for start, end in connections:
    cv2.line(
        canvas,
        body_points[start],
        body_points[end],
        (80,80,80),
        6
    )

# Joint Activity
activity = {
    "right_elbow": 90,
    "right_wrist": 100,
    "shoulder": 75,
    "right_knee": 50
}

# Draw Heatmap
for joint, intensity in activity.items():
    x, y = body_points[joint]

    # Glow Circle
    cv2.circle(
        canvas,
        (x,y),
        intensity,
        (0, 0, 255),
        -1    
    )

# Blur Effect
canvas = cv2.GaussianBlur(
    canvas,
    (101,101),
    0
)

# Add Skeleton Again
for start, end in connections:
    cv2.line(
        canvas,
        body_points[start],
        body_points[end],
        (255, 255, 255),
        3
    )

# Show
cv2.imshow(
    "Player Body Heatmap",
    canvas
)

cv2.waitKey(0)
cv2.destroyAllWindows()'''

'''import cv2

# Load Image
img = cv2.imread("human_sil0.jpeg")

# Check
if img is None:
    print("Image not found")
else:
    print("Image loaded")
    cv2.imshow(
        "Template",
        img    
    )
    cv2.waitKey(0)
    cv2.destroyAllWindows()
'''
'''
# __define-ocg__ BODY OVERLAY HEATMAP

import cv2
import numpy as np

# -----------------------------------------
# LOAD BODY TEMPLATE
# -----------------------------------------

body = cv2.imread(
    "human_sil1.png",
    cv2.IMREAD_COLOR
)

# Resize
body = cv2.resize(
    body,
    (500, 900)
)

# -----------------------------------------
# CREATE HEAT LAYER
# -----------------------------------------

heat_layer = np.zeros_like(body)

# -----------------------------------------
# BODY PART POSITIONS
# -----------------------------------------

body_parts = {
    
    "head": (250, 120),

    "shoulder": (250, 240),

    "right_elbow": (340, 340),
    "right_wrist": (350, 500),


    "left_elbow": (180, 340),

    "left_wrist": (150, 500),

    "hip": (250, 500),

    "right_knee": (320, 680),
    "right_ankle": (310, 840),    

    "left_knee": (180, 680),
    "left_ankle": (190, 840)
}

# -----------------------------------------
# ACTIVITY VALUES
# -----------------------------------------

activity = {

    "shoulder": 120,

    "right_elbow": 180,

    "right_wrist": 255,

    "right_knee": 100
}

# -----------------------------------------
# DRAW HEAT ZONES
# -----------------------------------------

for joint, intensity in activity.items():

    x, y = body_parts[joint]

    # Draw heat glow
    cv2.circle(
        heat_layer,
        (x, y),
        45,
        (intensity, intensity, intensity),
        -1
    )

# -----------------------------------------
# APPLY BLUR
# -----------------------------------------

heat_layer = cv2.GaussianBlur(
    heat_layer,
    (71, 71),
    0
)

# -----------------------------------------
# COLOR MAP
# -----------------------------------------

gray = cv2.cvtColor(
    heat_layer,
    cv2.COLOR_BGR2GRAY
)

gray = cv2.normalize(
    gray,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)
gray = np.uint8(gray)

colored = cv2.applyColorMap(
    gray,
    cv2.COLORMAP_JET
)

# -----------------------------------------
# OVERLAY
# -----------------------------------------

final = cv2.addWeighted(
    body,
    0.7,
    colored,
    0.9,
    0
)

# -----------------------------------------
# SHOW
# -----------------------------------------

cv2.imshow(
    "BODY Style Heatmap",
    final
)

cv2.waitKey(0)

cv2.destroyAllWindows()

# -----------------------------------------
# SAVE
# -----------------------------------------

cv2.imwrite(
    "pubg_style_heatmap.png",
    final
)

print("Heatmap Saved!")'''

'''import cv2
import pandas as pd
import numpy as np

# Load CSV
df = pd.read_csv("player_biomechanics_pix.csv")

# Load Body Template
body = cv2.imread(
    "human_sil_0.png",
    cv2.IMREAD_COLOR
)

body = cv2.resize(
    body,
    (500, 900)
)

# Body Parts POsition
body_parts = {
    "right_shoulder": (250, 240),
    "right_elbow": (320, 430),
    "right_wrist": (350, 500),
    "right_knee": (300, 680)
}

# Create heat layer
heat_layer = np.zeros_like(body)

# Calculate Movement
activity = {}
joints = [
    "right_shoulder",
    "right_elbow",
    "right_wrist",
    "right_knee"
]

# Movement Analysis
for joint in joints:
    x_col = f"{joint}_x"
    y_col = f"{joint}_y"

    Tot_movement = 0
    prev_x = None
    prev_y = None
    
    # Loop rows
    for index, row in df.iterrows():
        x = float(row[x_col])
        y = float(row[y_col])

        # Skip missing
        if x == 0 or y == 0:
            continue
        
        if prev_x is not None:
            dx = x - prev_x
            dy = y - prev_y

            movement = np.sqrt(dx**2 + dy**2)
            Tot_movement += movement
        prev_x = x
        prev_y = y
    activity[joint] = Tot_movement

# Normalize Intensity
max_move = max(
    activity.values()
)

for joint in activity:
    activity[joint] = int(
        (activity[joint]/ max_move)
        * 255
    )

# Draw Heat Zones
for joint, intensity in activity.items():
    x,y = body_parts[joint]
    cv2.circle(
        heat_layer,
        (x,y),
        45,
        (
            intensity,
            intensity,
            intensity    
        ),
        -1
    )

# Blur
heat_layer = cv2.GaussianBlur(
    heat_layer,
    (41, 41),
    0
)

# Convert To Color
gray = cv2.cvtColor(
    heat_layer,
    cv2.COLOR_BGR2GRAY
)

gray = cv2.normalize(
    gray,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)

gray = np.uint8(gray)

colored = cv2.applyColorMap(
    gray,
    cv2.COLORMAP_JET
)

# OverLay
final = cv2.addWeighted(
    body,
    0.7,
    colored,
    0.9,
    0
)

# Show
cv2.imshow(
    "Dynamic Body Heatmap",
    final
)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save
cv2.imwrite(
    "dynamic_heatmap.png",
    final
)

print("Dynamic Heatmap Saved")'''




'''# __define-ocg__ BOWLER VS BATTER HEATMAP

import cv2
import numpy as np
import pandas as pd

# -----------------------------------------
# LOAD CSV
# -----------------------------------------

df = pd.read_csv(
    "player_biomechanics_pix.csv"
)

# -----------------------------------------
# LOAD BODY TEMPLATE
# -----------------------------------------

body_template = cv2.imread(
    "human_sil_0.png",
    cv2.IMREAD_COLOR
)

body_template = cv2.resize(
    body_template,
    (500, 900)
)

# -----------------------------------------
# BODY PART POSITIONS
# -----------------------------------------

body_parts = {

    "right_shoulder": (250, 240),

    "right_elbow": (320, 340),

    "right_wrist": (350, 500),

    "right_knee": (300, 680)
}

# -----------------------------------------
# JOINTS
# -----------------------------------------

joints = [

    "right_shoulder",

    "right_elbow",

    "right_wrist",

    "right_knee"
]

# -----------------------------------------
# SPLIT PLAYERS
# -----------------------------------------

bowler_df = df[
    df["player_type"] == "Bowler"
]

batter_df = df[
    df["player_type"] == "Batter"
]

# -----------------------------------------
# FUNCTION
# -----------------------------------------

def calculate_activity(player_df):

    activity = {}

    for joint in joints:

        x_col = f"{joint}_x"
        y_col = f"{joint}_y"

        total_movement = 0

        prev_x = None
        prev_y = None

        for index, row in player_df.iterrows():

            x = float(row[x_col])
            y = float(row[y_col])

            if x == 0 or y == 0:
                continue

            if prev_x is not None:

                dx = x - prev_x
                dy = y - prev_y

                movement = np.sqrt(
                    dx**2 + dy**2
                )

                total_movement += movement

            prev_x = x
            prev_y = y

        activity[joint] = total_movement

    # Normalize
    max_move = max(
        activity.values()
    )

    for joint in activity:

        activity[joint] = int(

            (activity[joint] / max_move)

            * 255
        )

    return activity

# -----------------------------------------
# CALCULATE
# -----------------------------------------

bowler_activity = calculate_activity(
    bowler_df
)

batter_activity = calculate_activity(
    batter_df
)

# -----------------------------------------
# DRAW FUNCTION
# -----------------------------------------

def draw_heatmap(activity):

    body = body_template.copy()

    heat_layer = np.zeros_like(body)

    for joint, intensity in activity.items():

        x, y = body_parts[joint]

        cv2.circle(
            heat_layer,
            (x, y),
            25,
            (
                intensity,
                intensity,
                intensity
            ),
            -1
        )

    # Blur
    heat_layer = cv2.GaussianBlur(
        heat_layer,
        (41, 41),
        0
    )

    # Convert
    gray = cv2.cvtColor(
        heat_layer,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.normalize(
        gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    gray = np.uint8(gray)

    colored = cv2.applyColorMap(
        gray,
        cv2.COLORMAP_JET
    )

    final = cv2.addWeighted(
        body,
        0.7,
        colored,
        0.9,
        0
    )

    return final

# -----------------------------------------
# GENERATE HEATMAPS
# -----------------------------------------

bowler_map = draw_heatmap(
    bowler_activity
)

batter_map = draw_heatmap(
    batter_activity
)

# -----------------------------------------
# ADD LABELS
# -----------------------------------------

cv2.putText(
    bowler_map,
    "BOWLER",
    (150, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.2,
    (255, 255, 255),
    3
)

cv2.putText(
    batter_map,
    "BATTER",
    (150, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.2,
    (255, 255, 255),
    3
)

# -----------------------------------------
# COMBINE
# -----------------------------------------

combined = np.hstack(
    (bowler_map, batter_map)
)

# -----------------------------------------
# SHOW
# -----------------------------------------

cv2.imshow(
    "Bowler vs Batter Heatmap",
    combined
)

cv2.waitKey(0)

cv2.destroyAllWindows()

# -----------------------------------------
# SAVE
# -----------------------------------------

cv2.imwrite(
    "bowler_vs-batter_hetamap.png",
    combined
)

print("Comparison Heatmap Saved!")'''





'''# __define-ocg__ PHASE HEATMAP ANALYSIS

import cv2
import numpy as np
import pandas as pd

# -----------------------------------------
# LOAD CSV
# -----------------------------------------

df = pd.read_csv(
    "player_biomechanics_pix.csv"
)

# -----------------------------------------
# LOAD BODY TEMPLATE
# -----------------------------------------

body_template = cv2.imread(
    "human_sil_0.png",
    cv2.IMREAD_COLOR
)

body_template = cv2.resize(
    body_template,
    (500, 900)
)

# -----------------------------------------
# BODY PART POSITIONS
# -----------------------------------------

body_parts = {

    "right_shoulder": (250, 240),

    "right_elbow": (320, 340),

    "right_wrist": (350, 500),

    "right_knee": (300, 680)
}

# -----------------------------------------
# JOINTS
# -----------------------------------------

joints = [

    "right_shoulder",

    "right_elbow",

    "right_wrist",

    "right_knee"
]

# -----------------------------------------
# PHASES
# -----------------------------------------

runup_df = df[
    (df["frame_number"] >= 0)
    &
    (df["frame_number"] <= 40)
]

release_df = df[
    (df["frame_number"] >= 41)
    &
    (df["frame_number"] <= 60)
]

follow_df = df[
    (df["frame_number"] >= 61)
    &
    (df["frame_number"] <= 100)
]

# -----------------------------------------
# ACTIVITY FUNCTION
# -----------------------------------------

def calculate_activity(player_df):

    activity = {}

    for joint in joints:

        x_col = f"{joint}_x"
        y_col = f"{joint}_y"

        total_movement = 0

        prev_x = None
        prev_y = None

        for index, row in player_df.iterrows():

            x = float(row[x_col])
            y = float(row[y_col])

            if x == 0 or y == 0:
                continue

            if prev_x is not None:

                dx = x - prev_x
                dy = y - prev_y

                movement = np.sqrt(
                    dx**2 + dy**2
                )

                total_movement += movement

            prev_x = x
            prev_y = y

        activity[joint] = total_movement

    # Normalize
    max_move = max(
        activity.values()
    )

    for joint in activity:

        activity[joint] = int(

            (activity[joint] / max_move)

            * 255
        )

    return activity

# -----------------------------------------
# DRAW FUNCTION
# -----------------------------------------

def draw_heatmap(activity):

    body = body_template.copy()

    heat_layer = np.zeros_like(body)

    for joint, intensity in activity.items():

        x, y = body_parts[joint]

        cv2.circle(
            heat_layer,
            (x, y),
            25,
            (
                intensity,
                intensity,
                intensity
            ),
            -1
        )

    # Blur
    heat_layer = cv2.GaussianBlur(
        heat_layer,
        (41, 41),
        0
    )

    # Convert
    gray = cv2.cvtColor(
        heat_layer,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.normalize(
        gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    gray = np.uint8(gray)

    colored = cv2.applyColorMap(
        gray,
        cv2.COLORMAP_JET
    )

    final = cv2.addWeighted(
        body,
        0.7,
        colored,
        0.9,
        0
    )

    return final

# -----------------------------------------
# GENERATE
# -----------------------------------------

runup_map = draw_heatmap(
    calculate_activity(runup_df)
)

release_map = draw_heatmap(
    calculate_activity(release_df)
)

follow_map = draw_heatmap(
    calculate_activity(follow_df)
)

# -----------------------------------------
# LABELS
# -----------------------------------------

cv2.putText(
    runup_map,
    "RUN-UP",
    (120, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    3
)

cv2.putText(
    release_map,
    "RELEASE",
    (120, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    3
)

cv2.putText(
    follow_map,
    "FOLLOW THROUGH",
    (70, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    3
)

# -----------------------------------------
# COMBINE
# -----------------------------------------

combined = np.hstack(
    (
        runup_map,
        release_map,
        follow_map
    )
)

# -----------------------------------------
# SHOW
# -----------------------------------------

cv2.imshow(
    "Phase Heatmaps",
    combined
)

cv2.waitKey(0)

cv2.destroyAllWindows()

# -----------------------------------------
# SAVE
# -----------------------------------------

cv2.imwrite(
    "phase_heatmaps.png",
    combined
)

print("Phase Heatmaps Saved!")'''

'''from ultralytics import YOLO
model = YOLO("yolo11n.pt") 
# print(ultralytics.__version__)'''

from ultralytics import YOLO

model = YOLO("yolo11n.pt")
print(model)
