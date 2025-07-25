from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime


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
