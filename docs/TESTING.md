# Testing Guide

## Structure

- tests/*.py
  - Stdlib unittest regression tests for converter commands, organizers, dependency checks, WAV metadata, and optional ffmpeg smoke coverage
- tests/ps
  - PowerShell harnesses for end-to-end testing against sample files
  - Examples:
    - run_sample_tests.ps1: minimal, safe smoke test
    - run_full_matrix.ps1: configuration matrix across tools
    - analyze_logs.ps1: summarize matrix results
    - scan_missing_formats.ps1: find formats in Plex share
    - test_conversions.ps1: image/video/audio format conversions
    - test_all_conversions.ps1: comprehensive conversion matrix
- tests/python
  - Python scripts invoked by the PS harnesses
  - Examples:
    - test_conversions.py
    - test_all_conversions.py

## Prerequisites

- Windows PowerShell 7+
- Python 3.10+
- ffmpeg in PATH (winget install ffmpeg)
- Project deps installed: pip install -r requirements.txt
- Optional: .env with API keys for metadata/fingerprinting

## Common Commands

- Unit regression suite (no pytest required)
  - python -m unittest discover -s tests -v
  - Optional ffmpeg smoke tests are included in discovery and skip automatically when ffmpeg is unavailable

- Compile check
  - python -m compileall -q src tests

- Whitespace check
  - git diff --check

- Quick GUI run
  - scripts\run_gui.bat
  - python main.py

- Quick smoke test (safe, uses copies)
  - pwsh -NoProfile -File tests/ps/run_sample_tests.ps1

- Full matrix (logs in test_logs)
  - pwsh -NoProfile -File tests/ps/run_full_matrix.ps1
  - pwsh -NoProfile -File tests/ps/analyze_logs.ps1
  - Get-Content test_logs/summary.txt

- Conversion focus
  - pwsh -NoProfile -File tests/ps/test_conversions.ps1
  - pwsh -NoProfile -File tests/ps/test_all_conversions.ps1

## Notes

- Tests copy samples from \\VIVOBOOKMIKE\Plex where available, otherwise reuse converted outputs as inputs.
- All tests operate on local copies; originals in Plex are not modified.
- Video GPU is disabled in tests for reproducibility (CPU encode).

## Visual Checks

Use this after UI-facing changes:

- Launch the app from the project root.
- Confirm the app opens to the main working interface.
- Check the Media Organizer, Media Converter, and WAV to FLAC tabs.
- Confirm footer controls remain visible while scrolling.
- Expand and collapse advanced converter sections.
- Collapse and expand the activity log, then test the log filters.
- On Windows, confirm the taskbar icon matches assets/LogoIcon.ico.

## Dependency And Security Checks

Run these before dependency bumps or release prep:

- python -m pip install --upgrade pip
- python -m pip list --outdated
- python -m pip check
- python -m pip install pip-audit
- python -m pip_audit -r requirements.txt

External binaries are not covered by Python package audits. Keep FFmpeg and Chromaprint updated through the OS package manager.
