from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from .models import Book
from .schemas import BookCreate, BookUpdate

class BookService:
    @staticmethod
    async def get_books(db_session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await db_session.exec(statement)
        return result.all()
    
    async def get_user_books(db_session: AsyncSession, user_uid: str):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await db_session.exec(statement)
        return result.all()

    @staticmethod
    async def get_book(db_session: AsyncSession, book_id: str) -> Book:
        statement = select(Book).where(Book.uid == book_id)
        result = await db_session.exec(statement)
        return result.first()

    @staticmethod
    async def add_book(db_session: AsyncSession, user_uid: str, book_create: BookCreate) -> Book:
        new_book = Book(**book_create.model_dump())
        new_book.user_uid = user_uid
        db_session.add(new_book)
        await db_session.commit()
        await db_session.refresh(new_book)
        return new_book

    @staticmethod
    async def update_book(db_session: AsyncSession, book_id: str, book_update: BookUpdate) -> Book:
        book = await BookService.get_book(db_session, book_id)
        if book is not None:
            update_book = book_update.model_dump()
            for k, v in update_book.items():
                setattr(book, k, v)
            
            await db_session.commit()
        return book

    @staticmethod
    async def delete_book(db_session: AsyncSession, book_id: str):
        book = await BookService.get_book(db_session, book_id)
        if book is not None:
            await db_session.delete(book)
            await db_session.commit()
            return {}
        else:
            return None