"""Today's meetings from the local Outlook desktop app via COM automation.
Covers Teams meetings too, since Teams schedules through Outlook by default.
pip install pywin32
"""

from __future__ import annotations

from datetime import date, datetime, time as dt_time

import pythoncom
import win32com.client

from launcher.briefing.models import CalendarEvent


class OutlookCalendarProvider:
    def get_todays_events(self) -> list[CalendarEvent]:
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch(
                "Outlook.Application"
            ).GetNamespace("MAPI")

            calendar = outlook.GetDefaultFolder(9)  # olFolderCalendar
            items = calendar.Items
            items.IncludeRecurrences = True
            items.Sort("[Start]")

            today = date.today()
            restriction = today.strftime(
                "[Start] >= '%m/%d/%Y 00:00 AM' "
                "AND [Start] <= '%m/%d/%Y 11:59 PM'"
            )

            events = [
                CalendarEvent(
                    title=item.Subject,
                    start=_to_time(item.Start),
                )
                for item in items.Restrict(restriction)
            ]

            return sorted(events, key=lambda event: event.start)

        finally:
            pythoncom.CoUninitialize()


def _to_time(com_datetime) -> dt_time:
    return datetime(
        com_datetime.year,
        com_datetime.month,
        com_datetime.day,
        com_datetime.hour,
        com_datetime.minute,
    ).time()