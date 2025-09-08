from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, text, SQLModel
from src.config import Config

engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=True))

async def init_db():
    """Initialize the database connection."""
    async with engine.begin() as conn:
        from src.books.models import Book
        from src.auth.models import User
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    """Create a new database session."""
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as db_session:
        yield db_session