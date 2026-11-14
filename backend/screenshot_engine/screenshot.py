import pyautogui
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_FOLDER = BASE_DIR / "screenshots"

SCREENSHOT_FOLDER.mkdir(parents=True, exist_ok=True)


def capture_screenshot():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOT_FOLDER / f"axis_screenshot_{timestamp}.png"

    # Capture the actual computer display only
    image = pyautogui.screenshot()
    image.save(filepath)

    print(f"AXIS: Screen screenshot saved: {filepath}")

    return str(filepath)
