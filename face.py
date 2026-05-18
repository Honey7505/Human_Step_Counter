# Face Recognition And Detection System

from flask import Flask, render_template, Response, request, jsonify
import cv2
import face_recognition
import os
import numpy as np
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

# ==========================================
# LOAD KNOWN FACES
# ==========================================

KNOWN_FACES_DIR = "static/faces"

known_face_encodings = []
known_face_names = []
known_face_images = {}

for filename in os.listdir(KNOWN_FACES_DIR):

    if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
        continue

    path = os.path.join(KNOWN_FACES_DIR, filename)

    image = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) > 0:
        name = os.path.splitext(filename)[0]

        known_face_encodings.append(encodings[0])
        known_face_names.append(name)

        # 🔥 Correct path for browser
        known_face_images[name] = f"/static/faces/{filename}"

print("✅ Faces Loaded")

# ==========================================
# GLOBAL VARIABLES
# ==========================================

camera = None
recognized_people = set()
prev_boxes = []

# ==========================================
# FRAME GENERATOR
# ==========================================

def generate_frames():
    global camera, recognized_people, prev_boxes

    frame_count = 0

    while True:

        if camera is None:
            continue

        success, frame = camera.read()

        if not success or frame is None:
            break

        frame_count += 1

        # Resize
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = []
        face_encodings = []

        # Skip frames (performance)
        if frame_count % 2 == 0:
            face_locations = face_recognition.face_locations(rgb_small, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
            prev_boxes = face_locations
        else:
            face_locations = prev_boxes

        for i, face_location in enumerate(face_locations):

            name = "Unknown"

            if i < len(face_encodings):

                face_encoding = face_encodings[i]

                distances = face_recognition.face_distance(
                    known_face_encodings,
                    face_encoding
                )

                if len(distances) > 0:
                    best_match = np.argmin(distances)

                    # 🔥 Strict threshold
                    if distances[best_match] < 0.45:
                        name = known_face_names[best_match]
                        recognized_people.add(name)

            # Scale back
            top, right, bottom, left = face_location
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, name, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/start')
def start_camera():
    global camera, recognized_people
    recognized_people.clear()
    camera = cv2.VideoCapture(0)
    return "Camera Started"


@app.route('/stop')
def stop_camera():
    global camera
    if camera:
        camera.release()
        camera = None
    return "Stopped"


@app.route('/upload', methods=['POST'])
def upload_video():
    global camera, recognized_people

    recognized_people.clear()

    file = request.files['video']
    filename = secure_filename(file.filename)

    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", filename)

    file.save(path)

    camera = cv2.VideoCapture(path)

    return "Uploaded"


# ✅ FIXED ROUTE
@app.route('/faces')
def get_faces():
    return jsonify({
        "names": list(recognized_people),
        "images": known_face_images
    })

@app.route('/upload_image', methods=['POST'])
def upload_image():

    global known_face_encodings
    global known_face_names
    global known_face_images

    file = request.files['image']
    name = request.form['name']

    if not file or name == "":
        return "❌ Name or image missing"

    filename = secure_filename(name + ".jpg")
    save_path = os.path.join("static/faces", filename)

    file.save(save_path)

    image = face_recognition.load_image_file(save_path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        os.remove(save_path)
        return "❌ No face detected in image"

    known_face_encodings.append(encodings[0])
    known_face_names.append(name)
    known_face_images[name] = f"/static/faces/{filename}"

    return f"✅ {name} added successfully"


'''@app.route('/faces')
def get_faces():
    print("✅ Faces route working")
    return jsonify({
        "names": ["test"],
        "images": {
            "test": "/static/faces/test.jpg"
        }
    })'''

# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
