from fastapi import Depends, HTTPException, status
from . import database, models, schema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)

oatuh2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# create jwt token


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# verify token
def verify_access_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")  # type: ignore

        if id is None:
            raise credentials_exceptions
        token_data = schema.TokenData(id=str(id))

    except JWTError:
        raise credentials_exceptions

    return token_data


# get current user


def get_current_user(
    token: str = Depends(oatuh2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authentivate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exceptions)  # type: ignore

    user = db.query(models.User).filter(models.User.id == token.id).first()  # type: ignore

    return user
