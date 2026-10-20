"""Pure business logic: evaluate meetings for missing rooms and missing RSVPs."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from models import Meeting


@dataclass
class CheckResult:
    total: int = 0
    with_room: int = 0
    online: int = 0
    missing_room: List[Meeting] = field(default_factory=list)
    urgent_missing_room: List[Meeting] = field(default_factory=list)
    missing_rsvp: List[Meeting] = field(default_factory=list)
    pending_attendees_total: int = 0


def check_meetings(
    meetings: List[Meeting],
    lookahead_days: int = 7,
    urgent_hours: int = 24,
    now: Optional[datetime] = None,
) -> CheckResult:
    """Evaluate upcoming meetings inside the look-ahead window.

    * A meeting "misses a room" if it is not online-only and has no room.
    * A meeting "misses RSVPs" if at least one attendee has not responded.
    * A missing room is "urgent" if the meeting starts within ``urgent_hours``.
    """
    now = now or datetime.now(timezone.utc)
    horizon = now + timedelta(days=lookahead_days)
    urgent_limit = now + timedelta(hours=urgent_hours)

    result = CheckResult()
    for m in meetings:
        if not (now <= m.start <= horizon):
            continue
        result.total += 1

        if not m.needs_room:
            result.online += 1
        elif m.has_room:
            result.with_room += 1
        else:
            result.missing_room.append(m)
            if m.start <= urgent_limit:
                result.urgent_missing_room.append(m)

        pending = m.pending_attendees
        if pending:
            result.missing_rsvp.append(m)
            result.pending_attendees_total += len(pending)

    return result
