
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("AXIS: Camera could not be opened.")
    hands.close()
    exit()

print("AXIS: MediaPipe hand detection started.")
print("Show your palm to the camera.")
print("Press Q to exit.")

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("AXIS: Camera frame unavailable.")
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

            cv2.putText(
                frame,
                "HAND DETECTED",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            print("AXIS: Hand detected", end="\r")

        else:
            cv2.putText(
                frame,
                "NO HAND DETECTED",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        cv2.imshow("AXIS - MediaPipe Hand Debug", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    hands.close()
    cv2.destroyAllWindows()
    print("\nAXIS: Hand detection stopped.")
