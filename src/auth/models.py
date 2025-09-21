from sqlmodel import SQLModel, Field, Column, String, Relationship
import sqlalchemy.dialects.postgresql as pg
import uuid
from datetime import datetime
from typing import List
from src.books import models

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(sa_column=Column(
        pg.UUID,
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
        )
    )
    username: str = Field(
        sa_column=Column(String, unique=True, nullable=False)  # 👈 add String
    )
    email: str = Field(
        sa_column=Column(String, unique=True, nullable=False)  # 👈 add String
    )
    password_hash: str = Field(exclude=True)
    first_name: str 
    last_name: str 
    is_verified: bool = Field(default=False)
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=datetime.now
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=datetime.now,
            onupdate=datetime.now
        )
    )

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"