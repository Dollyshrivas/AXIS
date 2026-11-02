
import asyncio
from datetime import datetime
import os
import re
import psutil
import shutil
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus, urlsplit


BLOCKED_OPEN_SUFFIXES = {
    ".bat", ".cmd", ".com", ".exe", ".js", ".msi", ".ps1", ".py",
    ".scr", ".sh", ".vbs",
}

WEB_SUFFIXES = {
    "ai", "app", "au", "biz", "ca", "cloud", "co", "com", "de", "dev",
    "edu", "fr", "games", "gg", "gov", "in", "info", "int", "io", "jp",
    "me", "mil", "net", "online", "org", "site", "store", "tech", "tv",
    "uk", "us", "xyz",
}

WEB_APP_URLS = {
    "google": "https://www.google.com",
    "googlesearch": "https://www.google.com",
    "गूगल": "https://www.google.com",
    "गूगलसर्च": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "chatgpt": "https://chatgpt.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "github": "https://github.com",
    "netflix": "https://www.netflix.com",
}

# Common spoken names and abbreviations for installed apps.
APP_ALIASES = {
    "vscode": "visualstudiocode",
    "vs code": "visualstudiocode",
    "code": "visualstudiocode",
    "chrome": "googlechrome",
    "google chrome": "googlechrome",
    "edge": "microsoftedge",
    "explorer": "fileexplorer",
    "file explorer": "fileexplorer",
    "cmd": "commandprompt",
    "powershell": "windowspowershell",
    "python": "python314",
    "play games": "googleplaygamesbeta",
}

SKIPPED_SEARCH_DIRECTORIES = {
    "appdata",
    "application data",
    "$recycle.bin",
    "node_modules",
    "program files",
    "program files (x86)",
    "programdata",
    "system volume information",
    "temp",
    "venv",
    "windows",
    "windowsapps",
    ".cache",
    ".git",
    ".venv",
}


def _normalize_open_name(name):
    return "".join(
        character
        for character in str(name).casefold()
        if character.isalnum()
        or character == "_"
        or unicodedata.category(character).startswith("M")
    )


def _start_menu_roots():
    roots = []
    appdata = os.environ.get("APPDATA")
    programdata = os.environ.get("PROGRAMDATA")

    if appdata:
        roots.append(
            Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        )

    if programdata:
        roots.append(
            Path(programdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        )

    return [root for root in roots if root.is_dir()]


def _iter_open_candidates():
    """Find application shortcuts in Windows Start Menu."""
    seen = set()

    for root in _start_menu_roots():
        scanned = 0

        for current, directories, filenames in os.walk(root):
            depth = len(Path(current).relative_to(root).parts)

            if depth >= 6:
                directories.clear()
            else:
                directories[:] = [
                    name for name in directories
                    if not name.startswith(".")
                ]

            for filename in filenames:
                path = Path(current) / filename

                if path.suffix.casefold() not in {".lnk", ".url"}:
                    continue

                key = str(path).casefold()

                if key not in seen:
                    seen.add(key)
                    yield path

                scanned += 1

                if scanned >= 5000:
                    break

            if scanned >= 5000:
                break


def _is_web_address(target):
    if target.startswith(("http://", "https://")):
        parsed = urlsplit(target)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    if not re.fullmatch(
        r"(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?(?:/[^\s]*)?",
        target,
        re.IGNORECASE,
    ):
        return False

    suffix = target.rsplit(".", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    return suffix.casefold() in WEB_SUFFIXES


def _get_app_match_score(target_name, candidate_name):
    """Return a confidence score for matching an app shortcut."""
    if target_name == candidate_name:
        return 100

    if not target_name or not candidate_name:
        return 0

    # Match complete names contained within one another.
    if target_name in candidate_name or candidate_name in target_name:
        return 80

    # Compare meaningful words, ignoring common generic words.
    ignored = {"app", "application", "desktop", "program"}

    target_words = {
        word for word in re.findall(r"[a-z0-9]+", target_name)
        if word not in ignored
    }

    candidate_words = {
        word for word in re.findall(r"[a-z0-9]+", candidate_name)
        if word not in ignored
    }

    if not target_words or not candidate_words:
        return 0

    overlap = len(target_words & candidate_words)
    return int(70 * overlap / len(target_words))


def _find_installed_app(target, location=None):
    target_name = _normalize_open_name(target)

    # Resolve common aliases before searching.
    alias = APP_ALIASES.get(target.casefold())
    if alias:
        target_name = _normalize_open_name(alias)

    location_name = _normalize_open_name(location) if location else ""
    matches = []

    for path in _iter_open_candidates():
        if location_name:
            parent_name = _normalize_open_name(str(path.parent))
            if location_name not in parent_name:
                continue

        shortcut_name = _normalize_open_name(path.stem)
        score = _get_app_match_score(target_name, shortcut_name)

        if score >= 80:
            matches.append((score, path))

    if not matches:
        return None, []

    highest_score = max(score for score, _ in matches)
    best_matches = [
        path for score, path in matches
        if score == highest_score
    ]

    return best_matches[0] if len(best_matches) == 1 else None, best_matches


def open_item(target, location=None, file_only=False):
    target = str(target).strip().strip('"\'')
    if not target:
        return "Tell me the name of the app, file, folder, or website to open."

    if _is_web_address(target):
        url = (
            target
            if target.startswith(("http://", "https://"))
            else f"https://{target}"
        )
        return launch_chrome(url, target)

    # Search installed applications first.
    app_path, matches = _find_installed_app(target, location)

    if app_path is not None:
        try:
            os.startfile(str(app_path))
            return f"Opening {app_path.stem}."
        except OSError as error:
            print("Application launch error:", repr(error))
            return f"I found {app_path.stem}, but couldn't launch it."

    if len(matches) > 1:
        choices = ", ".join(
            f"{path.stem} in {path.parent.name}"
            for path in matches[:4]
        )
        return f"I found multiple matches: {choices}. Please specify the app."

    if file_only or Path(target).suffix:
        return f"I couldn't find {target} in your user folders."

    # Known web destinations.
    normalized = _normalize_open_name(target)
    website = WEB_APP_URLS.get(normalized)

    if website:
        return launch_chrome(website, target)

    # Google fallback only after no confident local match.
    search_url = (
        "https://www.google.com/search?q="
        + quote_plus(target + " official website")
    )
    return launch_chrome(search_url, f"Google search for {target}")


def open_file_explorer():
    try:
        subprocess.Popen(["explorer.exe"])
    except OSError as error:
        print("File Explorer launch error:", repr(error))
        return "I couldn't start File Explorer."

    return "Opening File Explorer."


def search_web(query, maps=False):
    query = str(query).strip()

    if not query:
        return "Tell me what you want me to search for."

    if maps:
        url = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(query)
        )
        return launch_chrome(url, f"Google Maps search for {query}")

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )
    return launch_chrome(url, f"Google search for {query}")


