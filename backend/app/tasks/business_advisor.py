import logging
from app.tasks.celery_app import celery_app
from app.services.business_advisor_service import BusinessAdvisorService

logger = logging.getLogger(__name__)

@celery_app.task(name="run_weekly_growth_advisor")
def run_weekly_growth_advisor():
    """Celery Beat weekly job running every Monday morning to send executive AI growth reports to Business Owners."""
    advisor = BusinessAdvisorService()
    report = advisor.generate_weekly_report(business_id="b1", business_name="Beauty Studio Baku")
    logger.info(f"[WEEKLY AI GROWTH ADVISOR] Dispatched growth insights to '{report.business_name}': {report.recommended_action}")
