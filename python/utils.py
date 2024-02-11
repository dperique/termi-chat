import textwrap

# Constants for ANSI color codes
ANSI_LIGHTBLUE = "\033[94m"
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

def warn_message(message_str: str) -> None:
    """Print a warning message in red."""
    print(f"{ANSI_RED}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def marker_message(message_str: str) -> None:
    """Print a message in light blue."""
    print(f"{ANSI_LIGHTBLUE}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def info_message(message_str: str) -> None:
    """Print an informational message in green."""
    print(f"{ANSI_GREEN}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def dashes() -> None:
    """Print 80 dashes for separation."""
    marker_message("-" * 80)

def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text except inside code blocks."""
    wrapped_text = ""
    in_code_block = False
    for line in text.split('\n'):
        if line.startswith("```"):
            in_code_block = not in_code_block
            wrapped_text += line + '\n'
        elif in_code_block:
            wrapped_text += line + '\n'
        else:
            wrapped_text += textwrap.fill(line, width=width) + '\n'
    return wrapped_text
