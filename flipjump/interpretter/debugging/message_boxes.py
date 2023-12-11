from typing import List, Optional

from flipjump.utils.exceptions import FlipJumpMissingImportException


EASYGUI_NOT_INSTALLED_MESSAGE = "This debug feature requires the easygui python library.\n"\
                                "Try `pip install easygui`, and also install tkinter on your system."


def display_message_box_with_choices_and_get_answer(body_message: str, title_message: str,
                                                    choices: List[str], default_cancel_answer: str) -> str:
    """
    Displays the message box query (with fixed choices), and return the answer.
    If easygui isn't installed correctly, raises an exception.
    """
    try:
        # might generate an 'import from collections is deprecated' warning if using easygui-version <= 0.98.3.
        import easygui
    except ImportError:
        raise FlipJumpMissingImportException(EASYGUI_NOT_INSTALLED_MESSAGE)

    answer: Optional[str] = easygui.buttonbox(body_message, title_message, choices)
    if answer is None:
        return default_cancel_answer
    return answer


def display_message_box(body_message: str, title_message: str) -> None:
    """
    Displays the message box to the user.
    If easygui isn't installed correctly, raises an exception.
    """
    try:
        # might generate an 'import from collections is deprecated' warning if using easygui-version <= 0.98.3.
        import easygui
    except ImportError:
        raise FlipJumpMissingImportException(EASYGUI_NOT_INSTALLED_MESSAGE)

    easygui.msgbox(msg=body_message, title=title_message)


def display_message_box_and_get_text_answer(body_message: str, title_message: str) -> Optional[str]:
    """
    Displays the message box query, and return the textual answer.
    If easygui isn't installed correctly, raises an exception.
    """
    try:
        # might generate an 'import from collections is deprecated' warning if using easygui-version <= 0.98.3.
        import easygui
    except ImportError:
        raise FlipJumpMissingImportException(EASYGUI_NOT_INSTALLED_MESSAGE)

    answer: Optional[str] = easygui.enterbox(msg=body_message, title=title_message)
    return answer
