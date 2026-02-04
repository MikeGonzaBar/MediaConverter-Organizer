from typing import Callable


def default_log(message: str, level: str = "INFO") -> None:
    """Simple default logger that prints to console."""
    print(f"[{level}] {message}")


def print_separator(printer: Callable[[str], None], width: int = 60) -> None:
    printer("=" * width)


def print_mode_banner(mode: str, printer: Callable[[str], None]) -> None:
    """Print a standardized mode banner using the provided printer function."""
    if mode == "check":
        printer("Mode: CHECK ONLY - Will only show what needs to be organized")
    elif mode == "dry_run":
        printer("Mode: DRY RUN - Will show what would be moved without actually moving files")
    elif mode == "move":
        printer("Mode: MOVE FILES - Will actually move files to organized locations")
    else:
        printer(f"Mode: {mode}")
