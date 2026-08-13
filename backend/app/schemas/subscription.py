from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    plan_id: UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    ai_messages_used: int

class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    price: float
    max_branches: int
    max_whatsapp_numbers: int
    ai_message_quota: int
    allows_branch_level_ai_tone: bool = False
    allows_voice_messages: bool = False
    allows_dynamic_pricing: bool = False
    allows_winback_campaigns: bool = False
    allows_discovery: bool = False
    allows_online_payments: bool = False
    allows_gcal_sync: bool = False
    allows_apple_cal_sync: bool = False
    allows_custom_domain: bool = False
    allows_no_show_deposits: bool = False
    allows_emergency_reassignment: bool = False
    allows_omnichannel_messaging: bool = False
    allows_growth_advisor: bool = False
    allows_geo_routing: bool = False
    allows_shift_management: bool = False
    features: Optional[Dict[str, Any]] = None
    is_active: bool

class PlanCreate(BaseModel):
    name: str
    price: float
    max_branches: int
    max_whatsapp_numbers: int
    ai_message_quota: int
    allows_branch_level_ai_tone: Optional[bool] = False
    allows_voice_messages: Optional[bool] = False
    allows_dynamic_pricing: Optional[bool] = False
    allows_winback_campaigns: Optional[bool] = False
    allows_discovery: Optional[bool] = False
    allows_online_payments: Optional[bool] = False
    allows_gcal_sync: Optional[bool] = False
    allows_apple_cal_sync: Optional[bool] = False
    allows_custom_domain: Optional[bool] = False
    allows_no_show_deposits: Optional[bool] = False
    allows_emergency_reassignment: Optional[bool] = False
    allows_omnichannel_messaging: Optional[bool] = False
    allows_growth_advisor: Optional[bool] = False
    allows_geo_routing: Optional[bool] = False
    allows_shift_management: Optional[bool] = False
    features: Optional[Dict[str, Any]] = None

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    max_branches: Optional[int] = None
    max_whatsapp_numbers: Optional[int] = None
    ai_message_quota: Optional[int] = None
    allows_branch_level_ai_tone: Optional[bool] = None
    allows_voice_messages: Optional[bool] = None
    allows_dynamic_pricing: Optional[bool] = None
    allows_winback_campaigns: Optional[bool] = None
    allows_discovery: Optional[bool] = None
    allows_online_payments: Optional[bool] = None
    allows_gcal_sync: Optional[bool] = None
    allows_apple_cal_sync: Optional[bool] = None
    allows_custom_domain: Optional[bool] = None
    allows_no_show_deposits: Optional[bool] = None
    allows_emergency_reassignment: Optional[bool] = None
    allows_omnichannel_messaging: Optional[bool] = None
    allows_growth_advisor: Optional[bool] = None
    allows_geo_routing: Optional[bool] = None
    allows_shift_management: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None



