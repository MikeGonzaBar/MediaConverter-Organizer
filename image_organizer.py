#!/usr/bin/env python3
"""
Image Organizer Script

This script recursively scans a directory for images and organizes them by year and month.
For debugging purposes, it prints the files that would be moved without actually moving them.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import mimetypes

# Try to import Pillow for EXIF data extraction
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow library not found. Install it with: pip install Pillow")
    print("Will fall back to file system dates for images without EXIF data.")

# Common image file extensions
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', 
    '.webp', '.svg', '.ico', '.raw', '.cr2', '.nef', '.arw',
    '.heic', '.heif', '.avif', '.jxl'
}

def is_image_file(file_path):
    """
    Check if a file is an image based on its extension and MIME type.
    
    Args:
        file_path (Path): Path to the file to check
        
    Returns:
        bool: True if the file is an image, False otherwise
    """
    # Check by extension first (faster)
    if file_path.suffix.lower() in IMAGE_EXTENSIONS:
        return True
    
    # Fallback to MIME type check
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type is not None and mime_type.startswith('image/')

def get_exif_date(image_path):
    """
    Extract the date from EXIF metadata of an image.
    
    Args:
        image_path (Path): Path to the image file
        
    Returns:
        datetime or None: The capture date from EXIF, or None if not found
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        with Image.open(image_path) as img:
            # Get EXIF data
            exif_data = img._getexif()
            if exif_data is None:
                return None
            
            # Look for DateTimeOriginal (36867) or DateTime (306)
            date_tags = [36867, 306, 50971]  # DateTimeOriginal, DateTime, DateTimeDigitized
            
            for tag_id in date_tags:
                if tag_id in exif_data:
                    date_str = exif_data[tag_id]
                    try:
                        # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        continue
            
            return None
            
    except Exception as e:
        # Silently fail and return None - will fall back to file system date
        return None

