import cv2
import numpy as np
import dlib
from imutils import face_utils

# Initialize camera and face detection/landmark models
cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()

# Handle exception if the predictor file is not found
try:
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except RuntimeError as e:
    print("Error: Predictor file not found.")
    exit()

# Initialize counters and status variables
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

# Function to compute the Euclidean distance between two points
def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

# Function to determine if the eye is blinking
def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Check if the eye is closed, drowsy, or active based on ratio
    if ratio > 0.25:
        return 2
    elif 0.21 <= ratio <= 0.25:
        return 1
    else:
        return 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Exiting...")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        # Draw a rectangle around the face
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Get landmarks of the face
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # Check if the left or right eye is blinking
        left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        # Update status based on blink detection
        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "SLEEPING !!!"
                color = (255, 0, 0)
        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = "Drowsy !"
                color = (0, 0, 255)
        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)

        # Display the status on the frame
        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        # Draw landmarks
        for (x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)

    # Show the frame and face with landmarks
    cv2.imshow("Frame", frame)

    # Break on 'Esc' key press
    if cv2.waitKey(1) == 27:  # Esc key to break
        print("Exiting...")
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()
