"""Handle user requests related to pomodoro-timers."""
import argparse
import dataclasses
import os
import signal
import subprocess as sp
import sys
import time
from typing import Any

import gi  # type: ignore
import psutil
from colorama import Fore, Style

gi.require_version("Notify", "0.7")
from gi.repository import Notify  # noqa


@dataclasses.dataclass
class _TimerInfo:
    name: str
    tout_min: int
    """Timer timeout in minutes."""
    t_start: float
    """UTC time when the timer was started."""
    pid: int


class Pomodoro:
    """Manage pomodoro timers."""

    TOUT_MIN_DEFAULT = 30  # Default timer timeout, in minutes.
    TOUT_MIN_MIN = 1  # Minimal timer timeout, in minutes.
    TOUT_MIN_MAX = 180  # Maximal timer timeout, in minutes.
    TMR_NAME_DEFAULT = "default"  # Default timer name.

    def process(self, args: dict[str, Any]) -> int:
        """
        Executing user's requests related to tasks.
        """
        if args["pomodoro_start"] is not None:
            self._start(args["pomodoro_start"])

        tmr_info_arr: list[_TimerInfo] = self._find_all()
        if args["pomodoro_list"]:
            self._print_all(tmr_info_arr)

        if args["pomodoro_kill"] is not None:
            self._kill(args["pomodoro_kill"], tmr_info_arr)

        return 0

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add arguments to the provided argument parser.

        This method is expected to run before parser.parse_args() is invoked.
        """
        parser.add_argument(
            "-ps", "--pomodoro-start", dest="pomodoro_start",
            nargs="*",  # The result is either None or a list containing two strings.
            help="Start a pomodoro timer. "
                 "Parameters are a timeout in minutes (from 1 to 180) and a name. "
                 "Default timeout is 30 minutes. Default name is 'default'.")
        parser.add_argument(
            "-pl", "--pomodoro-list", dest="pomodoro_list",
            action="store_true",  # The result is a boolean.
            help="List all active timers.")
        parser.add_argument(
            "-pk", "--pomodoro-kill",
            dest="pomodoro_kill",
            nargs="?",  # The result the result is either None or a string.
            help="Kill a timer.")

    @staticmethod
    def _start(pomodoro_start: list[str]) -> None:
        if len(pomodoro_start) == 0:
            tout_min = Pomodoro.TOUT_MIN_DEFAULT
            tmr_name = Pomodoro.TMR_NAME_DEFAULT
        elif len(pomodoro_start) == 1:
            tout_min = int(pomodoro_start[0])
            tmr_name = Pomodoro.TMR_NAME_DEFAULT
        else:
            tout_min = int(pomodoro_start[0])
            tmr_name = " ".join(pomodoro_start[1:])
        if tout_min < Pomodoro.TOUT_MIN_MIN or tout_min > Pomodoro.TOUT_MIN_MAX:
            raise ValueError(
                f"Timeout is out of range [{Pomodoro.TOUT_MIN_MIN}, {Pomodoro.TOUT_MIN_MAX}].")

        # We don't wait for the process to finish.
        # pylint: disable-next=consider-using-with
        child = sp.Popen(args=["python3", __file__, str(tout_min), tmr_name])

        print(f"Started a {tout_min}-minute pomodoro timer `{tmr_name}` (pid={child.pid}).")

    @staticmethod
    def _find_all() -> list[_TimerInfo]:
        tmr_info_arr = []
        for proc in psutil.process_iter():
            cmd_line = proc.cmdline()
            if len(cmd_line) == 4 and cmd_line[0] == "python3" and "pomodoro" in cmd_line[1]:
                tmr_info_arr.append(_TimerInfo(
                    name=cmd_line[3],
                    tout_min=int(cmd_line[2]),
                    t_start=proc.create_time(),
                    pid=proc.pid))
        return sorted(
            tmr_info_arr,
            key=lambda tmr_info: tmr_info.pid,
            reverse=False)

    @staticmethod
    def _print_all(tmr_info_arr: list[_TimerInfo]) -> None:
        if not tmr_info_arr:
            print("No active pomodoro timers found:")
            return
        tmr_cnt = len(tmr_info_arr)
        print(
            str(tmr_cnt) + " active pomodoro timer" + ("s" if tmr_cnt > 1 else "")
            + " found:")
        for i, tmr_info in enumerate(tmr_info_arr, start=1):
            time_expire = tmr_info.t_start + tmr_info.tout_min * 60
            time_to_run = time_expire - time.time()
            time_start_str = time.strftime("%H:%M:%S", time.localtime(tmr_info.t_start))
            time_expire_str = time.strftime("%H:%M:%S", time.localtime(time_expire))
            time_to_run_str = time.strftime("%H:%M:%S", time.gmtime(time_to_run))
            tmr_str = (
                f"\t{i}: "
                + (Fore.RED + Style.BRIGHT + tmr_info.name + Style.RESET_ALL) + " "
                + "(pid=" + (Style.BRIGHT + str(tmr_info.pid) + Style.RESET_ALL) + "), "
                + f"{tmr_info.tout_min} min, "
                + f"{time_start_str} -> {time_expire_str}, "
                + "expires in "
                + (Style.BRIGHT + str(time_to_run_str) + Style.RESET_ALL) + "."
            )
            print(tmr_str)

    @staticmethod
    def _kill(pid_part: str, tmr_info_arr: list[_TimerInfo]) -> None:
        for tmr_info in tmr_info_arr:
            if pid_part in str(tmr_info.pid):
                time_expire = tmr_info.t_start + tmr_info.tout_min * 60
                time_to_run = time_expire - time.time()
                time_to_run_str = time.strftime("%H:%M:%S", time.gmtime(time_to_run))
                kill_msg = (
                    "Killing the timer "
                    + (Fore.RED + Style.BRIGHT + tmr_info.name + Style.RESET_ALL) + " "
                    + "(pid=" + (Style.BRIGHT + str(tmr_info.pid) + Style.RESET_ALL) + "), "
                    + "which would have expired in "
                    + (Style.BRIGHT + str(time_to_run_str) + Style.RESET_ALL) + "."
                )
                print(kill_msg)
                os.kill(tmr_info.pid, signal.SIGKILL)


def launch_timer() -> int:
    """
    Launch a pomodoro timer, which will push a desktop notification when expires.
    """
    assert len(sys.argv) == 3
    tout_min = int(sys.argv[1])
    tmr_name = sys.argv[2]
    time.sleep(tout_min * 60)

    Notify.init(__name__)
    notification = Notify.Notification.new(
        summary="🍅 pomodoro",
        body=f"{tout_min} minutes elapsed for `{tmr_name}`."
    )
    notification.show()
    return 0


if __name__ == "__main__":
    sys.exit(launch_timer())
