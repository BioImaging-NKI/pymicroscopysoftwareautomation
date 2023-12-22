"""
General classes for all types of microscopy software
"""
import abc  # Abstract base class
import enum
import logging
import sys
import time


class Microscope(abc.ABC):
    def __init__(self, port: int, host: str, loglevel: int) -> None:
        self.port = port
        self.host = host
        logging.basicConfig(
            level=loglevel,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        self.log = logging.getLogger(__name__)

    @abc.abstractmethod
    def run(self) -> None:
        pass

    def is_running(self) -> bool:
        return self.get_state() == State.Running

    @abc.abstractmethod
    def pause(self) -> None:
        pass

    @abc.abstractmethod
    def resume(self) -> None:
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        pass

    @abc.abstractmethod
    def get_state(self) -> "State":
        pass

    def wait_until_state(
        self, target_state: "State", check_interval_secs: float
    ) -> None:
        while self.get_state() != target_state:
            time.sleep(check_interval_secs)

    def wait_until_idle(self, check_interval_secs: float) -> None:
        self.wait_until_state(State.Idle, check_interval_secs)


class State(enum.IntEnum):
    Unknown = -1
    Idle = 0
    Waiting = 1
    Running = 3
    Paused = 4
    Aborting = 5
    Aborted = 6

    def __str__(self) -> str:
        return self.name
