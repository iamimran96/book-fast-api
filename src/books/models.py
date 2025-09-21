import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime, date
import uuid
from typing import Optional
from src.auth import models
class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(sa_column=Column(
        pg.UUID,
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid",
    )
    user: Optional["models.User"] = Relationship(back_populates="books")
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
        return f"<Book {self.title} by {self.author}>"