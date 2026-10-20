"""Meeting Checker - exposes Prometheus metrics about meeting readiness.

Environment variables:
  DATA_FILE        path to the meetings JSON       (default: data/meetings.json)
  CHECK_INTERVAL   seconds between checks          (default: 30)
  LOOKAHEAD_DAYS   how far ahead to inspect        (default: 7)
  URGENT_HOURS     "urgent" window for no-room     (default: 24)
  METRICS_PORT     HTTP port for /metrics          (default: 8000)
"""
import logging
import os
import time

from prometheus_client import Counter, Gauge, start_http_server

from checker import check_meetings
from sources import FileSource

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("meeting-checker")

# ---- Metrics ---------------------------------------------------------------
MEETINGS_TOTAL = Gauge("meetings_total", "Upcoming meetings in the look-ahead window")
MEETINGS_WITH_ROOM = Gauge("meetings_with_room", "Upcoming in-person meetings that have a room")
MEETINGS_ONLINE = Gauge("meetings_online", "Upcoming online-only meetings (no room needed)")
MEETINGS_MISSING_ROOM = Gauge("meetings_missing_room", "Upcoming in-person meetings WITHOUT a room")
MEETINGS_URGENT_MISSING_ROOM = Gauge(
    "meetings_urgent_missing_room", "Meetings without a room that start within the urgent window"
)
MEETINGS_MISSING_RSVP = Gauge("meetings_missing_rsvp", "Meetings with at least one attendee who has not responded")
ATTENDEES_PENDING = Gauge("attendees_pending_rsvp", "Total attendees who have not responded")
LAST_SUCCESS = Gauge("meeting_checker_last_success_timestamp_seconds", "Unix time of the last successful check")
CHECK_ERRORS = Counter("meeting_checker_errors_total", "Failed calendar checks")


def run_check(source, lookahead_days: int, urgent_hours: int) -> None:
    result = check_meetings(source.fetch(), lookahead_days, urgent_hours)
    MEETINGS_TOTAL.set(result.total)
    MEETINGS_WITH_ROOM.set(result.with_room)
    MEETINGS_ONLINE.set(result.online)
    MEETINGS_MISSING_ROOM.set(len(result.missing_room))
    MEETINGS_URGENT_MISSING_ROOM.set(len(result.urgent_missing_room))
    MEETINGS_MISSING_RSVP.set(len(result.missing_rsvp))
    ATTENDEES_PENDING.set(result.pending_attendees_total)
    LAST_SUCCESS.set_to_current_time()
    log.info(
        "total=%d with_room=%d online=%d missing_room=%d urgent=%d missing_rsvp=%d",
        result.total, result.with_room, result.online,
        len(result.missing_room), len(result.urgent_missing_room), len(result.missing_rsvp),
    )
    for m in result.urgent_missing_room:
        log.warning("URGENT no room: '%s' starts %s", m.subject, m.start.isoformat())


def main() -> None:
    data_file = os.getenv("DATA_FILE", "data/meetings.json")
    interval = int(os.getenv("CHECK_INTERVAL", "30"))
    lookahead = int(os.getenv("LOOKAHEAD_DAYS", "7"))
    urgent = int(os.getenv("URGENT_HOURS", "24"))
    port = int(os.getenv("METRICS_PORT", "8000"))

    source = FileSource(data_file)
    start_http_server(port)
    log.info("Serving metrics on :%d/metrics (interval=%ss)", port, interval)

    while True:
        try:
            run_check(source, lookahead, urgent)
        except Exception:  # keep the exporter alive; surface via metric + alert
            CHECK_ERRORS.inc()
            log.exception("Calendar check failed")
        time.sleep(interval)


if __name__ == "__main__":
    main()
