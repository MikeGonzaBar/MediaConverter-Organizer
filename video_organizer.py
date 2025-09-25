#!/usr/bin/env python3
"""
Video Organizer Script

This script recursively scans a directory for videos and checks if they need to be organized
based on their metadata and current path structure. It can print files that are unorganized
and optionally move them to their proper organized locations.
"""

import os
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
import mimetypes
import subprocess
import json

# Try to import ffprobe for video metadata extraction
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    print("Warning: ffmpeg-python library not found. Install it with: pip install ffmpeg-python")
    print("Will fall back to file system dates for videos without metadata.")

# Common video file extensions
VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp',
    '.ogv', '.ts', '.mts', '.m2ts', '.vob', '.asf', '.rm', '.rmvb', '.divx',
    '.xvid', '.mpg', '.mpeg', '.m2v', '.m4v', '.f4v', '.f4p', '.f4a', '.f4b'
}

def is_video_file(file_path):
    """
    Check if a file is a video based on its extension and MIME type.
    
    Args:
        file_path (Path): Path to the file to check
        
    Returns:
        bool: True if the file is a video, False otherwise
    """
    # Check by extension first (faster)
    if file_path.suffix.lower() in VIDEO_EXTENSIONS:
        return True
    
    # Fallback to MIME type check
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type is not None and mime_type.startswith('video/')

def get_video_metadata(video_path):
    """
    Extract metadata from a video file using ffprobe.
    
    Args:
        video_path (Path): Path to the video file
        
    Returns:
        dict or None: Video metadata including creation date, or None if not found
    """
    if not FFMPEG_AVAILABLE:
        return None
    
    try:
        # Use ffprobe to get video metadata
        probe = ffmpeg.probe(str(video_path))
        
        if not probe or 'format' not in probe:
            return None
        
        format_info = probe['format']
        metadata = {}
        
        # Look for creation date in various metadata fields
        date_fields = [
            'creation_time', 'date', 'date_created', 'creation_date',
            'creation_time_utc', 'date_time', 'date_time_original'
        ]
        
        for field in date_fields:
            if field in format_info.get('tags', {}):
                date_str = format_info['tags'][field]
                try:
                    # Try different date formats
                    for fmt in [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S.%fZ",
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y:%m:%d %H:%M:%S",
                        "%Y-%m-%d",
                        "%Y/%m/%d %H:%M:%S"
                    ]:
                        try:
                            metadata['creation_date'] = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    if 'creation_date' in metadata:
                        break
                except Exception:
                    continue
        
        # Store other useful metadata
        if 'duration' in format_info:
            metadata['duration'] = float(format_info['duration'])
        
        if 'size' in format_info:
            metadata['size'] = int(format_info['size'])
        
        return metadata if metadata else None
        
    except Exception as e:
        # Silently fail and return None - will fall back to file system date
        return None

def get_file_date(file_path):
    """
    Get the date of a video file from metadata only.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        datetime or None: The file's date from metadata, or None if no metadata found
    """
    # Only use metadata creation date
    metadata = get_video_metadata(file_path)
    if metadata and 'creation_date' in metadata:
        return metadata['creation_date']
    
    # No metadata found - return None
    return None

