"""
Implementation of microscope for the Andor Fusion software.
"""
import json
import logging
from abc import ABC
import datetime
from typing import Any
import requests
from requests import Response
from .classes import Microscope, State


class AndorFusion(Microscope, ABC):
    """
    URLs:
    /v1/protocol/state
    /v1/protocol/current
    /v1/protocol/progress
    """

    def __init__(
        self, port: int = 15120, host: str = "localhost", loglevel: int = logging.INFO
    ) -> None:
        super().__init__(port=port, host=host, loglevel=loglevel)
        self.log.info("Andor Fusion control initialized.")

    # INTERNAL FUNCTIONS
    def __make_address(self, endpoint: str) -> str:
        return f"http://{self.host}:{self.port}{endpoint}"

    def __raise_on_error(self, endpoint: str, response: Response) -> None:
        if (response.status_code < 200) or (response.status_code > 299):
            raise ApiError(endpoint, response.status_code, response.reason)

    def __get(self, endpoint: str) -> Any:
        response = requests.get(self.__make_address(endpoint))
        self.__raise_on_error(endpoint, response)
        return response.json()

    def __get_plain(self, endpoint: str) -> str:
        response = requests.get(self.__make_address(endpoint))
        self.__raise_on_error(endpoint, response)
        return response.text

    def __get_value(self, endpoint: str, key: str) -> Any:
        jsonobj = self.__get(endpoint)
        return jsonobj[key]

    def __put(self, endpoint: str, obj: Any) -> None:
        body = json.dumps(obj)
        self.__put_plain(endpoint, body)

    def __put_plain(self, endpoint: str, body: str) -> None:
        response = requests.put(self.__make_address(endpoint), data=body)
        self.__raise_on_error(endpoint, response)

    def __put_value(self, endpoint: str, key: str, value: Any) -> None:
        struct = {key: value}
        self.__put(endpoint, struct)

    # STATE FUNCTIONS
    def run(self) -> None:
        self.__put_value("/v1/protocol/state", "State", "Running")

    def resume(self) -> None:
        self.run()

    def pause(self) -> None:
        self.__put_value("/v1/protocol/state", "State", "Paused")

    def stop(self) -> None:
        if self.is_running():
            self.__put_value("/v1/protocol/state", "State", "Aborted")
        else:
            self.log.warning("Got stop command, but the software was not running.")

    def get_state(self) -> State:
        return translate_state(self.__get_value("/v1/protocol/state", "State"))

    # PROTOCOL FUNCTIONS
    def get_current_protocol(self) -> str:
        return str(self.__get_value("/v1/protocol/current", "Name"))

    def set_current_protocol(self, name: str) -> None:
        self.__put_value("/v1/protocol/current", "Name", name)

    def get_protocol_progress(self) -> "ProtocolProgress":
        return ProtocolProgress(self.__get("/v1/protocol/progress"))

    def get_protocol_progress_percentage(self) -> float:
        return self.get_protocol_progress().progress_percentage()

    # FILENAME FUNCTIONS


class ProtocolProgress:
    def __init__(self, data: Any) -> None:
        self.start_time = datetime.datetime.fromisoformat(data["StartTime"])
        self.elapsed_time = self.__totimedelta(data["ElapsedTime"])
        self.remaining_time = self.__totimedelta(data["RemainingTime"])
        self.estimated_time_of_completion = datetime.datetime.fromisoformat(
            data["EstimatedTimeOfCompletion"]
        )
        self.progress = data["Progress"]  # type: float

    def get_local_timezone(self) -> datetime.tzinfo | None:
        return datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    def get_start_time(self) -> datetime.datetime:
        return self.start_time.astimezone(self.get_local_timezone())

    def get_estimated_time_of_completion(self) -> datetime.datetime:
        return self.estimated_time_of_completion.astimezone(self.get_local_timezone())

    def __totimedelta(self, timestring: str) -> datetime.timedelta:
        if len(timestring) > 14:
            return datetime.timedelta(
                hours=int(timestring[0:2]),
                minutes=int(timestring[3:5]),
                seconds=int(timestring[6:8]),
                microseconds=int(timestring[9:15]),
            )
        else:
            return datetime.timedelta(
                hours=int(timestring[0:2]),
                minutes=int(timestring[3:5]),
                seconds=int(timestring[6:8]),
            )

    def __str__(self) -> str:
        return f"""
        Started : {self.get_start_time()} 
        Elapsed : {self.elapsed_time}
        Remaining : {self.remaining_time}
        Estimated time of completion : {self.get_estimated_time_of_completion()}
        Progress : {self.progress_percentage():.2f}%
        """

    def progress_percentage(self) -> float:
        return self.progress * 100


def translate_state(statestring: str) -> State:
    if statestring == "Idle":
        return State.Idle
    if statestring == "Waiting":
        return State.Waiting
    if statestring == "Running":
        return State.Running
    if statestring == "Paused":
        return State.Paused
    if statestring == "Aborting":
        return State.Aborting
    if statestring == "Aborted":
        return State.Aborted
    return State.Unknown


class ApiError(Exception):
    """
    Indicates an error while calling the Fusion REST API.
    """

    def __init__(self, endpoint: str, code: int, reason: str) -> None:
        """
        Creates an new `ApiError` instance.
        """
        self._endpoint = endpoint
        self._code = code
        self._reason = reason

    def __repr__(self) -> str:
        return "<ApiError at {}: {} {}>".format(
            self._endpoint, self._code, self._reason
        )

    def __str__(self) -> str:
        return self.__repr__()

    def endpoint(self) -> str:
        """
        Gives the name of the API endpoint for which the error happened.
        """
        return self._endpoint

    def code(self) -> int:
        """
        Gives the HTTP response code for the error, as returned by the API.
        Also see `.reason()` for a more readable description of the problem.
        """
        return self._code

    def reason(self) -> str:
        """
        Gives the reason for the error, as returned by the API. (a string)
        """
        return self._reason
