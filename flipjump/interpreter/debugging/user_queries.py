"""
terminal prompts for the interactive debugger: show a message, ask for a one-line answer,
or ask to pick a choice. EOF / an empty answer selects the safe default, so piped and
scripted sessions behave deterministically.
"""

from typing import List, Optional


def _print_message(body_message: str, title_message: str) -> None:
    # ascii-only: the prompts must survive any console encoding (e.g. legacy windows codepages)
    print(f'\n==== {title_message} ====')
    print(body_message)


def show_message(body_message: str, title_message: str) -> None:
    """
    Displays the message to the user (terminal).
    """
    _print_message(body_message, title_message)


def ask_for_text(body_message: str, title_message: str) -> Optional[str]:
    """
    Displays the message (terminal), and reads a one-line textual answer.
    @return: the stripped answer, or None on an empty answer / EOF (= cancel).
    """
    _print_message(body_message, title_message)
    try:
        answer = input('> ').strip()
    except EOFError:
        return None
    return answer if answer else None


def ask_for_choice(body_message: str, title_message: str, choices: List[str], default_cancel_answer: str) -> str:
    """
    Displays the message and the numbered choices (terminal), and reads the chosen one -
    by number, or by (case-insensitive, unique-prefix) name.
    @return: the chosen choice; an empty answer / EOF returns the default.
    """
    _print_message(body_message, title_message)
    for index, choice in enumerate(choices, start=1):
        default_mark = '  (default)' if choice == default_cancel_answer else ''
        print(f'  {index}. {choice}{default_mark}')

    while True:
        try:
            raw_answer = input('choice> ').strip()
        except EOFError:
            return default_cancel_answer
        if not raw_answer:
            return default_cancel_answer

        if raw_answer.isdigit() and 1 <= int(raw_answer) <= len(choices):
            return choices[int(raw_answer) - 1]

        exact_matches = [choice for choice in choices if choice.lower() == raw_answer.lower()]
        if exact_matches:
            return exact_matches[0]
        name_matches = [choice for choice in choices if choice.lower().startswith(raw_answer.lower())]
        if len(name_matches) == 1:
            return name_matches[0]

        print(f'  invalid choice: {raw_answer!r}. enter a number (1-{len(choices)}) or a unique choice prefix.')
