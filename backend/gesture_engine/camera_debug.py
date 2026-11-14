
import cv2

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("AXIS: Camera could not be opened.")
    exit()

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("AXIS: Camera debug started.")
print("Press Q to exit.")

while True:
    success, frame = camera.read()

    if not success:
        print("AXIS: Failed to read camera frame.")
        break

    frame = cv2.flip(frame, 1)

    height, width = frame.shape[:2]

    cv2.putText(
        frame,
        f"Camera working | {width}x{height}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("AXIS Camera Debug", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
