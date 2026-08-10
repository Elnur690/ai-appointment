from app.integrations.ai.provider import ToolDefinition, ToolParameter, ToolParameterType

def get_customer_tools() -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="check_availability",
            description="Check available time slots for a specific date and service.",
            parameters=[
                ToolParameter(name="service_id", type=ToolParameterType.STRING, description="The ID of the service.", required=True),
                ToolParameter(name="date", type=ToolParameterType.STRING, description="The date in YYYY-MM-DD format.", required=True),
                ToolParameter(name="staff_id", type=ToolParameterType.STRING, description="The ID of the staff member (optional).", required=False),
            ]
        ),
        ToolDefinition(
            name="get_services",
            description="List available services for the branch.",
            parameters=[]
        ),
        ToolDefinition(
            name="get_staff_for_service",
            description="List staff who can perform a specific service.",
            parameters=[
                ToolParameter(name="service_id", type=ToolParameterType.STRING, description="The ID of the service.", required=True),
            ]
        ),
        ToolDefinition(
            name="create_appointment",
            description="Book an appointment.",
            parameters=[
                ToolParameter(name="service_id", type=ToolParameterType.STRING, description="The ID of the service.", required=True),
                ToolParameter(name="staff_id", type=ToolParameterType.STRING, description="The ID of the staff member.", required=True),
                ToolParameter(name="date", type=ToolParameterType.STRING, description="The date in YYYY-MM-DD format.", required=True),
                ToolParameter(name="time", type=ToolParameterType.STRING, description="The time in HH:MM format.", required=True),
                ToolParameter(name="customer_name", type=ToolParameterType.STRING, description="The customer's name (optional).", required=False),
            ]
        ),
        ToolDefinition(
            name="reschedule_appointment",
            description="Reschedule an existing appointment.",
            parameters=[
                ToolParameter(name="appointment_id", type=ToolParameterType.STRING, description="The ID of the appointment.", required=True),
                ToolParameter(name="new_date", type=ToolParameterType.STRING, description="The new date in YYYY-MM-DD format.", required=True),
                ToolParameter(name="new_time", type=ToolParameterType.STRING, description="The new time in HH:MM format.", required=True),
                ToolParameter(name="new_staff_id", type=ToolParameterType.STRING, description="The new staff ID (optional).", required=False),
            ]
        ),
        ToolDefinition(
            name="cancel_appointment",
            description="Cancel an appointment.",
            parameters=[
                ToolParameter(name="appointment_id", type=ToolParameterType.STRING, description="The ID of the appointment.", required=True),
                ToolParameter(name="reason", type=ToolParameterType.STRING, description="The reason for cancellation (optional).", required=False),
            ]
        ),
        ToolDefinition(
            name="get_my_appointments",
            description="Get the customer's upcoming appointments.",
            parameters=[]
        ),
        ToolDefinition(
            name="get_next_upcoming_appointment",
            description="Get the customer's next upcoming appointment details (date, time, service, staff).",
            parameters=[]
        ),
        ToolDefinition(
            name="get_past_visit_history",
            description="Get the customer's past visit and service history.",
            parameters=[]
        ),
        ToolDefinition(
            name="request_human_agent",
            description="Request handoff to a human staff member.",
            parameters=[
                ToolParameter(name="reason", type=ToolParameterType.STRING, description="Reason for requesting human assistance.", required=False),
            ]
        ),
    ]

