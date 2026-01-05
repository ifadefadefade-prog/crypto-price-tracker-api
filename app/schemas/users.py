from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator, model_validator
from typing import Optional
from datetime import datetime
import re


def validate_password(v: str) -> str:
    if not 8 <= len(v) <= 16:
        raise ValueError("Пароль должен содержать от 8 до 16 символов")
    if not re.search(r'[a-zA-Z]', v):
        raise ValueError("Пароль должен содержать хотя бы одну букву")
    if not re.search(r'\d', v):
        raise ValueError("Пароль должен содержать хотя бы одну цифру")
    if not re.search(r'[!?*$%.,()#@]', v):
        raise ValueError(
            "Пароль должен содержать хотя бы один спецсимвол: !?*$%.,()#@"
        )
    return v


class UserBase(BaseModel):
    username: str = Field(min_length=6, max_length=20,
                          pattern=r'^[a-zA-Z0-9_]+$')


class UserCreate(UserBase):
    email: EmailStr
    password: str

    @field_validator('password')
    def verify_password(cls, v: str):
        return validate_password(v)


class UserLogin(BaseModel):
    login: str
    password: str


class UserChangePassword(BaseModel):
    old_pass: str
    new_pass: str

    @field_validator('new_pass')
    def verify_password(cls, v: str):
        return validate_password(v)

    @model_validator(mode='after')
    def check_pass(self):
        if self.old_pass == self.new_pass:
            raise ValueError("Новый пароль не должен совпадать со старым")
        return self


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime] = Field(default=None)

    model_config = {
        "from_attributes": True
    }
