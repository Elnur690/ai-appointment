from datetime import datetime, date as date_type, time as time_type, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.provider import ToolCall
from app.models.appointment import Appointment, AppointmentStatus, AppointmentSource
from app.models.business import Business, Branch
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.saas import Plan
from app.models.service import Service
from app.models.staff import Staff, StaffService
from app.services.no_show_protection_service import NoShowProtectionService


class ToolExecutor:
    """Executes AI tool calls directly against PostgreSQL and the service layer."""

    def __init__(self, db: AsyncSession, branch_id: UUID, business_id: UUID, customer_id: UUID | None = None):
        self.db = db
        self.branch_id = branch_id
        self.business_id = business_id
        self.customer_id = customer_id

    async def execute(self, tool_call: ToolCall) -> dict:
        """Execute a single tool call and return the result as a dict."""
        handlers = {
            "check_availability": self._check_availability,
            "get_services": self._get_services,
            "get_staff_for_service": self._get_staff_for_service,
            "create_appointment": self._create_appointment,
            "reschedule_appointment": self._reschedule_appointment,
            "cancel_appointment": self._cancel_appointment,
            "get_my_appointments": self._get_my_appointments,
            "get_next_upcoming_appointment": self._get_next_upcoming_appointment,
            "get_past_visit_history": self._get_past_visit_history,
            "request_human_agent": self._request_human_agent,
        }
        handler = handlers.get(tool_call.name)
        if not handler:
            return {"error": f"Unknown tool: {tool_call.name}"}

        try:
            return await handler(**tool_call.arguments)
        except Exception as e:
            return {"error": str(e)}

    async def _get_services(self) -> dict:
        rows = (
            await self.db.execute(
                select(Service).where(
                    Service.business_id == self.business_id,
                    Service.is_active.is_(True),
                )
            )
        ).scalars().all()
        return {
            "services": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "duration_minutes": s.duration_minutes,
                    "price": f"{float(s.price):.2f} {s.currency}",
                }
                for s in rows
            ]
        }

    async def _get_staff_for_service(self, service_id: str) -> dict:
        try:
            svc_uuid = UUID(str(service_id))
            linked_staff = (
                await self.db.execute(
                    select(Staff)
                    .join(StaffService, StaffService.staff_id == Staff.id)
                    .where(
                        Staff.business_id == self.business_id,
                        Staff.is_active.is_(True),
                        StaffService.service_id == svc_uuid,
                    )
                )
            ).scalars().all()
        except ValueError:
            linked_staff = []

        if not linked_staff:
            linked_staff = (
                await self.db.execute(
                    select(Staff).where(
                        Staff.business_id == self.business_id,
                        Staff.is_active.is_(True),
                    )
                )
            ).scalars().all()

        return {
            "staff": [
                {"id": str(st.id), "name": st.name, "role": st.role}
                for st in linked_staff
            ]
        }

    async def _get_branch(self) -> Branch | None:
        if not self.branch_id:
            return None
        return (
            await self.db.execute(select(Branch).where(Branch.id == self.branch_id))
        ).scalar_one_or_none()

    async def _get_branch_tz(self, branch: Branch | None = None) -> ZoneInfo:
        br = branch or await self._get_branch()
        tz_name = br.timezone if br and br.timezone else "Asia/Baku"
        try:
            return ZoneInfo(tz_name)
        except Exception:
            return ZoneInfo("Asia/Baku")

    async def _check_availability(self, service_id: str, date: str, staff_id: str | None = None) -> dict:
        target_date = date_type.fromisoformat(date)
        duration_minutes = 30
        try:
            svc = (
                await self.db.execute(
                    select(Service).where(
                        Service.id == UUID(str(service_id)),
                        Service.business_id == self.business_id,
                    )
                )
            ).scalar_one_or_none()
            if svc:
                duration_minutes = svc.duration_minutes
        except ValueError:
            pass

        branch = await self._get_branch()
        branch_tz = await self._get_branch_tz(branch)

        # Determine local working hours for the target weekday (fallback 09:00-20:00)
        start_t = time_type(9, 0)
        end_t = time_type(20, 0)
        if branch and branch.working_hours:
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            day_cfg = branch.working_hours.get(days[target_date.weekday()])
            if isinstance(day_cfg, dict) and day_cfg.get("start") and day_cfg.get("end"):
                sh, sm = map(int, str(day_cfg["start"]).split(":")[:2])
                eh, em = map(int, str(day_cfg["end"]).split(":")[:2])
                start_t, end_t = time_type(sh, sm), time_type(eh, em)
            elif isinstance(day_cfg, str) and "-" in day_cfg:
                s_part, e_part = day_cfg.split("-", 1)
                sh, sm = map(int, s_part.strip().split(":")[:2])
                eh, em = map(int, e_part.strip().split(":")[:2])
                start_t, end_t = time_type(sh, sm), time_type(eh, em)

        staff_stmt = select(Staff).where(
            Staff.business_id == self.business_id,
            Staff.is_active.is_(True),
        )
        if self.branch_id:
            staff_stmt = staff_stmt.where(Staff.branch_id == self.branch_id)
        if staff_id:
            try:
                staff_stmt = staff_stmt.where(Staff.id == UUID(str(staff_id)))
            except ValueError:
                pass
        staff_list = (await self.db.execute(staff_stmt)).scalars().all()

        day_start_local = datetime.combine(target_date, time_type(0, 0), tzinfo=branch_tz)
        day_end_local = day_start_local + timedelta(days=1)
        day_start_utc = day_start_local.astimezone(timezone.utc)
        day_end_utc = day_end_local.astimezone(timezone.utc)

        booked_rows = (
            await self.db.execute(
                select(Appointment).where(
                    Appointment.business_id == self.business_id,
                    Appointment.start_time < day_end_utc,
                    Appointment.end_time > day_start_utc,
                    Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.no_show]),
                )
            )
        ).scalars().all()

        work_start_dt = datetime.combine(target_date, start_t, tzinfo=branch_tz)
        work_end_dt = datetime.combine(target_date, end_t, tzinfo=branch_tz)

        slots = []
        for st in staff_list:
            st_booked = [b for b in booked_rows if b.staff_id == st.id]
            cursor = work_start_dt
            while cursor + timedelta(minutes=duration_minutes) <= work_end_dt:
                slot_start_utc = cursor.astimezone(timezone.utc)
                slot_end_utc = (cursor + timedelta(minutes=duration_minutes)).astimezone(timezone.utc)
                overlaps = any(
                    (b.start_time if b.start_time.tzinfo else b.start_time.replace(tzinfo=timezone.utc)) < slot_end_utc
                    and (b.end_time if b.end_time.tzinfo else b.end_time.replace(tzinfo=timezone.utc)) > slot_start_utc
                    for b in st_booked
                )
                if not overlaps:
                    slots.append({
                        "time": cursor.strftime("%H:%M"),
                        "staff_id": str(st.id),
                        "staff_name": st.name,
                    })
                cursor += timedelta(minutes=30)
        return {"available_slots": slots[:20]}

    async def _create_appointment(
        self,
        service_id: str,
        staff_id: str,
        date: str,
        time: str,
        customer_name: str | None = None,
    ) -> dict:
        if not self.customer_id:
            return {"error": "Customer context is required to create an appointment."}

        svc = (
            await self.db.execute(
                select(Service).where(
                    Service.id == UUID(str(service_id)),
                    Service.business_id == self.business_id,
                )
            )
        ).scalar_one_or_none()
        if not svc:
            return {"error": "Service not found."}

        st = (
            await self.db.execute(
                select(Staff).where(
                    Staff.id == UUID(str(staff_id)),
                    Staff.business_id == self.business_id,
                )
            )
        ).scalar_one_or_none()
        if not st:
            return {"error": "Staff member not found."}

        branch_tz = await self._get_branch_tz()
        target_date = date_type.fromisoformat(date)
        hh, mm = map(int, time.split(":")[:2])
        start_dt = datetime.combine(target_date, time_type(hh, mm), tzinfo=branch_tz).astimezone(timezone.utc)
        end_dt = start_dt + timedelta(minutes=svc.duration_minutes)

        conflict = (
            await self.db.execute(
                select(Appointment.id).where(
                    Appointment.business_id == self.business_id,
                    Appointment.staff_id == st.id,
                    Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.no_show]),
                    Appointment.start_time < end_dt,
                    Appointment.end_time > start_dt,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if conflict:
            return {"error": "Selected time slot is already booked for this staff member."}

        # Evaluate real customer history & business Beh (deposit) rules
        no_show_count = (
            await self.db.execute(
                select(func.count(Appointment.id)).where(
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                    Appointment.status == AppointmentStatus.no_show,
                )
            )
        ).scalar() or 0

        completed_count = (
            await self.db.execute(
                select(func.count(Appointment.id)).where(
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                    Appointment.status == AppointmentStatus.completed,
                )
            )
        ).scalar() or 0

        business = (
            await self.db.execute(select(Business).where(Business.id == self.business_id))
        ).scalar_one_or_none()

        is_deposit_enabled = False
        if business:
            plan = None
            if business.plan_id:
                plan = (await self.db.execute(select(Plan).where(Plan.id == business.plan_id))).scalar_one_or_none()
            plan_allows = bool(plan.allows_no_show_deposits) if plan else False
            biz_settings = business.default_ai_tone_config or {}
            overrides = business.trial_features_override or {}
            if "allows_no_show_deposits" in overrides:
                is_deposit_enabled = bool(overrides["allows_no_show_deposits"])
            else:
                is_deposit_enabled = plan_allows
        else:
            biz_settings = {}

        deposit_req = NoShowProtectionService().evaluate_booking_risk(
            customer_no_shows=int(no_show_count),
            service_price=Decimal(str(svc.price)),
            is_deposit_feature_enabled=is_deposit_enabled,
            customer_completed_visits=int(completed_count),
            service_id=str(svc.id),
            business_settings=biz_settings,
        )

        appt = Appointment(
            branch_id=self.branch_id,
            business_id=self.business_id,
            staff_id=st.id,
            customer_id=self.customer_id,
            service_id=svc.id,
            start_time=start_dt,
            end_time=end_dt,
            status=AppointmentStatus.pending if deposit_req.is_deposit_required else AppointmentStatus.confirmed,
            source=AppointmentSource.ai_chat,
            notes=f"Customer: {customer_name}" if customer_name else None,
        )
        self.db.add(appt)
        await self.db.flush()

        checkout_url: str | None = None
        if deposit_req.is_deposit_required:
            from app.core.config import settings
            from app.core.security import decrypt_credentials_dict
            from app.models.payment import PaymentGatewayConfig
            from app.integrations.payments.payriff import PayriffAdapter
            from app.integrations.payments.epoint import EpointAdapter

            allowed_providers = (
                list(getattr(plan, "allowed_payment_providers", None) or ["cash", "payriff", "epoint"])
                if plan
                else ["cash", "payriff", "epoint"]
            )
            gw_configs = (
                await self.db.execute(
                    select(PaymentGatewayConfig).where(
                        PaymentGatewayConfig.business_id == self.business_id,
                        PaymentGatewayConfig.is_active.is_(True),
                        PaymentGatewayConfig.provider.in_(["payriff", "epoint"]),
                    )
                )
            ).scalars().all()
            chosen_cfg = next(
                (g for g in gw_configs if g.provider in allowed_providers),
                None,
            )

            dep_method = (
                PaymentMethod.payriff
                if (not chosen_cfg or chosen_cfg.provider == "payriff")
                else PaymentMethod.epoint
            )
            dep_payment = Payment(
                business_id=self.business_id,
                appointment_id=appt.id,
                amount=float(deposit_req.deposit_amount),
                currency=svc.currency or "AZN",
                method=dep_method,
                status=PaymentStatus.pending,
                notes=f"Beh / Deposit ({svc.name})",
            )
            self.db.add(dep_payment)
            await self.db.flush()

            if chosen_cfg:
                creds = decrypt_credentials_dict(chosen_cfg.merchant_credentials)
                try:
                    if chosen_cfg.provider == "payriff" and creds.get("merchant_id") and creds.get("secret_key"):
                        link_res = await PayriffAdapter().create_payment_link(
                            payment_id=dep_payment.id,
                            amount=deposit_req.deposit_amount,
                            currency=svc.currency or "AZN",
                            description=f"Beh / Deposit - {svc.name}",
                            merchant_config=creds,
                            return_url=f"https://{settings.PLATFORM_DOMAIN}",
                        )
                        dep_payment.gateway_transaction_id = link_res.transaction_id
                        checkout_url = link_res.payment_url
                    elif chosen_cfg.provider == "epoint" and creds.get("public_key") and creds.get("private_key"):
                        link_res = await EpointAdapter().create_payment_link(
                            payment_id=dep_payment.id,
                            amount=deposit_req.deposit_amount,
                            currency=svc.currency or "AZN",
                            description=f"Beh / Deposit - {svc.name}",
                            merchant_config=creds,
                            return_url=f"https://{settings.PLATFORM_DOMAIN}",
                        )
                        dep_payment.gateway_transaction_id = link_res.transaction_id
                        checkout_url = link_res.payment_url
                except Exception:
                    checkout_url = None

        await self.db.commit()
        await self.db.refresh(appt)

        return {
            "status": "success",
            "appointment": {
                "id": str(appt.id),
                "service": svc.name,
                "staff": st.name,
                "date": date,
                "time": time,
                "status": appt.status.value,
                "deposit_required": deposit_req.is_deposit_required,
                "deposit_amount": float(deposit_req.deposit_amount) if deposit_req.is_deposit_required else 0.0,
                "deposit_reason": deposit_req.reason,
                "checkout_url": checkout_url,
            },
        }

    async def _reschedule_appointment(
        self,
        appointment_id: str,
        new_date: str,
        new_time: str,
        new_staff_id: str | None = None,
    ) -> dict:
        if not self.customer_id:
            return {"error": "Customer context is required to reschedule an appointment."}

        appt = (
            await self.db.execute(
                select(Appointment).where(
                    Appointment.id == UUID(str(appointment_id)),
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                )
            )
        ).scalar_one_or_none()
        if not appt:
            return {"error": "Appointment not found."}

        branch_tz = await self._get_branch_tz()
        duration = appt.end_time - appt.start_time
        target_date = date_type.fromisoformat(new_date)
        hh, mm = map(int, new_time.split(":")[:2])
        new_start = datetime.combine(target_date, time_type(hh, mm), tzinfo=branch_tz).astimezone(timezone.utc)
        new_end = new_start + duration
        target_staff_id = UUID(str(new_staff_id)) if new_staff_id else appt.staff_id

        conflict = (
            await self.db.execute(
                select(Appointment.id).where(
                    Appointment.business_id == self.business_id,
                    Appointment.staff_id == target_staff_id,
                    Appointment.id != appt.id,
                    Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.no_show]),
                    Appointment.start_time < new_end,
                    Appointment.end_time > new_start,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if conflict:
            return {"error": "Selected time slot is already booked for this staff member."}

        appt.start_time = new_start
        appt.end_time = new_end
        appt.staff_id = target_staff_id
        await self.db.commit()

        return {
            "status": "success",
            "appointment": {
                "id": str(appt.id),
                "date": new_date,
                "time": new_time,
                "status": appt.status.value,
            },
        }

    async def _cancel_appointment(self, appointment_id: str, reason: str | None = None) -> dict:
        if not self.customer_id:
            return {"error": "Customer context is required to cancel an appointment."}

        appt = (
            await self.db.execute(
                select(Appointment).where(
                    Appointment.id == UUID(str(appointment_id)),
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                )
            )
        ).scalar_one_or_none()
        if not appt:
            return {"error": "Appointment not found."}

        appt.status = AppointmentStatus.cancelled
        if reason:
            appt.notes = f"{appt.notes + ' | ' if appt.notes else ''}Cancelled: {reason}"
        await self.db.commit()
        return {"status": "success", "message": "Appointment cancelled successfully."}

    async def _get_my_appointments(self) -> dict:
        if not self.customer_id:
            return {"appointments": []}
        rows = (
            await self.db.execute(
                select(Appointment, Service, Staff)
                .join(Service, Service.id == Appointment.service_id)
                .join(Staff, Staff.id == Appointment.staff_id)
                .where(
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                    Appointment.start_time >= datetime.now(timezone.utc),
                    Appointment.status.notin_([AppointmentStatus.cancelled]),
                )
                .order_by(Appointment.start_time.asc())
            )
        ).all()
        return {
            "appointments": [
                {
                    "id": str(a.id),
                    "service_name": svc.name,
                    "date": a.start_time.strftime("%Y-%m-%d"),
                    "time": a.start_time.strftime("%H:%M"),
                    "staff_name": st.name,
                    "status": a.status.value,
                }
                for a, svc, st in rows
            ]
        }

    async def _get_next_upcoming_appointment(self) -> dict:
        res = await self._get_my_appointments()
        appts = res.get("appointments", [])
        return {"appointment": appts[0] if appts else None}

    async def _get_past_visit_history(self) -> dict:
        if not self.customer_id:
            return {"history": []}
        rows = (
            await self.db.execute(
                select(Appointment, Service, Staff)
                .join(Service, Service.id == Appointment.service_id)
                .join(Staff, Staff.id == Appointment.staff_id)
                .where(
                    Appointment.business_id == self.business_id,
                    Appointment.customer_id == self.customer_id,
                    Appointment.start_time < datetime.now(timezone.utc),
                )
                .order_by(Appointment.start_time.desc())
                .limit(10)
            )
        ).all()
        return {
            "history": [
                {
                    "date": a.start_time.strftime("%Y-%m-%d"),
                    "service": svc.name,
                    "price": f"{float(svc.price):.2f} {svc.currency}",
                    "staff": st.name,
                    "status": a.status.value,
                }
                for a, svc, st in rows
            ]
        }

    async def _request_human_agent(self, reason: str | None = None) -> dict:
        return {
            "status": "success",
            "message": "Human agent requested. Handoff initiated.",
            "reason": reason,
        }
