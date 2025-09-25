# Testing Guide

## Structure

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
- Python 3.9+
- ffmpeg in PATH (winget install ffmpeg)
- Project deps installed: pip install -r requirements.txt
- Optional: .env with API keys for metadata/fingerprinting

## Common Commands

- Quick GUI run
  - run_gui.bat

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
