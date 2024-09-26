from enum import Enum, auto

class AppState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    NOT_FOUND_WINDOW = auto()
