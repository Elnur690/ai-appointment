from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.integrations.ai.provider import ToolCall

class ToolExecutor:
    """Executes AI tool calls by delegating to the service layer."""
    
    def __init__(self, db: AsyncSession, branch_id: UUID, business_id: UUID, customer_id: UUID | None = None):
        self.db = db
        self.branch_id = branch_id
        self.business_id = business_id
        self.customer_id = customer_id
    
    async def execute(self, tool_call: ToolCall) -> dict:
        """Execute a single tool call and return the result as a dict."""
        handlers = {
            'check_availability': self._check_availability,
            'get_services': self._get_services,
            'get_staff_for_service': self._get_staff_for_service,
            'create_appointment': self._create_appointment,
            'reschedule_appointment': self._reschedule_appointment,
            'cancel_appointment': self._cancel_appointment,
            'get_my_appointments': self._get_my_appointments,
            'get_next_upcoming_appointment': self._get_next_upcoming_appointment,
            'get_past_visit_history': self._get_past_visit_history,
            'request_human_agent': self._request_human_agent,
        }

    async def _get_next_upcoming_appointment(self) -> dict:
        return {
            "appointment": {
                "id": "appt-123",
                "service_name": "Haircut & Styling",
                "date": "Tomorrow",
                "time": "10:00 AM",
                "staff_name": "Dr. Alex",
                "status": "confirmed"
            }
        }

    async def _get_past_visit_history(self) -> dict:
        return {
            "history": [
                {"date": "2026-07-14", "service": "Haircut & Styling", "price": "30 AZN", "staff": "Dr. Alex"},
                {"date": "2026-06-10", "service": "Beard Trim", "price": "15 AZN", "staff": "Elvin A."}
            ]
        }

        
        handler = handlers.get(tool_call.name)
        if not handler:
            return {'error': f'Unknown tool: {tool_call.name}'}
            
        try:
            return await handler(**tool_call.arguments)
        except Exception as e:
            return {'error': str(e)}

    # TODO: Wire these up to actual service layer implementations.
    # Currently returning mock data to allow conversation handler testing.

    async def _check_availability(self, service_id: str, date: str, staff_id: str | None = None) -> dict:
        return {
            "available_slots": [
                {"time": "10:00", "staff_id": "staff-1", "staff_name": "Alice"},
                {"time": "14:00", "staff_id": "staff-2", "staff_name": "Bob"}
            ]
        }

    async def _get_services(self) -> dict:
        return {
            "services": [
                {"id": "service-1", "name": "Haircut", "duration": 30, "price": "$30"},
                {"id": "service-2", "name": "Coloring", "duration": 120, "price": "$100"}
            ]
        }

    async def _get_staff_for_service(self, service_id: str) -> dict:
        return {
            "staff": [
                {"id": "staff-1", "name": "Alice"},
                {"id": "staff-2", "name": "Bob"}
            ]
        }

    async def _create_appointment(self, service_id: str, staff_id: str, date: str, time: str, customer_name: str | None = None) -> dict:
        return {
            "status": "success",
            "appointment": {
                "id": "appt-123",
                "service_id": service_id,
                "staff_id": staff_id,
                "date": date,
                "time": time,
                "status": "confirmed"
            }
        }

    async def _reschedule_appointment(self, appointment_id: str, new_date: str, new_time: str, new_staff_id: str | None = None) -> dict:
        return {
            "status": "success",
            "appointment": {
                "id": appointment_id,
                "date": new_date,
                "time": new_time,
                "status": "rescheduled"
            }
        }

    async def _cancel_appointment(self, appointment_id: str, reason: str | None = None) -> dict:
        return {
            "status": "success",
            "message": "Appointment cancelled successfully."
        }

    async def _get_my_appointments(self) -> dict:
        return {
            "appointments": [
                {
                    "id": "appt-123",
                    "service_name": "Haircut",
                    "date": "2026-08-15",
                    "time": "10:00",
                    "staff_name": "Alice"
                }
            ]
        }

    async def _request_human_agent(self, reason: str | None = None) -> dict:
        return {
            "status": "success",
            "message": "Human agent requested. Handoff initiated."
        }
