
import pyautogui
import os
from datetime import datetime

# Screenshot storage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_FOLDER = BASE_DIR / "screenshots"

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


def capture_screenshot():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"axis_screenshot_{timestamp}.png"

    filepath = os.path.join(
        SCREENSHOT_FOLDER,
        filename
    )

    screenshot = pyautogui.screenshot()

    screenshot.save(filepath)

    print(f"AXIS: Screenshot captured: {filepath}")

    return filepath


if __name__ == "__main__":
    capture_screenshot()
