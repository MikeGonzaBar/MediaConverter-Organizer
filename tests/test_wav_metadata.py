import importlib
import sys
import tempfile
import threading
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


def install_wav_converter_dependency_stubs():
    pydub = types.ModuleType("pydub")

    class FakeAudioSegment:
        @staticmethod
        def from_wav(_path):
            return FakeAudioSegment()

        def export(self, output_file, **_kwargs):
            Path(output_file).write_bytes(b"flac")

    pydub.AudioSegment = FakeAudioSegment
    pydub_utils = types.ModuleType("pydub.utils")
    pydub_utils.which = lambda _name: "ffmpeg"

    mutagen = types.ModuleType("mutagen")
    mutagen_flac = types.ModuleType("mutagen.flac")

    class FakeFLAC(dict):
        def __init__(self, *_args, **_kwargs):
            super().__init__()

        def delete(self):
            self.clear()

        def save(self):
            pass

    mutagen_flac.FLAC = FakeFLAC

    musicbrainzngs = types.ModuleType("musicbrainzngs")
    musicbrainzngs.set_useragent = lambda *_args, **_kwargs: None
    musicbrainzngs.search_releases = lambda *_args, **_kwargs: {}
    musicbrainzngs.get_release_by_id = lambda *_args, **_kwargs: {}
    musicbrainzngs.search_recordings = lambda *_args, **_kwargs: {}

    acoustid = types.ModuleType("acoustid")
    acoustid.fingerprint_file = lambda *_args, **_kwargs: (0, "")
    acoustid.lookup = lambda *_args, **_kwargs: {}

    pylast = types.ModuleType("pylast")

    class WSError(Exception):
        pass

    class LastFMNetwork:
        def __init__(self, *_args, **_kwargs):
            pass

    pylast.WSError = WSError
    pylast.LastFMNetwork = LastFMNetwork

    sys.modules.update(
        {
            "pydub": pydub,
            "pydub.utils": pydub_utils,
            "mutagen": mutagen,
            "mutagen.flac": mutagen_flac,
            "musicbrainzngs": musicbrainzngs,
            "acoustid": acoustid,
            "pylast": pylast,
        }
    )


install_wav_converter_dependency_stubs()
wav_to_flac_converter = importlib.import_module("src.wav_to_flac_converter")


