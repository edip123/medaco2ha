"""Turn interval values into hourly long-term statistics rows.

Kept free of Home Assistant imports so it can be unit tested on its own.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from .api import Interval


@dataclass(frozen=True)
class HourRow:
    """One hourly statistics row: energy in the hour and running total."""

    start: datetime
    state: float
    sum: float


def to_hourly_rows(
    intervals: Iterable[Interval],
    last_sum: float = 0.0,
    after: datetime | None = None,
) -> list[HourRow]:
    """Group intervals by UTC hour and accumulate a running sum.

    Only hours strictly after ``after`` (the start of the last imported
    hour) are returned, so repeated imports never double count.

    The newest hour is held back while it is incomplete (fewer than four
    15 minute slots), because importing it too low would never be fixed.
    Any other incomplete hour is imported with the values that exist: the
    first hour after a meter was installed usually starts mid-hour, and a
    gap in the middle must not stop the import of everything after it.
    """
    buckets: dict[datetime, list[float]] = {}
    for interval in intervals:
        hour = interval.start.astimezone(timezone.utc).replace(
            minute=0, second=0, microsecond=0
        )
        if after is not None and hour <= after:
            continue
        buckets.setdefault(hour, []).append(interval.kwh)

    hours = sorted(buckets)
    rows: list[HourRow] = []
    running = last_sum
    for hour in hours:
        values = buckets[hour]
        if hour == hours[-1] and len(values) not in (1, 4):
            # Partial trailing hour: wait until the remaining slots arrive.
            break
        energy = round(sum(values), 6)
        running = round(running + energy, 6)
        rows.append(HourRow(start=hour, state=energy, sum=running))
    return rows
