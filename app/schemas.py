from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


class URLCreateRequest(BaseModel):
    original_url: HttpUrl
    custom_code: Optional[str] = None

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not (3 <= len(v) <= 10):
            raise ValueError("custom_code must be 3-10 characters long")
        if not v.isalnum():
            raise ValueError("custom_code must be alphanumeric")
        return v


class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    clicks: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True
