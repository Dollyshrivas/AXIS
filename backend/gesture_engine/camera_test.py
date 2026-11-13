import cv2

# Open the laptop's default camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("AXIS: Camera could not be opened.")
    exit()

print("AXIS: Camera connected successfully!")
print("Press Q to close the camera.")

while True:
    success, frame = camera.read()

    if not success:
        print("AXIS: Could not read camera frame.")
        break

    # Mirror the camera feed
    frame = cv2.flip(frame, 1)

    # Display the camera feed
    cv2.imshow("AXIS - Gesture Camera", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
