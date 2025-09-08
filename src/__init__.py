from fastapi import FastAPI
from src.books.routes import books_router
from src.auth.routes import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting application...")
    yield
    print("Shutting down application...")

app = FastAPI(
    title="Imrania BookStore API",
    description="A simple book API with user authentication",
    version="1.0.0",
    lifespan=life_span
)

app.include_router(books_router, prefix="/api/v1", tags=["Books"])
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])