from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class RegisterIn(LoginIn):
    full_name: str = ""


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str = ""


class GuideIn(BaseModel):
    query: str = Field(min_length=10, max_length=4000)
    location: str = "Sheffield"
