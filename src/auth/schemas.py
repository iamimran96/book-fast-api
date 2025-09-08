from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class CreateUser(BaseModel):
    first_name: str = Field(max_length=21)
    last_name: str = Field(max_length=21)
    username: str = Field(max_length=32)    
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class User(BaseModel):
    uid: uuid.UUID
    username: str 
    email: str
    password_hash: str = Field(exclude=True) 
    first_name: str
    last_name: str 
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class LoginUser(BaseModel):
    email: str
    password: str