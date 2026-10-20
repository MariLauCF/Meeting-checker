"""Data models for calendar meetings."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# RSVP responses that mean "attendee has not answered yet".
PENDING_RESPONSES = {"none", "notresponded", ""}


@dataclass
class Attendee:
    name: str
    response: str = "none"  # accepted | declined | tentative | none

    @property
    def is_pending(self) -> bool:
        return self.response.strip().lower() in PENDING_RESPONSES


@dataclass
class Meeting:
    id: str
    subject: str
    start: datetime
    end: datetime
    organizer: str
    room: str = ""            # empty string => no room assigned
    is_online: bool = False   # online-only meetings do not need a room
    attendees: List[Attendee] = field(default_factory=list)

    @property
    def needs_room(self) -> bool:
        return not self.is_online

    @property
    def has_room(self) -> bool:
        return bool(self.room and self.room.strip())

    @property
    def pending_attendees(self) -> List[Attendee]:
        return [a for a in self.attendees if a.is_pending]
