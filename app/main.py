from fastapi import FastAPI
from app.router import user, post, auth
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
