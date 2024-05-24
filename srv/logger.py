import sys
from sys import exc_info


def get_frame_fallback(n):
    try:
        raise Exception
    except Exception:
        frame = exc_info()[2].tb_frame.f_back
        for _ in range(n):
            frame = frame.f_back
        return frame


def load_get_frame_function():
    if hasattr(sys, "_getframe"):
        get_frame = sys._getframe
    else:
        get_frame = get_frame_fallback
    return get_frame

get_frame = load_get_frame_function()


class LoguruFallback: # When loguru is not avaible
    def __init__(self):
        pass
    def info(self, *argv: tuple[str]):
        n = get_frame().f_globals['__name__']
        print(f"[{n}][INFO]: {" ".join(argv)}")
    def error(self, *argv: tuple[str]):
        n = get_frame().f_globals['__name__']
        print(f"[{n}][ERROR]: {" ".join(argv)}")
    def warning(self, *argv: tuple[str]):
        n = get_frame().f_globals['__name__']
        print(f"[{n}][WARNING]: {" ".join(argv)}")