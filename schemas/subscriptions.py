from pydantic import BaseModel, Field, PositiveFloat, field_validator
from typing import Optional
import pymorphy3
from datetime import datetime
import re


morph = pymorphy3.MorphAnalyzer()


class SubscriptionCreate(BaseModel):
    token: str = Field(..., description="The symbol of the" +
                       " cryptocurrency token",
                       pattern=r'^[A-Z]{3,5}$')
    threshold: PositiveFloat = Field(ge=0.1, le=100.0,
                                     description="The spread threshold" +
                                     " percentage for notifications")
    comment: Optional[str] = Field(None, description="An optional comment" +
                                   " about the subscription")

    @field_validator('comment')
    def validate_comment(cls, v):
        forbidden_words = ['spam', 'advertisement', 'clickbait']
        words = re.findall(r'\b\w+\b', v.lower())
        for word in words:
            parsed_word = morph.parse(word)[0].normal_form
            if parsed_word in forbidden_words:
                raise ValueError(f"The comment contains a forbidden word: '{word}'")


class SubscriptionResponse(BaseModel):
    id: int = Field(..., description="The unique identifier" +
                    " of the subscription")
    user_id: int = Field(..., description="The unique identifier" +
                         " of the user")
    created_at: datetime = Field(..., description="The timestamp" +
                                        " when the subscription was created")

    token: str
    threshold: PositiveFloat
    comment: Optional[str] = None

    @classmethod
    def check_threshold(cls, current_spread: float, threshold: float) -> bool:
        return current_spread >= threshold
