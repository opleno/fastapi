from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime


# Pydentic models (schemas)

# Users

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


# Posts

class PostBase(BaseModel):
    title: str = ""
    content: str = ""
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True


class PostOut(PostBase):
    votes: int
    Post: PostResponse

    class Config:
        orm_mode = True


# Auth


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
