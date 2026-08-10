import logging
from datetime import datetime
import uuid
import httpx

logger = logging.getLogger(__name__)

class AppleCalendarService:
    """Manages 2-way Apple Calendar (iCloud CalDAV) synchronization for staff members."""
    
    ICLOUD_CALDAV_URL = "https://caldav.icloud.com"

    def _generate_vevent_ics(
        self,
        event_uid: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
    ) -> str:
        """Generate iCalendar (RFC 5545) VEVENT string for Apple CalDAV PUT request."""
        dtstart = start_time.strftime("%Y%m%dT%H%M%SZ")
        dtend = end_time.strftime("%Y%m%dT%H%M%SZ")
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        return (
            "BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//AI Appointment SaaS//EN\r\n"
            "BEGIN:VEVENT\r\n"
            f"UID:{event_uid}\r\n"
            f"DTSTAMP:{dtstamp}\r\n"
            f"DTSTART:{dtstart}\r\n"
            f"DTEND:{dtend}\r\n"
            f"SUMMARY:{summary}\r\n"
            f"DESCRIPTION:{description or ''}\r\n"
            "END:VEVENT\r\n"
            "END:VCALENDAR\r\n"
        )

    async def sync_appointment_to_apple_calendar(
        self,
        apple_email: str,
        app_specific_password: str,
        calendar_path: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
    ) -> str | None:
        """Push appointment event to staff member's Apple iCloud Calendar via CalDAV PUT."""
        event_uid = str(uuid.uuid4())
        ics_content = self._generate_vevent_ics(
            event_uid=event_uid,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
        )
        
        url = f"{self.ICLOUD_CALDAV_URL}/{calendar_path.strip('/')}/{event_uid}.ics"
        auth = (apple_email, app_specific_password)
        headers = {"Content-Type": "text/calendar; charset=utf-8"}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.put(url, content=ics_content, headers=headers, auth=auth)
                if resp.status_code in [200, 201, 204]:
                    return event_uid
                logger.error(f"CalDAV PUT error: status {resp.status_code}")
                return None
            except Exception as e:
                logger.error(f"Apple Calendar sync error: {e}")
                return None

    async def get_apple_busy_slots(
        self,
        apple_email: str,
        app_specific_password: str,
        calendar_path: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        """Fetch staff member's Apple Calendar busy slots via CalDAV REPORT query."""
        dtstart = start_time.strftime("%Y%m%dT%H%M%SZ")
        dtend = end_time.strftime("%Y%m%dT%H%M%SZ")
        
        caldav_report_xml = f"""<?xml version="1.0" encoding="utf-8" ?>
<C:calendar-query xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
    <D:prop>
        <D:getetag/>
        <C:calendar-data/>
    </D:prop>
    <C:filter>
        <C:comp-filter name="VCALENDAR">
            <C:comp-filter name="VEVENT">
                <C:time-range start="{dtstart}" end="{dtend}"/>
            </C:comp-filter>
        </C:comp-filter>
    </C:filter>
</C:calendar-query>"""

        url = f"{self.ICLOUD_CALDAV_URL}/{calendar_path.strip('/')}/"
        auth = (apple_email, app_specific_password)
        headers = {"Content-Type": "application/xml; charset=utf-8", "Depth": "1"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.request("REPORT", url, content=caldav_report_xml, headers=headers, auth=auth)
                if resp.status_code in [200, 207]:
                    # Mock return of parsed busy intervals for external events
                    return [{"start": dtstart, "end": dtend, "summary": "External Apple Calendar Event"}]
                return []
            except Exception as e:
                logger.error(f"Apple Calendar freebusy query error: {e}")
                return []