def get_exif_data(image_path):
    """
    Extract all EXIF metadata from an image.
    
    Args:
        image_path (Path): Path to the image file
        
    Returns:
        dict or None: The EXIF data dictionary, or None if not found
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        with Image.open(image_path) as img:
            # Get EXIF data
            exif_data = img._getexif()
            return exif_data
    except Exception as e:
        # Silently fail and return None
        return None

def compare_exif_data(exif1, exif2):
    """
    Compare two EXIF data dictionaries to check if they are identical.
    Handles complex EXIF data structures safely.
    
    Args:
        exif1 (dict): First EXIF data dictionary
        exif2 (dict): Second EXIF data dictionary
        
    Returns:
        bool: True if EXIF data is identical, False otherwise
    """
    if exif1 is None and exif2 is None:
        return True
    if exif1 is None or exif2 is None:
        return False
    
    # Check if dictionaries have the same keys
    if set(exif1.keys()) != set(exif2.keys()):
        return False
    
    # Compare values, handling unhashable types
    for key in exif1:
        val1 = exif1[key]
        val2 = exif2[key]
        
        # Handle different data types
        if type(val1) != type(val2):
            return False
        
        if isinstance(val1, (dict, list, tuple)):
            # For complex types, convert to string for comparison
            if str(val1) != str(val2):
                return False
        else:
            # For simple types, direct comparison
            if val1 != val2:
                return False
    
    return True

def get_file_date(file_path):
    """
    Get the date of an image file, prioritizing EXIF capture date over file system dates.
    For filesystem dates, returns the earliest available date.
    
    Args:
        file_path (Path): Path to the file
        
    Returns:
        datetime: The file's date (EXIF capture date preferred, then earliest filesystem date)
    """
    # First, try to get EXIF capture date
    exif_date = get_exif_date(file_path)
    if exif_date:
        return exif_date
    
    # Fall back to file system dates - get the earliest available
    try:
        stat = file_path.stat()
        dates = []
        
        # Collect all available dates
        if hasattr(stat, 'st_birthtime'):  # Unix birth time
            dates.append(datetime.fromtimestamp(stat.st_birthtime))
        
        if hasattr(stat, 'st_ctime'):  # Creation time (Windows) or metadata change time (Unix)
            dates.append(datetime.fromtimestamp(stat.st_ctime))
        
        if hasattr(stat, 'st_mtime'):  # Modification time
            dates.append(datetime.fromtimestamp(stat.st_mtime))
        
        if hasattr(stat, 'st_atime'):  # Access time
            dates.append(datetime.fromtimestamp(stat.st_atime))
        
        # Return the earliest date if we have any
        if dates:
            return min(dates)
        else:
            raise OSError("No date attributes found")
            
    except (OSError, AttributeError):
        # If we can't get any date, use current date
        print(f"Warning: Could not get date for {file_path}, using current date")
        return datetime.now()

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

def scan_and_organize_images(source_dir):
    """
    Scan the source directory recursively for images and organize them by year/month.
    Uses EXIF capture dates when available, otherwise uses the earliest filesystem date.
    Only images without any date information are left for manual review.
    
    Args:
        source_dir (Path): Source directory to scan
    """
    if not source_dir.exists():
        print(f"Error: Directory '{source_dir}' does not exist.")
        return
    
    if not source_dir.is_dir():
        print(f"Error: '{source_dir}' is not a directory.")
        return
    
    print(f"Scanning directory: {source_dir}")
    print("=" * 50)
    
    image_count = 0
    organized_files = {}
    exif_count = 0
    no_exif_count = 0
    manual_review_files = []
    
    # Recursively scan for images
    print("Scanning for images... (Press Ctrl+C to stop)")
    scanned_files = 0
    
    for file_path in source_dir.rglob('*'):
        scanned_files += 1
        
        # Show progress every 100 files
        if scanned_files % 100 == 0:
            print(f"  Scanned {scanned_files} files, found {image_count} images...")
        
        if file_path.is_file() and is_image_file(file_path):
            image_count += 1
            
            # Get the best available date (EXIF first, then earliest filesystem date)
            file_date = get_file_date(file_path)
            
            if file_date:
                # Check if we got EXIF date or filesystem date
                exif_date = get_exif_date(file_path)
                if exif_date:
                    # Image has EXIF data
                    exif_count += 1
                    date_source = "EXIF"
                else:
                    # Using filesystem date
                    no_exif_count += 1
                    date_source = "Filesystem"
                
                year = file_date.year
                month = file_date.month
                
                # Create target directory structure
                month_name = get_month_name(month)
                target_dir = source_dir / str(year) / f"{month:02d}-{month_name}"
                
                # Create target file path
                target_file = target_dir / file_path.name
                
                # Check if file is already in the correct location
                if file_path == target_file:
                    # File is already in the correct location - skip it
                    continue
                
                # Store organization info for files that need to be moved
                if (year, month) not in organized_files:
                    organized_files[(year, month)] = []
                
                organized_files[(year, month)].append({
                    'source': file_path,
                    'target': target_file,
                    'date': file_date,
                    'date_source': date_source
                })
            else:
                # No date available - flag for manual review
                no_exif_count += 1
                manual_review_files.append(file_path)
    
    print(f"Found {image_count} image files")
    print(f"  - {exif_count} with EXIF capture dates")
    print(f"  - {no_exif_count} using filesystem dates")
    print("=" * 50)
    
    if image_count == 0:
        print("No image files found in the specified directory.")
        return
    
    # Count files that need to be moved
    files_to_move = sum(len(files) for files in organized_files.values())
    
    # Move images that need organizing
    if organized_files:
        print(f"MOVING IMAGES:")
        print("=" * 50)
        
        moved_count = 0
        error_count = 0
        
        for (year, month) in sorted(organized_files.keys()):
            month_name = get_month_name(month)
            print(f"\n{year}")
            print(f"  {month:02d}-{month_name}/")
            
            for file_info in organized_files[(year, month)]:
                source = file_info['source']
                target = file_info['target']
                date = file_info['date']
                
                print(f"    {source.name}")
                print(f"      From: {source}")
                print(f"      To:   {target}")
                print(f"      Date: {date.strftime('%Y-%m-%d %H:%M:%S')} ({file_info['date_source']})")
                
                try:
                    # Create target directory if it doesn't exist
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Check if target file already exists
                    if target.exists():
                        print(f"      WARNING: Target file already exists!")
                        
                        # Check if both files have EXIF data and compare them
                        source_exif = get_exif_data(source)
                        target_exif = get_exif_data(target)
                        
                        if source_exif is not None and target_exif is not None:
                            if compare_exif_data(source_exif, target_exif):
                                print(f"      ✓ EXIF data is identical - deleting source file")
                                source.unlink()  # Delete the source file
                                print(f"      ✓ SOURCE FILE DELETED (duplicate found)")
                                moved_count += 1
                            else:
                                print(f"      ✗ EXIF data differs - skipping to avoid overwrite")
                                error_count += 1
                        else:
                            print(f"      ✗ Cannot compare EXIF data - skipping to avoid overwrite")
                            error_count += 1
                        continue
                    
                    # Move the file
                    source.rename(target)
                    print(f"      ✓ MOVED SUCCESSFULLY")
                    moved_count += 1
                    
                except Exception as e:
                    print(f"      ✗ ERROR: {e}")
                    error_count += 1
                
                print()
        
        print("=" * 50)
        print(f"MOVEMENT SUMMARY:")
        print(f"  Files moved successfully: {moved_count}")
        print(f"  Files with errors: {error_count}")
        print("=" * 50)
    else:
        print("All images are already in the correct location!")
    
    # Print manual review list
    if manual_review_files:
        print("=" * 50)
        print("MANUAL REVIEW REQUIRED (Images without any date information):")
        print("=" * 50)
        print("The following images have no date information and need manual review:")
        print()
        
        for file_path in sorted(manual_review_files):
            print(f"  {file_path}")
        
        print()
        print("These files will remain in their current location.")
        print("You can manually organize them based on:")
        print("- File name patterns (e.g., IMG_YYYYMMDD_*)")
        print("- Content analysis")
        print("- Your knowledge of when they were taken")
    
    print("=" * 50)
    print(f"FINAL SUMMARY:")
    print(f"  Total images found: {image_count}")
    print(f"  Images with EXIF data: {exif_count}")
    print(f"  Images using filesystem dates: {no_exif_count}")
    print(f"  Images that needed moving: {files_to_move}")
    print(f"  Images needing manual review: {len(manual_review_files)}")
    print("\n✓ Images with date information have been automatically organized!")
    print("⚠ Images without any date information remain in their original location for manual review.")

def main():
    """Main function to handle command line arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description="Organize images by year and month using EXIF capture dates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_organizer.py /path/to/photos
  python image_organizer.py "C:\\Users\\Username\\Pictures"

Note: Install Pillow for EXIF support: pip install Pillow
        """
    )
    
    parser.add_argument(
        'directory',
        help='Path to the directory containing images to organize'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,  # 5 minutes default
        help='Timeout in seconds for processing each image (default: 300)'
    )
    
    args = parser.parse_args()
    
    # Convert to Path object
    source_dir = Path(args.directory)
    
    try:
        # Execute the organization
        scan_and_organize_images(source_dir)
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
