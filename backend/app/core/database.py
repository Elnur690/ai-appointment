import logging
from typing import AsyncGenerator
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database extensions, create all ORM tables, and seed initial SaaS Admin & Plans."""
    import app.models  # noqa: F401 - register all ORM models on Base.metadata
    from app.models.base import Base
    from app.models.saas import SaasOwner, Plan
    from app.core.security import hash_password

    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception as exc:
            logger.warning(f"pgvector extension check skipped or unavailable: {exc}")
        await conn.run_sync(Base.metadata.create_all)

    # Seed initial SaaS Owner & default plans if database is fresh
    try:
        async with AsyncSessionLocal() as session:
            existing_admin = (
                await session.execute(select(SaasOwner).where(SaasOwner.email == settings.SAAS_ADMIN_EMAIL))
            ).scalar_one_or_none()
            if not existing_admin:
                admin = SaasOwner(
                    email=settings.SAAS_ADMIN_EMAIL,
                    password_hash=hash_password(settings.SAAS_ADMIN_PASSWORD),
                    name="Randevu.vip Platform Owner",
                    is_active=True,
                )
                session.add(admin)

            existing_plans = (await session.execute(select(Plan))).scalars().all()
            if not existing_plans:
                session.add_all([
                    Plan(
                        name="Starter",
                        price=29.00,
                        max_branches=1,
                        max_whatsapp_numbers=1,
                        ai_message_quota=1000,
                        allowed_ai_providers=["gemini"],
                        features={"assigned_model": "gemini-3.5-flash"},
                        is_active=True,
                    ),
                    Plan(
                        name="Pro",
                        price=79.00,
                        max_branches=3,
                        max_whatsapp_numbers=3,
                        ai_message_quota=5000,
                        allows_voice_messages=True,
                        allows_dynamic_pricing=True,
                        allows_winback_campaigns=True,
                        allows_online_payments=True,
                        allows_gcal_sync=True,
                        allows_apple_cal_sync=True,
                        allows_no_show_deposits=True,
                        allows_loyalty_program=True,
                        allows_combo_packages=True,
                        allows_geo_routing=True,
                        allows_shift_management=True,
                        allows_cadence_engine=True,
                        allows_gift_vouchers=True,
                        allows_flash_drops=True,
                        allowed_ai_providers=["gemini", "claude"],
                        features={"assigned_model": "claude-3-7-sonnet"},
                        is_active=True,
                    ),
                    Plan(
                        name="Enterprise",
                        price=199.00,
                        max_branches=20,
                        max_whatsapp_numbers=20,
                        ai_message_quota=50000,
                        allows_branch_level_ai_tone=True,
                        allows_voice_messages=True,
                        allows_dynamic_pricing=True,
                        allows_winback_campaigns=True,
                        allows_discovery=True,
                        allows_online_payments=True,
                        allows_gcal_sync=True,
                        allows_apple_cal_sync=True,
                        allows_custom_domain=True,
                        allows_no_show_deposits=True,
                        allows_emergency_reassignment=True,
                        allows_omnichannel_messaging=True,
                        allows_growth_advisor=True,
                        allows_loyalty_program=True,
                        allows_combo_packages=True,
                        allows_group_bookings=True,
                        allows_product_upsells=True,
                        allows_geo_routing=True,
                        allows_shift_management=True,
                        allows_cadence_engine=True,
                        allows_gift_vouchers=True,
                        allows_flash_drops=True,
                        allowed_ai_providers=["gemini", "claude", "openai"],
                        features={"assigned_model": "gpt-4o"},
                        is_active=True,
                    ),
                ])
            await session.commit()
    except Exception as exc:
        logger.warning(f"Initial seed skipped or failed: {exc}")
