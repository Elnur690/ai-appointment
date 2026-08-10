from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class KnowledgeEntryCreate(BaseModel):
    title: str
    question_context: str
    answer_content: str
    entry_type: Optional[str] = 'custom'
    branch_id: Optional[UUID] = None
    tags: Optional[List[str]] = None

class KnowledgeEntryUpdate(BaseModel):
    title: Optional[str] = None
    question_context: Optional[str] = None
    answer_content: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class KnowledgeEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    question_context: str
    answer_content: str
    entry_type: str
    status: str
    branch_id: Optional[UUID]
    ai_original_response: Optional[str]
    correction_notes: Optional[str]
    usage_count: int
    avg_relevance_score: Optional[float]
    created_at: datetime

class CorrectionCaptureRequest(BaseModel):
    conversation_id: UUID
    customer_question: str
    ai_wrong_response: str
    staff_correct_response: str
    correction_notes: Optional[str] = None
