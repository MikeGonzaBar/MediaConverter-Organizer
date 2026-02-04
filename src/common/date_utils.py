from calendar import month_name
from pathlib import Path


def get_month_name(month: int) -> str:
    """Return full English month name for 1-12 using stdlib calendar."""
    if not 1 <= month <= 12:
        raise ValueError(f"month must be in 1..12, got {month}")
    return month_name[month]


def format_month_dir(month: int) -> str:
    """Return directory component in format 'MM-Month' (e.g., '01-January')."""
    return f"{month:02d}-{get_month_name(month)}"


def build_year_month_dir(base: Path, year: int, month: int) -> Path:
    """Return base/year/MM-Month path as Path object."""
    return base / str(year) / format_month_dir(month)
