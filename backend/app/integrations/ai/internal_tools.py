from app.integrations.ai.provider import ToolDefinition, ToolParameter, ToolParameterType

def get_internal_group_tools() -> list[ToolDefinition]:
    """Read-only tool definitions for internal staff/owner WhatsApp groups."""
    return [
        ToolDefinition(
            name="get_today_schedule",
            description="View today's appointment schedule for the branch or a specific staff member.",
            parameters=[
                ToolParameter(
                    name="staff_id",
                    type=ToolParameterType.STRING,
                    description="Optional staff ID or name to filter schedule for a specific person.",
                    required=False,
                )
            ],
        ),
        ToolDefinition(
            name="get_upcoming_appointments",
            description="View upcoming appointment bookings for the branch for the next N days.",
            parameters=[
                ToolParameter(
                    name="days",
                    type=ToolParameterType.INTEGER,
                    description="Number of days to look ahead (default 3).",
                    required=False,
                ),
                ToolParameter(
                    name="staff_id",
                    type=ToolParameterType.STRING,
                    description="Optional staff ID to filter by.",
                    required=False,
                ),
            ],
        ),
        ToolDefinition(
            name="get_daily_revenue_summary",
            description="View total revenue and breakdown (cash vs online) for today or a specific date.",
            parameters=[
                ToolParameter(
                    name="date",
                    type=ToolParameterType.STRING,
                    description="Target date in YYYY-MM-DD format (defaults to today).",
                    required=False,
                )
            ],
        ),
        ToolDefinition(
            name="get_no_shows",
            description="List recent no-show appointments for follow-up.",
            parameters=[
                ToolParameter(
                    name="days",
                    type=ToolParameterType.INTEGER,
                    description="Number of past days to check for no-shows (default 7).",
                    required=False,
                )
            ],
        ),
        ToolDefinition(
            name="get_branch_summary",
            description="Overview of branch activity, active staff, and booking status.",
            parameters=[
                ToolParameter(
                    name="branch_id",
                    type=ToolParameterType.STRING,
                    description="Optional branch ID.",
                    required=False,
                )
            ],
        ),
    ]