def get_month_name(month_number):
    """
    Get the month name from month number.
    
    Args:
        month_number (int): Month number (1-12)
        
    Returns:
        str: Month name
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return month_names[month_number - 1]

def is_already_organized(file_path, source_dir):
    """
    Check if a video file is already in the correct organized structure.
    
    Args:
        file_path (Path): Path to the video file
        source_dir (Path): Source directory
        
    Returns:
        bool: True if the file is already organized, False otherwise
    """
    try:
        # Get the file's date from metadata
        file_date = get_file_date(file_path)
        if file_date is None:
            # No metadata - can't determine if organized
            return False
            
        year = file_date.year
        month = file_date.month
        
        # Create expected organized path
        month_name = get_month_name(month)
        expected_dir = source_dir / str(year) / f"{month:02d}-{month_name}"
        expected_path = expected_dir / file_path.name
        
        # Check if the file is already in the expected location
        return file_path == expected_path
        
    except Exception:
        # If we can't determine the date, assume it's not organized
        return False

def get_expected_path(file_path, source_dir):
    """
    Get the expected organized path for a video file.
    
    Args:
        file_path (Path): Path to the video file
        source_dir (Path): Source directory
        
    Returns:
        Path: Expected organized path
    """
    file_date = get_file_date(file_path)
    if file_date is None:
        # No metadata - can't determine expected path
        return None
        
    year = file_date.year
    month = file_date.month
    
    month_name = get_month_name(month)
    expected_dir = source_dir / str(year) / f"{month:02d}-{month_name}"
    return expected_dir / file_path.name

def move_video_file(file_info, dry_run=False):
    """
    Move a video file to its organized location.
    
    Args:
        file_info (dict): Dictionary containing file information
        dry_run (bool): If True, only print what would be done without actually moving
        
    Returns:
        bool: True if successful, False otherwise
    """
    source = file_info['source']
    target = file_info['target']
    
    if dry_run:
        print(f"  [DRY RUN] Would move: {source.name}")
        print(f"    From: {source}")
        print(f"    To:   {target}")
        return True
    
    try:
        # Create the target directory if it doesn't exist
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if target file already exists
        if target.exists():
            print(f"  [WARNING] Target file already exists: {target}")
            print(f"    Skipping: {source.name}")
            return False
        
        # Move the file
        shutil.move(str(source), str(target))
        print(f"  [MOVED] {source.name}")
        print(f"    From: {source}")
        print(f"    To:   {target}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed to move {source.name}: {e}")
        return False

def scan_and_organize_videos(source_dir, move_files=False, dry_run=False):
    """
    Scan the source directory recursively for videos and organize them.
    
    Args:
        source_dir (Path): Source directory to scan
        move_files (bool): If True, actually move the files to organized locations
        dry_run (bool): If True, only print what would be done without actually moving
    """
    if not source_dir.exists():
        print(f"Error: Directory '{source_dir}' does not exist.")
        return
    
    if not source_dir.is_dir():
        print(f"Error: '{source_dir}' is not a directory.")
        return
    
    print(f"Scanning directory: {source_dir}")
    if move_files:
        if dry_run:
            print("Mode: DRY RUN - Will show what would be moved without actually moving files")
        else:
            print("Mode: MOVE FILES - Will actually move files to organized locations")
    else:
        print("Mode: CHECK ONLY - Will only show what needs to be organized")
    print("=" * 60)
    
    video_count = 0
    unorganized_files = []
    metadata_count = 0
    no_metadata_count = 0
    
    # Recursively scan for videos
    print("Scanning for videos... (Press Ctrl+C to stop)")
    scanned_files = 0
    
    for file_path in source_dir.rglob('*'):
        scanned_files += 1
        
        # Show progress every 100 files
        if scanned_files % 100 == 0:
            print(f"  Scanned {scanned_files} files, found {video_count} videos...")
        
        if file_path.is_file() and is_video_file(file_path):
            video_count += 1
            
            # Check if video has metadata
            metadata = get_video_metadata(file_path)
            
            if metadata and 'creation_date' in metadata:
                metadata_count += 1
                date_source = "Metadata"
                
                # Check if the file is already organized
                if not is_already_organized(file_path, source_dir):
                    # Get the expected organized path
                    expected_path = get_expected_path(file_path, source_dir)
                    file_date = get_file_date(file_path)
                    
                    unorganized_files.append({
                        'source': file_path,
                        'target': expected_path,
                        'date': file_date,
                        'date_source': date_source,
                        'metadata': metadata
                    })
            else:
                no_metadata_count += 1
                # Skip files without metadata - don't add to unorganized_files
    
    print(f"Found {video_count} video files")
    print(f"  - {metadata_count} with metadata creation dates")
    print(f"  - {no_metadata_count} without metadata (skipped)")
    print("=" * 60)
    
    if video_count == 0:
        print("No video files found in the specified directory.")
        return
    
    # Print unorganized files
    if unorganized_files:
        print(f"UNORGANIZED VIDEOS:")
        print("=" * 60)
        
        # Group by year and month
        organized_by_date = {}
        for file_info in unorganized_files:
            year = file_info['date'].year
            month = file_info['date'].month
            key = (year, month)
            
            if key not in organized_by_date:
                organized_by_date[key] = []
            organized_by_date[key].append(file_info)
        
        moved_count = 0
        failed_count = 0
        
        for (year, month) in sorted(organized_by_date.keys()):
            month_name = get_month_name(month)
            print(f"\n{year}")
            print(f"  {month:02d}-{month_name}/")
            
            for file_info in organized_by_date[(year, month)]:
                source = file_info['source']
                target = file_info['target']
                date = file_info['date']
                date_source = file_info['date_source']
                metadata = file_info['metadata']
                
                if not move_files:
                    # Just print the information
                    print(f"    {source.name}")
                    print(f"      From: {source}")
                    print(f"      To:   {target}")
                    print(f"      Date: {date.strftime('%Y-%m-%d %H:%M:%S')} ({date_source})")
                    
                    # Print additional metadata if available
                    if metadata:
                        if 'duration' in metadata:
                            duration_min = metadata['duration'] / 60
                            print(f"      Duration: {duration_min:.1f} minutes")
                        if 'size' in metadata:
                            size_mb = metadata['size'] / (1024 * 1024)
                            print(f"      Size: {size_mb:.1f} MB")
                    
                    print()
                else:
                    # Move the file
                    if move_video_file(file_info, dry_run):
                        moved_count += 1
                    else:
                        failed_count += 1
        
        print("=" * 60)
        print(f"SUMMARY:")
        print(f"  Total videos found: {video_count}")
        print(f"  Videos with metadata: {metadata_count}")
        print(f"  Videos without metadata (skipped): {no_metadata_count}")
        print(f"  Unorganized videos: {len(unorganized_files)}")
        
        if move_files:
            if dry_run:
                print(f"  Files that would be moved: {moved_count}")
                print(f"  Files that would fail: {failed_count}")
            else:
                print(f"  Files successfully moved: {moved_count}")
                print(f"  Files that failed to move: {failed_count}")
        
        if not move_files:
            print()
            print("These videos need to be moved to their proper organized locations.")
            print("Use --move to actually move the files, or --dry-run to see what would be moved.")
        
    else:
        print("All videos are already properly organized!")
        print("=" * 60)
        print(f"SUMMARY:")
        print(f"  Total videos found: {video_count}")
        print(f"  Videos with metadata: {metadata_count}")
        print(f"  Videos without metadata (skipped): {no_metadata_count}")
        print(f"  Unorganized videos: 0")
        print()
        print("✓ All videos are already in the correct organized structure!")

def main():
    """Main function to handle command line arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Check if videos need to be organized by year and month using metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_organizer.py /path/to/videos                    # Check only
  python video_organizer.py /path/to/videos --dry-run          # Show what would be moved
  python video_organizer.py /path/to/videos --move             # Actually move files
  python video_organizer.py "C:\\Users\\Username\\Videos" --move

Note: Install ffmpeg-python for metadata support: pip install ffmpeg-python
        """
    )
    
    parser.add_argument(
        'directory',
        help='Path to the directory containing videos to check'
    )
    
    parser.add_argument(
        '--move',
        action='store_true',
        help='Actually move files to their organized locations'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be moved without actually moving files'
    )
    
    args = parser.parse_args()
    
    # Convert to Path object
    source_dir = Path(args.directory)
    
    try:
        # Execute the scan
        scan_and_organize_videos(source_dir, move_files=args.move, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user (Ctrl+C)")
        print("Partial results may have been displayed above.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        print("If the script is stuck, try:")
        print("1. Press Ctrl+C to stop")
        print("2. Check if the directory path is correct")
        print("3. Try with a smaller directory first")
        sys.exit(1)

if __name__ == "__main__":
    main()
