"""
Terminal Formatter for Human Review CLI

Provides formatting utilities for displaying human review requests in a CLI.
"""

import textwrap
import json
from typing import Dict, Any, List, Optional, Union
import os

# Terminal colors and styles
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def get_terminal_width() -> int:
    """Get the current terminal width or use a default"""
    try:
        columns, _ = os.get_terminal_size()
        return columns
    except:
        return 80  # Default width if terminal size can't be determined


def format_title(title: str) -> str:
    """Format a section title with color and emphasis"""
    return f"{Colors.BOLD}{Colors.CYAN}=== {title.upper()} ==={Colors.RESET}"


def format_heading(heading: str) -> str:
    """Format a heading with color"""
    return f"{Colors.BOLD}{Colors.YELLOW}{heading}{Colors.RESET}"


def format_subheading(heading: str) -> str:
    """Format a subheading with color"""
    return f"{Colors.BOLD}{heading}{Colors.RESET}"


def format_key_value(key: str, value: Union[str, int, float, bool]) -> str:
    """Format a key-value pair for terminal display"""
    return f"{Colors.BOLD}{key}{Colors.RESET}: {value}"


def format_separator(char="-") -> str:
    """Create a separator line spanning the terminal width"""
    width = get_terminal_width()
    return char * width


def format_content(content: Any) -> str:
    """Format content for display with proper indentation and handling for complex types"""
    if isinstance(content, dict):
        try:
            return json.dumps(content, indent=2)
        except:
            return str(content)
    elif isinstance(content, str):
        return content
    else:
        return str(content)


def truncate_str(text: str, max_length: int = 100) -> str:
    """Truncate a string if it's too long, adding an ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def success_message(message: str) -> str:
    """Format a success message"""
    return f"{Colors.GREEN}{message}{Colors.RESET}"


def error_message(message: str) -> str:
    """Format an error message"""
    return f"{Colors.RED}{message}{Colors.RESET}"


def warning_message(message: str) -> str:
    """Format a warning message"""
    return f"{Colors.YELLOW}{message}{Colors.RESET}"


def wrap_text(text: str, width: Optional[int] = None) -> str:
    """Wrap text to the specified width or terminal width"""
    if width is None:
        width = get_terminal_width() - 2  # Leave a small margin
    
    return textwrap.fill(text, width=width)


def format_approval_status(status: str) -> str:
    """Format approval status with color"""
    if status == "approved":
        return f"{Colors.GREEN}✓ Approved{Colors.RESET}"
    elif status == "rejected":
        return f"{Colors.RED}✗ Rejected{Colors.RESET}"
    else:
        return f"{Colors.YELLOW}⋯ Pending{Colors.RESET}"
