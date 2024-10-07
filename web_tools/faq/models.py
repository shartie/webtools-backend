from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field, model_validator, EmailStr
from typing import Optional

# user request
class GetUserDetailsRequest(BaseModel):
    email: str

# faq request
class CreateFromUrlRequest(BaseModel):
    url: str

class UpdateFAQSectionRequest(BaseModel):
    visibility: bool

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True, extra='ignore')
    guid: UUID
    username: str
    email: EmailStr

class FAQItemResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True, extra='ignore')
    guid: UUID
    question: str
    answer: str
    order: int


class FAQSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    guid: UUID
    title: str
    description: str
    items: Optional[list[FAQItemResponse]] = None
    is_public: bool


# openai
class FAQItem(BaseModel):
    question: str
    answer: str
    order: int

class FAQSection(BaseModel):
    title: str
    description: str
    items: list[FAQItem]