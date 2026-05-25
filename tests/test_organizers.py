import contextlib
import io
import threading
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import image_organizer, video_organizer


class ImageOrganizerTests(unittest.TestCase):
    def test_is_image_file_uses_case_insensitive_extension_and_mime_fallback(self):
        self.assertTrue(image_organizer.is_image_file(Path("PHOTO.JPEG")))
        self.assertTrue(image_organizer.is_image_file(Path("vector.svgz")))
        self.assertFalse(image_organizer.is_image_file(Path("notes.txt")))

    def test_compare_exif_data_handles_none_complex_values_and_type_mismatches(self):
        self.assertTrue(image_organizer.compare_exif_data(None, None))
        self.assertFalse(image_organizer.compare_exif_data({1: "a"}, None))
        self.assertFalse(image_organizer.compare_exif_data({1: "1"}, {1: 1}))
        self.assertTrue(image_organizer.compare_exif_data({1: [1, 2], 2: {"x": "y"}}, {1: [1, 2], 2: {"x": "y"}}))

    def test_existing_target_with_same_exif_but_different_bytes_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "photo.jpg"
            target = root / "2021" / "05-May" / "photo.jpg"
            target.parent.mkdir(parents=True)
            source.write_bytes(b"source bytes")
            target.write_bytes(b"target bytes")

            with (
                patch.object(image_organizer, "get_file_date", return_value=datetime(2021, 5, 2, 3, 4, 5)),
                patch.object(image_organizer, "get_exif_date", return_value=datetime(2021, 5, 2, 3, 4, 5)),
                patch.object(image_organizer, "get_exif_data", return_value={36867: "2021:05:02 03:04:05"}),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                image_organizer.scan_and_organize_images(root)

            self.assertTrue(source.exists())
            self.assertEqual(source.read_bytes(), b"source bytes")
            self.assertEqual(target.read_bytes(), b"target bytes")

    def test_existing_target_with_same_exif_and_same_bytes_deletes_duplicate_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "photo.jpg"
            target = root / "2021" / "05-May" / "photo.jpg"
            target.parent.mkdir(parents=True)
            source.write_bytes(b"same bytes")
            target.write_bytes(b"same bytes")

            with (
                patch.object(image_organizer, "get_file_date", return_value=datetime(2021, 5, 2, 3, 4, 5)),
                patch.object(image_organizer, "get_exif_date", return_value=datetime(2021, 5, 2, 3, 4, 5)),
                patch.object(image_organizer, "get_exif_data", return_value={36867: "2021:05:02 03:04:05"}),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                image_organizer.scan_and_organize_images(root)

            self.assertFalse(source.exists())
            self.assertEqual(target.read_bytes(), b"same bytes")

    def test_image_analysis_cancellation_stops_scan(self):
        logs = []
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "photo.jpg").write_bytes(b"image")
            organizer = image_organizer.ImageOrganizer(
                root,
                mode="check",
                log_callback=lambda message, level="INFO": logs.append((level, message)),
                cancel_event=cancel_event,
            )

            organizer.organize_images()

        self.assertTrue(any("cancelled" in message.lower() for _, message in logs))


class VideoOrganizerTests(unittest.TestCase):
    def test_parse_video_date_handles_bytes_and_date_only(self):
        self.assertEqual(video_organizer.parse_video_date(b"2023-04-05"), datetime(2023, 4, 5))
        self.assertEqual(video_organizer.parse_video_date("2023:04:05 06:07:08"), datetime(2023, 4, 5, 6, 7, 8))
        self.assertIsNone(video_organizer.parse_video_date("not a date"))

    def test_video_metadata_parses_utc_z_without_fractional_seconds(self):
        probe = {"format": {"tags": {"creation_time": "2023-04-05T06:07:08Z"}}}
        fake_ffmpeg = SimpleNamespace(probe=lambda _path: probe)
        with patch.object(video_organizer, "FFMPEG_AVAILABLE", True), patch.object(video_organizer, "ffmpeg", fake_ffmpeg, create=True):
            metadata = video_organizer.get_video_metadata(Path("clip.mp4"))

        self.assertEqual(metadata["creation_date"], datetime(2023, 4, 5, 6, 7, 8))

    def test_video_metadata_parses_timezone_offset_and_numeric_fields(self):
        probe = {
            "format": {
                "tags": {"creation_time": "2023-04-05T06:07:08+00:00"},
                "duration": "12.5",
                "size": "2048",
            }
        }
        fake_ffmpeg = SimpleNamespace(probe=lambda _path: probe)
        with patch.object(video_organizer, "FFMPEG_AVAILABLE", True), patch.object(video_organizer, "ffmpeg", fake_ffmpeg, create=True):
            metadata = video_organizer.get_video_metadata(Path("clip.mp4"))

        self.assertEqual(metadata["creation_date"], datetime(2023, 4, 5, 6, 7, 8))
        self.assertEqual(metadata["duration"], 12.5)
        self.assertEqual(metadata["size"], 2048)

    def test_move_video_file_dry_run_does_not_create_target_or_move_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "clip.mp4"
            target = root / "2023" / "04-April" / "clip.mp4"
            source.write_bytes(b"video")

            with contextlib.redirect_stdout(io.StringIO()):
                result = video_organizer.move_video_file({"source": source, "target": target}, dry_run=True)

            self.assertTrue(result)
            self.assertTrue(source.exists())
            self.assertFalse(target.exists())

    def test_move_video_file_cancelled_does_not_move_source(self):
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "clip.mp4"
            target = root / "2023" / "04-April" / "clip.mp4"
            source.write_bytes(b"video")

            with contextlib.redirect_stdout(io.StringIO()):
                result = video_organizer.move_video_file(
                    {"source": source, "target": target},
                    dry_run=False,
                    cancel_event=cancel_event,
                )

            self.assertFalse(result)
            self.assertTrue(source.exists())
            self.assertFalse(target.exists())

    def test_video_organizer_rejects_invalid_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            organizer = video_organizer.VideoOrganizer(tmp, mode="bad", log_callback=lambda *_: None)
            with self.assertRaises(ValueError):
                organizer.organize_videos()

    def test_video_scan_cancellation_logs_and_stops(self):
        logs = []
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "clip.mp4").write_bytes(b"video")
            organizer = video_organizer.VideoOrganizer(
                root,
                mode="check",
                log_callback=lambda message, level="INFO": logs.append((level, message)),
                cancel_event=cancel_event,
            )

            organizer.organize_videos()

        self.assertTrue(any("cancelled" in message.lower() for _, message in logs))

    def test_get_expected_path_returns_none_without_metadata_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root / "clip.mp4"
            video.write_bytes(b"video")

            with patch.object(video_organizer, "get_file_date", return_value=None):
                self.assertIsNone(video_organizer.get_expected_path(video, root))

    def test_is_already_organized_requires_exact_expected_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            organized = root / "2023" / "04-April" / "clip.mp4"
            misplaced = root / "clip.mp4"
            organized.parent.mkdir(parents=True)
            organized.write_bytes(b"video")
            misplaced.write_bytes(b"video")

            with patch.object(video_organizer, "get_file_date", return_value=datetime(2023, 4, 5)):
                self.assertTrue(video_organizer.is_already_organized(organized, root))
                self.assertFalse(video_organizer.is_already_organized(misplaced, root))


if __name__ == "__main__":
    unittest.main()
