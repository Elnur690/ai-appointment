import asyncio
import logging
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.models.business import Business
from app.models.saas import Plan
from app.services.business_advisor_service import BusinessAdvisorService

logger = logging.getLogger(__name__)


@celery_app.task(name="run_weekly_growth_advisor")
def run_weekly_growth_advisor():
    """Celery Beat weekly job running every Monday morning to send executive AI growth reports to Business Owners."""
    asyncio.run(_async_run_weekly_growth_advisor())


async def _async_run_weekly_growth_advisor():
    advisor = BusinessAdvisorService()
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Business)
            .join(Plan, Business.plan_id == Plan.id)
            .where(Business.is_active.is_(True), Plan.allows_growth_advisor.is_(True))
        )
        rows = (await session.execute(stmt)).scalars().all()
        for biz in rows:
            report = advisor.generate_weekly_report(business_id=str(biz.id), business_name=biz.name)
            logger.info(
                f"[WEEKLY AI GROWTH ADVISOR] Dispatched growth insights to '{report.business_name}': {report.recommended_action}"
            )
    await engine.dispose()
