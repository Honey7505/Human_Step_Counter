import cv2
import face_recognition
import os
import numpy as np

# Folder Path
Faces_reco = "faces_pic"
Faces_reco_encoding = []
Faces_reco_names = []

# Load Known faces
for filename in os.listdir(Faces_reco):
    image_path = os.path.join(Faces_reco, filename)
    print("Loading", image_path)

    image = face_recognition.load_image_file(image_path)

    encoding = face_recognition.face_encodings(image)
    if len(encoding) == 0:
        print(f"No face detect in {filename}")
        continue

    Faces_reco_encoding.append(encoding[0])
    name = os.path.splitext(filename)[0]
    Faces_reco_names.append(name)

    print(f"{name} load successfully")

print("Known Faces Load Successfully!")

# Start webcam/video
cap = cv2.VideoCapture("avengers1.mp4")

cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    "Face Recognition",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Resize for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert BGR to RGB
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")

    # Face encodings
    face_encodings = face_recognition.face_encodings(
        rgb_small_frame,
        face_locations
    )

    for face_encoding, face_location in zip(face_encodings, face_locations):

        # Compare Faces
        matches = face_recognition.compare_faces(
            Faces_reco_encoding,
            face_encoding,
            tolerance=0.6
        )

        name = "Unknown"

        # Face Distance
        face_dist = face_recognition.face_distance(
            Faces_reco_encoding,
            face_encoding
        )

        if len(face_dist) > 0:
            best_match_index = np.argmin(face_dist)

            if matches[best_match_index]:
                name = Faces_reco_names[best_match_index]

        # Scale back face location
        top, right, bottom, left = face_location
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw rectangle
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

        # Draw name
        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Recognition", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
