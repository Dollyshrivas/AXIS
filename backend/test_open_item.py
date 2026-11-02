import unittest
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tool_router import (
    detect_tool,
    extract_open_request,
    extract_web_search_request,
    try_tool,
)
from tools import _iter_open_candidates, open_file_explorer, open_item, search_web


class OpenItemTests(unittest.TestCase):
    def test_routes_location_requests_in_english_hindi_and_hinglish(self):
        for request in ("where am I", "meri location", "मेरा स्थान"):
            with self.subTest(request=request):
                self.assertEqual(detect_tool(request), "get_location")

    def test_extracts_open_name_and_folder(self):
        self.assertEqual(
            extract_open_request("Please open budget.xlsx in Documents"),
            {"target": "budget.xlsx", "location": "documents"},
        )

    def test_extracts_spoken_my_file_request(self):
        self.assertEqual(
            extract_open_request("Open my file budget.xlsx"),
            {"target": "budget.xlsx", "file_only": True},
        )

    def test_file_not_found_does_not_search_the_web(self):
        with patch("tools._iter_open_candidates", return_value=[]), patch(
            "tools.launch_chrome"
        ) as chrome:
            result = open_item("old budget", file_only=True)

        self.assertIn("couldn't find", result)
        chrome.assert_not_called()

    def test_routes_bare_filename_to_local_file_search(self):
        with patch("tool_router.execute_tool", return_value="Opening notes.txt.") as execute:
            result = try_tool("notes.txt")

        self.assertEqual(result, "Opening notes.txt.")
        execute.assert_called_once_with("open_item", {"target": "notes.txt"})

    def test_routes_general_app_name_to_open_item(self):
        with patch("tool_router.execute_tool", return_value="Opening Spotify.lnk.") as execute:
            result = try_tool("launch Spotify")

        self.assertEqual(result, "Opening Spotify.lnk.")
        execute.assert_called_once_with("open_item", {"target": "spotify"})

    def test_routes_hindi_transliterated_open_google_command(self):
        with patch(
            "tool_router.execute_tool", return_value="Opening Google now."
        ) as execute:
            result = try_tool("ओपन गूगल")

        self.assertEqual(result, "Opening Google now.")
        execute.assert_called_once_with("open_item", {"target": "गूगल"})

    def test_routes_file_explorer_request(self):
        self.assertEqual(detect_tool("Open my file explorer"), "open_file_explorer")
        with patch(
            "tool_router.execute_tool", return_value="Opening File Explorer."
        ) as execute:
            result = try_tool("open file explorer")

        self.assertEqual(result, "Opening File Explorer.")
        execute.assert_called_once_with("open_file_explorer", None)

    def test_opens_file_explorer(self):
        with patch("tools.subprocess.Popen") as popen:
            result = open_file_explorer()

        self.assertEqual(result, "Opening File Explorer.")
        popen.assert_called_once_with(["explorer.exe"])

    def test_routes_nearby_place_requests_to_maps_without_open_keyword(self):
        self.assertEqual(
            extract_web_search_request("Give me some salons near me"),
            {"query": "salons near me", "maps": True},
        )
        with patch("tool_router.execute_tool", return_value="Opening Maps.") as execute:
            result = try_tool("Give me some salons near me")

        self.assertEqual(result, "Opening Maps.")
        execute.assert_called_once_with(
            "search_web", {"query": "salons near me", "maps": True}
        )

    def test_routes_website_requests_to_google_search_without_open_keyword(self):
        with patch("tool_router.execute_tool", return_value="Opening search.") as execute:
            result = try_tool("Give me some websites for learning Python")

        self.assertEqual(result, "Opening search.")
        execute.assert_called_once_with(
            "search_web",
            {"query": "websites for learning python", "maps": False},
        )

    def test_search_web_opens_maps_for_nearby_places(self):
        with patch(
            "tools.launch_chrome", return_value="Opening Google Maps."
        ) as chrome:
            result = search_web("salons near me", maps=True)

        self.assertEqual(result, "Opening Google Maps.")
        chrome.assert_called_once_with(
            "https://www.google.com/maps/search/?api=1&query=salons+near+me",
            "Google Maps search for salons near me",
        )

    def test_search_web_opens_google_results(self):
        with patch(
            "tools.launch_chrome", return_value="Opening Google search."
        ) as chrome:
            result = search_web("websites for learning Python")

        self.assertEqual(result, "Opening Google search.")
        chrome.assert_called_once_with(
            "https://www.google.com/search?q=websites+for+learning+Python",
            "Google search for websites for learning Python",
        )

    def test_opens_web_address_in_chrome(self):
        with patch("tools.launch_chrome", return_value="Opening example.com now.") as chrome:
            result = open_item("example.com")

        self.assertEqual(result, "Opening example.com now.")
        chrome.assert_called_once_with("https://example.com", "example.com")

    def test_opens_google_website_when_not_installed(self):
        with patch("tools._iter_open_candidates", return_value=[]), patch(
            "tools.launch_chrome", return_value="Opening Google now."
        ) as chrome:
            result = open_item("Google")

        self.assertEqual(result, "Opening Google now.")
        chrome.assert_called_once_with("https://www.google.com", "Google")

    def test_opens_google_website_for_devanagari_name(self):
        with patch("tools._iter_open_candidates", return_value=[]), patch(
            "tools.launch_chrome", return_value="Opening Google now."
        ) as chrome:
            result = open_item("गूगल")

        self.assertEqual(result, "Opening Google now.")
        chrome.assert_called_once_with("https://www.google.com", "गूगल")

    def test_searches_google_for_unknown_app(self):
        with patch("tools._iter_open_candidates", return_value=[]), patch(
            "tools.launch_chrome", return_value="Opening Google search now."
        ) as chrome:
            result = open_item("Some App")

        self.assertEqual(result, "Opening Google search now.")
        chrome.assert_called_once_with(
            "https://www.google.com/search?q=Some+App+official+website",
            "Google search for Some App",
        )

    def test_missing_file_does_not_search_web(self):
        with patch("tools._iter_open_candidates", return_value=[]), patch(
            "tools.launch_chrome"
        ) as chrome:
            result = open_item("missing-report.pdf")

        self.assertIn("couldn't find", result)
        chrome.assert_not_called()

    def test_asks_before_opening_ambiguous_name(self):
        matches = [Path("C:/Users/test/Documents/Notes.txt"), Path("C:/Users/test/Downloads/Notes.txt")]
        with patch("tools._iter_open_candidates", return_value=matches), patch("tools.os.startfile", create=True) as startfile:
            result = open_item("Notes.txt")

        self.assertIn("multiple matches", result)
        self.assertIn("Documents", result)
        self.assertIn("Downloads", result)
        startfile.assert_not_called()

    def test_location_selects_a_single_matching_item(self):
        matches = [Path("C:/Users/test/Documents/Notes.txt"), Path("C:/Users/test/Downloads/Notes.txt")]
        with patch("tools._iter_open_candidates", return_value=matches), patch("tools.os.startfile", create=True) as startfile:
            result = open_item("Notes.txt", location="Documents")

        self.assertEqual(result, "Opening Notes.txt.")
        startfile.assert_called_once_with(str(matches[0]))

    def test_finds_and_opens_file_in_deep_user_folder(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            nested_folder = home / "Pictures" / "Trips" / "2026"
            nested_folder.mkdir(parents=True)
            file_path = nested_folder / "holiday.jpg"
            file_path.touch()

            with patch("tools.Path.home", return_value=home), patch.dict(
                os.environ, {"OneDrive": ""}, clear=False
            ), patch("tools.os.startfile", create=True) as startfile:
                result = open_item("holiday.jpg")

        self.assertEqual(result, "Opening holiday.jpg.")
        startfile.assert_called_once_with(str(file_path))

    def test_skips_cache_and_virtual_environment_directories(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            cache = home / ".cache"
            environment = home / "project" / "venv"
            cache.mkdir()
            environment.mkdir(parents=True)
            (cache / "hidden.txt").touch()
            (environment / "package.txt").touch()

            with patch("tools.Path.home", return_value=home), patch.dict(
                os.environ, {"OneDrive": ""}, clear=False
            ):
                candidates = list(_iter_open_candidates())

        self.assertNotIn(cache / "hidden.txt", candidates)
        self.assertNotIn(environment / "package.txt", candidates)


if __name__ == "__main__":
    unittest.main()