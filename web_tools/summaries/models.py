from typing import List, Optional, Field
from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime
from enum import Enum


class SummaryData(BaseModel):
    title: str
    short_description: str
    authors: List[str]


class WebSummaryResponse(BaseModel):
    summary: str


class CreateWebSummaryRequest(BaseModel):
    text: str


class SourceTypeEnum(str, Enum):
    url = "url"
    file = "file"


# Author Schemas
class AuthorBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the author")


class AuthorCreate(AuthorBase):
    pass


class AuthorRead(AuthorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Summary Schemas
class SummaryBase(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the summary")
    short_description: str = Field(
        ..., max_length=500, description="Short description of the summary"
    )
    content: str = Field(..., description="Markdown formatted content of the summary")
    status: str = Field(
        "draft",
        max_length=50,
        description="Status of the summary (e.g., draft, published)",
    )
    is_deleted: bool = Field(
        False, description="Flag to indicate if the summary is deleted"
    )
    user_id: Optional[str] = Field(
        None, max_length=255, description="ID of the user who owns the summary"
    )


class SummaryCreate(SummaryBase):
    authors: List[str] = Field(..., description="List of author names")


class SummaryRead(SummaryBase):
    id: UUID
    authors: List[AuthorRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Source Schemas (Optional)
class SourceBase(BaseModel):
    url: Optional[HttpUrl] = Field(None, description="URL of the source")
    summary_id: UUID = Field(..., description="ID of the associated summary")


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
