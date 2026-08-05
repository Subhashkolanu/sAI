"""
=========================================================
sAI V1 - Automation Engine
=========================================================
Features
- Run scheduled tasks
- One-time tasks
- Repeating tasks
- Background scheduler
=========================================================
"""

from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Callable, Dict, List

import schedule

from config import CHECK_INTERVAL


class AutomationEngine:
    def __init__(self):
        self.running = False
        self.thread = None
        self.tasks: List[Dict] = []

    # --------------------------------------------------

    def every_seconds(self, seconds: int, func: Callable, *args, **kwargs):

        job = schedule.every(seconds).seconds.do(
            func,
            *args,
            **kwargs,
        )

        self.tasks.append(
            {
                "type": "seconds",
                "interval": seconds,
                "job": job,
                "function": func.__name__,
            }
        )

        return job

    # --------------------------------------------------

    def every_minutes(self, minutes: int, func: Callable, *args, **kwargs):

        job = schedule.every(minutes).minutes.do(
            func,
            *args,
            **kwargs,
        )

        self.tasks.append(
            {
                "type": "minutes",
                "interval": minutes,
                "job": job,
                "function": func.__name__,
            }
        )

        return job

    # --------------------------------------------------

    def every_hours(self, hours: int, func: Callable, *args, **kwargs):

        job = schedule.every(hours).hours.do(
            func,
            *args,
            **kwargs,
        )

        self.tasks.append(
            {
                "type": "hours",
                "interval": hours,
                "job": job,
                "function": func.__name__,
            }
        )

        return job

    # --------------------------------------------------

    def every_day(self, time_string: str, func: Callable, *args, **kwargs):

        job = schedule.every().day.at(time_string).do(
            func,
            *args,
            **kwargs,
        )

        self.tasks.append(
            {
                "type": "daily",
                "time": time_string,
                "job": job,
                "function": func.__name__,
            }
        )

        return job

    # --------------------------------------------------

    def once(self, delay_seconds: int, func: Callable, *args, **kwargs):

        def wrapper():
            time.sleep(delay_seconds)
            func(*args, **kwargs)

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

        return thread

    # --------------------------------------------------

    def list_tasks(self):

        return self.tasks

    # --------------------------------------------------

    def clear(self):

        schedule.clear()
        self.tasks.clear()

    # --------------------------------------------------

    def _runner(self):

        while self.running:
            schedule.run_pending()
            time.sleep(CHECK_INTERVAL)

    # --------------------------------------------------

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._runner,
            daemon=True,
        )

        self.thread.start()

    # --------------------------------------------------

    def stop(self):

        self.running = False

        if self.thread:
            self.thread.join(timeout=1)


# ------------------------------------------------------
# Example
# ------------------------------------------------------

def sample_task():
    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] Scheduled task executed."
    )


if __name__ == "__main__":

    engine = AutomationEngine()

    engine.every_seconds(10, sample_task)

    engine.start()

    print("Automation engine started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
        print("Automation engine stopped.")