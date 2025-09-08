from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException as HttpException
from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.books.schemas import Book, BookUpdate, BookCreate
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer

# Create a router instance for book-related endpoints
books_router = APIRouter()

# Create AccessTokenBearer instance for authentication
access_token_bearer = AccessTokenBearer()

# GET /books - Retrieve all books
@books_router.get("/books", response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_books(session: AsyncSession = Depends(get_session), user_detials = Depends(access_token_bearer)) -> List[Book]:
    books = await BookService().get_books(session)
    return books

# POST /books - Create a new book
@books_router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
async def add_book(book_data: BookCreate, session: AsyncSession = Depends(get_session), user_detials = Depends(access_token_bearer)):
    new_book = await BookService().add_book(session, book_data)
    return new_book

# GET /books/{book_id} - Retrieve a specific book by book_id
@books_router.get("/books/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book(book_id: str, session: AsyncSession = Depends(get_session), user_detials = Depends(access_token_bearer)) -> Book:
    book = await BookService().get_book(session, book_id)
    if book:
        return book
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# PATCH /books/{book_id} - Update a specific book by book_id
@books_router.patch("/books/{book_id}", response_model=Book)
async def update_book(book_id: str, update_book: BookUpdate, session: AsyncSession = Depends(get_session), user_detials = Depends(access_token_bearer)) -> Book:
    book = await BookService().update_book(session, book_id, update_book)
    if book:
        return book
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# DELETE /books/{book_id} - Delete a specific book by book_id
@books_router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session), user_detials = Depends(access_token_bearer)):
    book_to_delete = await BookService().delete_book(session, book_id)
    if book_to_delete is not None:
        return {}
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