def say_hello():
    return "Hello! AXIS tool system is working."


def get_status():
    return {
        "status": "online",
        "system": "AXIS",
        "message": "All systems operational",
    }


def get_time():
    return datetime.now().strftime("%I:%M:%S %p")


def get_location():
    try:
        from winrt.windows.devices.geolocation import Geolocator

        async def read_position():
            return await Geolocator().get_geoposition_async()

        position = asyncio.run(read_position())
        coordinate = position.coordinate
        point = coordinate.point.position

        return (
            f"Your current location is latitude {point.latitude:.5f}, "
            f"longitude {point.longitude:.5f}, accurate to about "
            f"{coordinate.accuracy:.0f} meters."
        )

    except Exception as error:
        print("Location access error:", repr(error))
        return (
            "I couldn't access your device location. Turn on Location services "
            "and allow desktop apps to access your location in Windows Settings."
        )


def get_battery():
    battery = psutil.sensors_battery()

    if battery is None:
        return "Battery information is not available."

    percent = battery.percent

    if battery.power_plugged:
        return f"Battery is at {percent:.0f}% and the laptop is charging."

    return f"Battery is at {percent:.0f}%."


def launch_chrome(url=None, app_name=None):
    chrome_paths = [
        shutil.which("chrome"),
        os.path.join(
            os.environ.get("PROGRAMFILES", ""),
            "Google", "Chrome", "Application", "chrome.exe",
        ),
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", ""),
            "Google", "Chrome", "Application", "chrome.exe",
        ),
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Google", "Chrome", "Application", "chrome.exe",
        ),
    ]

    chrome_path = next(
        (path for path in chrome_paths if path and os.path.isfile(path)),
        None,
    )

    if chrome_path is None:
        return "Google Chrome was not found on this computer."

    command = [chrome_path]

    if url is not None:
        command.append(url)

    try:
        subprocess.Popen(command)
    except OSError as error:
        print("Chrome launch error:", repr(error))
        return "I couldn't launch Google Chrome."

    return (
        "Opening Google Chrome."
        if app_name is None
        else f"Opening {app_name} now."
    )


def open_chrome():
    return launch_chrome()


def open_youtube():
    return launch_chrome(
        "https://www.youtube.com",
        "YouTube",
    )


def open_whatsapp():
    return launch_chrome(
        "https://web.whatsapp.com",
        "WhatsApp",
    )
