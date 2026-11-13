import math


def distance(point1, point2):
    """Calculate distance between two hand landmarks."""
    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


def classify_gesture(hand_landmarks):
    """
    Recognize basic hand gestures using 21 landmarks.
    """

    landmarks = hand_landmarks.landmark

    # Check whether four fingers are extended.
    index_open = landmarks[8].y < landmarks[6].y
    middle_open = landmarks[12].y < landmarks[10].y
    ring_open = landmarks[16].y < landmarks[14].y
    pinky_open = landmarks[20].y < landmarks[18].y

    fingers = [
        index_open,
        middle_open,
        ring_open,
        pinky_open
    ]

    # Check thumb position relative to palm size.
    palm_size = distance(landmarks[0], landmarks[9])

    thumb_open = (
        distance(landmarks[4], landmarks[5])
        > palm_size * 0.4
    )

    # Open Palm
    if all(fingers) and thumb_open:
        return "OPEN PALM"

    # Thumbs Up
    if (
        not any(fingers)
        and landmarks[4].y < landmarks[3].y
    ):
        return "THUMBS UP"

    # Pointing
    if index_open and not any(fingers[1:]):
        return "POINTING"

    # Fist
    if not any(fingers):
        return "FIST"

    return "UNKNOWN"