class WavMetadataLookupTests(unittest.TestCase):
    def test_extract_track_number_handles_common_patterns(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)

        self.assertEqual(lookup._extract_track_number("01 - Opening"), 1)
        self.assertEqual(lookup._extract_track_number("Track 12"), 12)
        self.assertEqual(lookup._extract_track_number("07 track"), 7)
        self.assertIsNone(lookup._extract_track_number("Opening"))

    def test_generic_filename_detection_handles_multilingual_patterns(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)

        self.assertTrue(lookup._is_generic_filename("Pista 07"))
        self.assertTrue(lookup._is_generic_filename("Cancion 02"))
        self.assertFalse(lookup._is_generic_filename("A Real Song Title"))

    def test_parse_directory_structure_preserves_full_plain_year(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            audio = source / "Artist" / "1999 - Album Name" / "03 Track.wav"
            audio.parent.mkdir(parents=True)
            audio.write_bytes(b"wav")

            metadata = lookup.parse_directory_structure(audio, source)

        self.assertEqual(metadata["artist"], "Artist")
        self.assertEqual(metadata["album"], "Album Name")
        self.assertEqual(metadata["year"], "1999")
        self.assertEqual(metadata["track_number"], "03")
        self.assertTrue(metadata["is_generic"])

    def test_parse_directory_structure_handles_bracketed_year_and_various_artists(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            audio = source / "VA" / "[2001] Compilation" / "01 Song Title.wav"
            audio.parent.mkdir(parents=True)
            audio.write_bytes(b"wav")

            metadata = lookup.parse_directory_structure(audio, source)

        self.assertEqual(metadata["artist"], "Various Artists")
        self.assertEqual(metadata["album"], "Compilation")
        self.assertEqual(metadata["year"], "2001")
        self.assertEqual(metadata["track_number"], "01")

    def test_generic_existing_metadata_is_not_treated_as_complete(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)

        self.assertFalse(
            lookup._is_metadata_complete(
                {
                    "title": "Track 01",
                    "artist": "Artist",
                    "album": "Album",
                    "musicbrainz_recordingid": "recording-id",
                }
            )
        )

    def test_generic_metadata_skips_text_searches_when_audio_and_album_lookup_fail(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)
        lookup.lastfm_enabled = True

        with (
            patch.object(lookup, "search_track_by_position", return_value=None) as album_search,
            patch.object(lookup, "search_musicbrainz_individual", return_value={"title": "wrong"}) as track_search,
            patch.object(lookup, "lastfm_search", return_value={"title": "wrong"}) as lastfm_search,
        ):
            metadata = lookup.get_metadata(
                artist="Artist",
                album="Album",
                title="Track 01",
                track_number=1,
                is_generic=True,
                file_path=None,
            )

        album_search.assert_called_once_with("Artist", "Album", 1)
        track_search.assert_not_called()
        lastfm_search.assert_not_called()
        self.assertEqual(metadata["title"], "Track 01")
        self.assertEqual(metadata["track_number"], "01")

    def test_complete_existing_metadata_short_circuits_external_searches(self):
        lookup = wav_to_flac_converter.AdvancedMetadataLookup(enable_fingerprinting=False)
        existing = {
            "title": "Song Title",
            "artist": "Artist",
            "album": "Album",
            "musicbrainz_recordingid": "recording-id",
        }

        with (
            patch.object(lookup, "search_musicbrainz_individual", return_value={"title": "wrong"}) as track_search,
            patch.object(lookup, "audio_fingerprint_lookup", return_value={"title": "wrong"}) as fingerprint_search,
            patch.object(lookup, "lastfm_search", return_value={"title": "wrong"}) as lastfm_search,
        ):
            metadata = lookup.get_metadata(
                artist="Artist",
                album="Album",
                title="Song Title",
                is_generic=False,
                existing_metadata=existing,
            )

        self.assertIs(metadata, existing)
        track_search.assert_not_called()
        fingerprint_search.assert_not_called()
        lastfm_search.assert_not_called()

    def test_converter_find_audio_files_is_case_insensitive_and_ignores_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "a.WAV").write_bytes(b"wav")
            (source / "b.flac").write_bytes(b"flac")
            (source / "c.mp3").write_bytes(b"mp3")

            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(Path(tmp) / "out"),
                enable_metadata=False,
                enable_fingerprinting=False,
            )

            self.assertEqual({path.name for path in converter.find_audio_files()}, {"a.WAV", "b.flac"})

    def test_converter_convert_all_stops_before_work_when_cancelled(self):
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "a.wav").write_bytes(b"wav")
            (source / "b.wav").write_bytes(b"wav")
            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(Path(tmp) / "out"),
                enable_metadata=False,
                enable_fingerprinting=False,
            )

            converted, failed = converter.convert_all(cancel_event=cancel_event)

        self.assertEqual((converted, failed), (0, 0))
        self.assertEqual(converter.stats["cancelled"], 2)

    def test_existing_flac_is_copied_and_counted_as_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            output = Path(tmp) / "output"
            source.mkdir()
            flac = source / "song.flac"
            flac.write_bytes(b"flac")
            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(output),
                enable_metadata=False,
                enable_fingerprinting=False,
            )

            self.assertTrue(converter.process_single_file(flac))

            self.assertEqual(converter.stats["skipped_flac"], 1)
            self.assertEqual((output / "song.flac").read_bytes(), b"flac")

    def test_failed_wav_conversion_updates_failed_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            wav = source / "song.wav"
            wav.write_bytes(b"wav")
            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(Path(tmp) / "out"),
                enable_metadata=False,
                enable_fingerprinting=False,
            )

            with patch.object(converter, "convert_wav_to_flac", return_value=False):
                converted, failed = converter.convert_all()

        self.assertEqual((converted, failed), (0, 1))
        self.assertEqual(converter.stats["failed"], 1)

    def test_complete_metadata_skips_embedding(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            flac = source / "song.flac"
            flac.write_bytes(b"flac")
            existing = {
                "title": "Song",
                "artist": "Artist",
                "album": "Album",
                "musicbrainz_recordingid": "id",
            }
            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(Path(tmp) / "out"),
                enable_metadata=False,
                enable_fingerprinting=False,
            )
            converter.enable_metadata = True
            converter.metadata_lookup = Mock()
            converter.metadata_lookup.get_existing_metadata.return_value = existing
            converter.metadata_lookup.parse_directory_structure.return_value = {
                "title": "Song",
                "artist": "Artist",
                "album": "Album",
                "year": "",
                "track_number": "",
                "is_generic": False,
            }
            converter.metadata_lookup.get_metadata.return_value = existing

            with patch.object(converter, "embed_metadata") as embed_metadata:
                self.assertTrue(converter.process_single_file(flac))

            embed_metadata.assert_not_called()
            self.assertEqual(converter.stats["metadata_complete"], 1)

    def test_improved_metadata_is_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            flac = source / "song.flac"
            flac.write_bytes(b"flac")
            converter = wav_to_flac_converter.EnhancedWAVToFLACConverter(
                str(source),
                output_folder=str(Path(tmp) / "out"),
                enable_metadata=False,
                enable_fingerprinting=False,
            )
            converter.enable_metadata = True
            converter.metadata_lookup = Mock()
            converter.metadata_lookup.get_existing_metadata.return_value = {}
            converter.metadata_lookup.parse_directory_structure.return_value = {
                "title": "Song",
                "artist": "Artist",
                "album": "Album",
                "year": "2020",
                "track_number": "01",
                "is_generic": False,
            }
            converter.metadata_lookup.get_metadata.return_value = {
                "title": "Song",
                "artist": "Artist",
                "album": "Album",
                "musicbrainz_recordingid": "id",
            }

            with patch.object(converter, "embed_metadata", return_value=True) as embed_metadata:
                self.assertTrue(converter.process_single_file(flac))

            embed_metadata.assert_called_once()
            metadata = embed_metadata.call_args.args[1]
            self.assertEqual(metadata["year"], "2020")
            self.assertEqual(metadata["track_number"], "01")
            self.assertEqual(converter.stats["metadata_found"], 1)


if __name__ == "__main__":
    unittest.main()
