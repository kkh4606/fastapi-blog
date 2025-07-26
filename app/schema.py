from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from typing import Optional


class User(BaseModel):
    email: EmailStr
    password: str


class UserCreate(User):
    pass


class Post(BaseModel):
    title: str
    content: str
    published: bool = False


class PostCreate(Post):
    pass


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool] = False


class PostOut(Post):
    id: int
    owner_id: int | None = None
    date_created: datetime

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    date_created: datetime

    posts: List[PostOut] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
