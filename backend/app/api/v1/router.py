from fastapi import APIRouter
from app.api.v1 import (
    auth, saas_admin, businesses, branches, staff, 
    services, appointments, customers, conversations, 
    payments, webhooks, knowledge, whatsapp_groups, waitlist
)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(saas_admin.router, prefix="/admin", tags=["SaaS Admin"])
api_v1_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_v1_router.include_router(branches.router, prefix="/branches", tags=["Branches"])
api_v1_router.include_router(staff.router, prefix="/staff", tags=["Staff"])
api_v1_router.include_router(services.router, prefix="/services", tags=["Services"])
api_v1_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_v1_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_v1_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_v1_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_v1_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_v1_router.include_router(whatsapp_groups.router, prefix="/whatsapp-groups", tags=["WhatsApp Groups"])
api_v1_router.include_router(waitlist.router, prefix="/waitlist", tags=["Waitlist"])


