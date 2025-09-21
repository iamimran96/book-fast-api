from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException as HttpException
from typing import List
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.books.schemas import Book, BookUpdate, BookCreate
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

# Create a router instance for book-related endpoints
books_router = APIRouter()

# Create AccessTokenBearer instance for authentication
access_token_bearer = AccessTokenBearer()

# Role-based access control can be added as needed
role_checker = Depends(RoleChecker(["admin", "user"]))

# GET /books - Retrieve all books
@books_router.get("/books", response_model=List[Book], status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_books(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer)
    ) -> List[Book]:
    """
    Endpoint to get all books.
    
    - Retrieve a list of all books in the database.
    - Accessible by users with 'admin' or 'user' roles.
    """
    books = await BookService.get_books(session)
    return books

# POST /books - Create a new book
@books_router.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, dependencies=[role_checker])
async def add_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session),
    user_detials = Depends(access_token_bearer)
    ) -> Book:
    """
    Endpoint to add book in inventory.
    
    - Create a new book entry.
    - Associates the book with the currently authenticated user.
    """
    user_uid = user_detials.get("user")[ "uid"]
    new_book = await BookService.add_book(session, user_uid ,book_data)
    return new_book

# GET /user/{user_uid} - Retrieve all books submitted by a specific user
@books_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
    ) -> List[Book]:
    """
    Endpoint to get a books.
    
    - Retrieve all books created by a specific user using their UID.
    """
    books = await BookService.get_user_books(user_uid, session)
    return books

# GET /books/{book_id} - Retrieve a specific book by book_id
@books_router.get("/books/{book_id}", response_model=Book, status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer)
    ) -> Book:
    """
    Endpoint to get a book by its ID.
    
    - Retrieve a specific book by its ID.
    - Returns 404 if the book is not found.
    """
    book = await BookService.get_book(session, book_id)
    if book:
        return book
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# PATCH /books/{book_id} - Update a specific book by book_id
@books_router.patch("/books/{book_id}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_id: str,
    update_book: BookUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer)
    ) -> Book:
    """
    Endpoint to Update a book by its ID.
    
    - Update a book's details using its ID.
    - Returns 404 if the book does not exist.
    """
    book = await BookService.update_book(session, book_id, update_book)
    if book:
        return book
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# DELETE /books/{book_id} - Delete a specific book by book_id
@books_router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker])
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer)):
    """
    Endpoint to delete a book by its ID.
    
    - Delete a book by its ID.
    - Returns 204 No Content on success, or 404 if the book is not found.
    """
    book_to_delete = await BookService.delete_book(session, book_id)
    if book_to_delete is not None:
        return {}
    raise HttpException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
