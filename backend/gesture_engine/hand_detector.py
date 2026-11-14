
import cv2
import mediapipe as mp
import sys
import time
from pathlib import Path

# ==================================================
# 1. AXIS BACKEND PATH
# ==================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ==================================================
# 2. IMPORT AXIS MODULES
# ==================================================

from screenshot_engine.screenshot import capture_screenshot
from gesture_classifier import classify_gesture


# ==================================================
# 3. MEDIAPIPE CONFIGURATION
# ==================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ==================================================
# 4. GESTURE SETTINGS
# ==================================================

HOLD_SECONDS = 0.8
ARM_TIMEOUT = 5

WINDOW_NAME = "AXIS - Gesture Detection"

armed = False
arm_time = 0

fist_started = None
fist_triggered = False


# ==================================================
# 5. SCREENSHOT FUNCTION
# ==================================================

def take_screen_screenshot():

    print("\nAXIS: Hiding webcam preview...")

    try:
        # Close only the AXIS preview window.
        cv2.destroyWindow(WINDOW_NAME)

        # Allow Windows to process the window close.
        cv2.waitKey(100)

        # Allow the desktop to refresh.
        time.sleep(1.0)

        print("AXIS: Capturing computer display...")

        # Capture the actual desktop, NOT the webcam frame.
        screenshot_path = capture_screenshot()

        print("AXIS: SCREENSHOT SUCCESS!")
        print(f"AXIS: Saved at: {screenshot_path}")

        return screenshot_path

    except Exception as error:
        print(f"AXIS: Screenshot failed: {error}")
        return None


# ==================================================
# 6. START WEBCAM
# ==================================================

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("AXIS: Camera could not be opened.")
    hands.close()
    sys.exit(1)

print("\n================================")
print("AXIS GESTURE SCREENSHOT SYSTEM")
print("================================")
print("1. Show OPEN PALM to activate.")
print("2. Close your palm into a FIST.")
print("3. Hold your fist for 0.8 seconds.")
print("4. AXIS captures your COMPUTER SCREEN.")
print("Press Q to exit.")
print("================================\n")


# ==================================================
# 7. MAIN GESTURE LOOP
# ==================================================

try:

    while True:

        success, frame = camera.read()

        if not success:
            print("AXIS: Camera frame unavailable.")
            break

        # Mirror webcam for gesture detection only.
        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(rgb_frame)

        open_palm_detected = False
        fist_detected = False

        detected_gestures = []

        # ------------------------------------------
        # Detect hand landmarks
        # ------------------------------------------

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                gesture = classify_gesture(hand_landmarks)

                detected_gestures.append(gesture)

                if gesture == "OPEN PALM":
                    open_palm_detected = True

                elif gesture == "FIST":
                    fist_detected = True

        current_time = time.monotonic()

        # ------------------------------------------
        # STEP 1: OPEN PALM ACTIVATION
        # ------------------------------------------

        if open_palm_detected and not armed:

            armed = True
            arm_time = current_time

            fist_started = None
            fist_triggered = False

            print("AXIS: Open palm detected!")
            print("AXIS: Ready. Close your palm.")

        # ------------------------------------------
        # STEP 2: ACTIVATION TIMEOUT
        # ------------------------------------------

        if armed and current_time - arm_time > ARM_TIMEOUT:

            armed = False
            fist_started = None
            fist_triggered = False

            print("AXIS: Activation expired.")
            print("AXIS: Show open palm again.")

        # ------------------------------------------
        # STEP 3: CLOSED FIST DETECTION
        # ------------------------------------------

        if armed and fist_detected and not fist_triggered:

            if fist_started is None:
                fist_started = current_time

            hold_duration = current_time - fist_started

            remaining = max(
                0,
                HOLD_SECONDS - hold_duration
            )

            cv2.putText(
                frame,
                f"Hold fist: {remaining:.1f}s",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            # --------------------------------------
            # STEP 4: CAPTURE SCREEN
            # --------------------------------------

            if hold_duration >= HOLD_SECONDS:

                print("\nAXIS: Fist confirmed!")

                screenshot_path = take_screen_screenshot()

                if screenshot_path:
                    print("AXIS: Your computer screen was captured.")

                # Require a new open palm for next capture.
                fist_triggered = True
                armed = False
                fist_started = None

        elif armed and not fist_detected:

            fist_started = None

        # ------------------------------------------
        # STEP 5: CAMERA WINDOW STATUS
        # ------------------------------------------

        if detected_gestures:
            status = " | ".join(detected_gestures)
        else:
            status = "No hand detected"

        cv2.putText(
            frame,
            status,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0) if detected_gestures else (0, 0, 255),
            2
        )

        if armed:
            status_message = "AXIS READY - CLOSE YOUR FIST"
        else:
            status_message = "SHOW OPEN PALM TO ACTIVATE"

        cv2.putText(
            frame,
            status_message,
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 0),
            2
        )

        # Display webcam only for hand detection.
        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    camera.release()
    hands.close()
    cv2.destroyAllWindows()

    print("\nAXIS: Gesture system stopped.")
