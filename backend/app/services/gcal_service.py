import logging
from datetime import datetime
from uuid import UUID
import httpx

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Manages 2-way Google Calendar synchronization for staff members."""
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"

    async def sync_appointment_to_gcal(
        self,
        staff_access_token: str,
        calendar_id: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str | None = None,
    ) -> str | None:
        """Push appointment event to Google Calendar."""
        headers = {
            "Authorization": f"Bearer {staff_access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "summary": summary,
            "description": description or "",
            "start": {"dateTime": start_time.isoformat()},
            "end": {"dateTime": end_time.isoformat()},
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{self.BASE_URL}/calendars/{calendar_id}/events", json=payload, headers=headers)
                data = resp.json()
                return data.get("id")
            except Exception as e:
                logger.error(f"Google Calendar sync error: {e}")
                return None

    async def get_busy_slots(
        self,
        staff_access_token: str,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict]:
        """Fetch staff Google Calendar busy slots to block double-booking."""
        headers = {
            "Authorization": f"Bearer {staff_access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "timeMin": start_time.isoformat(),
            "timeMax": end_time.isoformat(),
            "items": [{"id": calendar_id}],
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{self.BASE_URL}/freeBusy", json=payload, headers=headers)
                data = resp.json()
                calendars = data.get("calendars", {})
                return calendars.get(calendar_id, {}).get("busy", [])
            except Exception as e:
                logger.error(f"Google Calendar freebusy check error: {e}")
                return []
