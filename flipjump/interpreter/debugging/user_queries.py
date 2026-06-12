"""
terminal helpers for the interactive debugger: show a message, and read one command line.
"""

from typing import Optional


def _print_message(body_message: str, title_message: str) -> None:
    # ascii-only: the prompts must survive any console encoding (e.g. legacy windows codepages)
    print(f'\n==== {title_message} ====')
    print(body_message)


def show_message(body_message: str, title_message: str) -> None:
    """
    Displays the message to the user (terminal).
    """
    _print_message(body_message, title_message)


def ask_for_command(prompt: str) -> Optional[str]:
    """
    Reads one command line from the user (terminal).
    @return: the stripped line (possibly empty), or None on EOF / Ctrl+D.
    """
    try:
        return input(prompt).strip()
    except EOFError:
        return None
