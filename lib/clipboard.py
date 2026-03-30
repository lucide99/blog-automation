"""클립보드 복사"""

import pyperclip


def copy_to_clipboard(text: str):
    pyperclip.copy(text)
