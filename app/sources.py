"""Calendar data sources.

``FileSource`` reads a JSON file whose meeting times are expressed as hour
offsets from "now", so the demo data is always in the near future.

To monitor a real calendar (e.g. Microsoft Graph), implement another class
exposing ``fetch() -> list[Meeting]`` and select it in ``main.py``.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import List, Protocol

from models import Attendee, Meeting


class CalendarSource(Protocol):
    def fetch(self) -> List[Meeting]:
        ...


class FileSource:
    def __init__(self, path: str):
        self.path = path

    def fetch(self) -> List[Meeting]:
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        now = datetime.now(timezone.utc)
        meetings = []
        for m in raw["meetings"]:
            start = now + timedelta(hours=m["starts_in_hours"])
            end = start + timedelta(minutes=m.get("duration_minutes", 60))
            meetings.append(
                Meeting(
                    id=m["id"],
                    subject=m["subject"],
                    start=start,
                    end=end,
                    organizer=m["organizer"],
                    room=m.get("room", ""),
                    is_online=m.get("is_online", False),
                    attendees=[Attendee(a["name"], a.get("response", "none")) for a in m.get("attendees", [])],
                )
            )
        return meetings
