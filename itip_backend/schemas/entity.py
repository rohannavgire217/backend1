from datetime import datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime


class ClassificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    model_version: str
    classified_at: datetime
