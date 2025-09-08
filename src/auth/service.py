from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from .models import User
from .schemas import CreateUser
from .utils import generate_password_hash

class AuthService:
    @staticmethod
    async def get_user_by_email(db_session: AsyncSession, email: str):
        statement = select(User).where(User.email == email)
        result = await db_session.exec(statement)
        return result.first()

    @staticmethod
    async def user_exist(db_session: AsyncSession, email):
        user = await AuthService.get_user_by_email(db_session, email)
        return user is not None
    
    @staticmethod
    async def create_user(db_session: AsyncSession, user_create: CreateUser) -> User:
        user_create_data = user_create.model_dump()
        new_user = User(**user_create_data)
        new_user.password_hash = generate_password_hash(user_create_data['password'])
        db_session.add(new_user)
        await db_session.commit()
        return new_user