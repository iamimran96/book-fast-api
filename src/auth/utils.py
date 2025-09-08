from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
import uuid
import logging
from src.config import Config

passwd_context = CryptContext(
    schemes=["bcrypt"]
)

ACCESS_TOKEN_EXPIRE = 3600

def generate_password_hash(password: str) -> str:
    """Generate a hashed password."""
    return passwd_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    """Verify a plain password against a hashed password."""
    return passwd_context.verify(password, hash)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRE)
        )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_access_token(token: str):
    try:
        token_data = jwt.decode(
            token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWKError as error:
        logging.exception(error)
        return None