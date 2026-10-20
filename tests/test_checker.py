"""Unit tests for the meeting evaluation logic. Run: python -m unittest discover -s tests"""
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from checker import check_meetings  # noqa: E402
from models import Attendee, Meeting  # noqa: E402

NOW = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)


def meeting(mid, hours, room="", online=False, responses=()):
    start = NOW + timedelta(hours=hours)
    return Meeting(
        id=mid, subject=mid, start=start, end=start + timedelta(hours=1), organizer="o",
        room=room, is_online=online,
        attendees=[Attendee(f"a{i}", r) for i, r in enumerate(responses)],
    )


class CheckMeetingsTest(unittest.TestCase):
    def test_room_counts(self):
        ms = [meeting("a", 2, room="R1"), meeting("b", 3), meeting("c", 4, online=True)]
        r = check_meetings(ms, now=NOW)
        self.assertEqual((r.total, r.with_room, r.online, len(r.missing_room)), (3, 1, 1, 1))

    def test_urgent_missing_room(self):
        ms = [meeting("soon", 5), meeting("later", 48)]
        r = check_meetings(ms, urgent_hours=24, now=NOW)
        self.assertEqual(len(r.missing_room), 2)
        self.assertEqual([m.id for m in r.urgent_missing_room], ["soon"])

    def test_rsvp_pending(self):
        ms = [meeting("a", 2, "R", responses=["accepted", "none", "notResponded"]),
              meeting("b", 2, "R", responses=["accepted", "declined"])]
        r = check_meetings(ms, now=NOW)
        self.assertEqual(len(r.missing_rsvp), 1)
        self.assertEqual(r.pending_attendees_total, 2)

    def test_outside_window_ignored(self):
        ms = [meeting("past", -2), meeting("far", 24 * 30)]
        self.assertEqual(check_meetings(ms, now=NOW).total, 0)

    def test_whitespace_room_counts_as_missing(self):
        self.assertEqual(len(check_meetings([meeting("x", 2, room="   ")], now=NOW).missing_room), 1)


if __name__ == "__main__":
    unittest.main()
