
import cv2
import mediapipe as mp
import sys
import time
from pathlib import Path

# =====================================
# 1. IMPORT AXIS SCREENSHOT ENGINE
# =====================================

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from screenshot_engine.screenshot import capture_screenshot
from gesture_classifier import classify_gesture


# =====================================
# 2. INITIALIZE MEDIAPIPE
# =====================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# =====================================
# 3. SCREENSHOT GESTURE SETTINGS
# =====================================

HOLD_SECONDS = 2
COOLDOWN_SECONDS = 5

open_palm_started = None
last_capture_time = 0

# Prevent repeated screenshots while palm stays open
open_palm_triggered = False


# =====================================
# 4. OPEN LAPTOP CAMERA
# =====================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("AXIS: Camera could not be opened.")
    hands.close()
    sys.exit(1)

print("AXIS: Gesture system started.")
print("AXIS: Show an open palm to capture a screenshot.")
print("AXIS: Hold your palm for 0.8 seconds.")
print("AXIS: Press Q to exit.")


# =====================================
# 5. MAIN CAMERA LOOP
# =====================================

try:

    while True:

        success, frame = camera.read()

        if not success:
            print("AXIS: Could not read camera frame.")
            break

        # Mirror camera feed
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Detect hands
        results = hands.process(rgb_frame)

        open_palm_detected = False
        detected_gestures = []

        # =====================================
        # 6. RECOGNIZE HAND GESTURES
        # =====================================

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                # Draw hand landmarks
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                # Recognize gesture
                gesture = classify_gesture(hand_landmarks)

                detected_gestures.append(gesture)

                # Check open palm
                if gesture == "OPEN PALM":
                    open_palm_detected = True

        # =====================================
        # 7. DISPLAY GESTURE STATUS
        # =====================================

        if detected_gestures:

            status_text = " | ".join(detected_gestures)

            cv2.putText(
                frame,
                status_text,
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        else:

            cv2.putText(
                frame,
                "No hand detected",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        # =====================================
        # 8. OPEN PALM SCREENSHOT TRIGGER
        # =====================================

        current_time = time.monotonic()

        if open_palm_detected:

            if open_palm_started is None:
                open_palm_started = current_time

            hold_duration = (
                current_time - open_palm_started
            )

            remaining = max(
                0,
                HOLD_SECONDS - hold_duration
            )

            cv2.putText(
                frame,
                f"Hold palm: {remaining:.1f}s",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            # Capture only once per open-palm gesture
            if (
                hold_duration >= HOLD_SECONDS
                and not open_palm_triggered
                and current_time - last_capture_time >= COOLDOWN_SECONDS
            ):

                print("AXIS: Open palm detected!")

                try:
                    screenshot_path = capture_screenshot()

                    print(
                        f"AXIS: Screenshot saved at {screenshot_path}"
                    )

                    cv2.putText(
                        frame,
                        "SCREENSHOT CAPTURED!",
                        (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    last_capture_time = current_time

                except Exception as error:
                    print(
                        f"AXIS: Screenshot failed: {error}"
                    )

                open_palm_triggered = True

        else:

            # Reset when palm is no longer detected
            open_palm_started = None
            open_palm_triggered = False

        # =====================================
        # 9. DISPLAY CAMERA WINDOW
        # =====================================

        cv2.imshow(
            "AXIS - Gesture Screenshot System",
            frame
        )

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    # =====================================
    # 10. RELEASE RESOURCES
    # =====================================

    camera.release()
    hands.close()
    cv2.destroyAllWindows()

    print("AXIS: Gesture system stopped.")
