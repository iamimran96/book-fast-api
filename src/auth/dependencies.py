from fastapi.security import HTTPBearer
from fastapi import Depends, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.utils import decode_access_token
from src.auth.redis import token_in_blocklist
from src.db.main import get_session
from src.auth.service import AuthService
from typing import Any

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials

        token_data = decode_access_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                content ="Invalid or expired token"
                )
        
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail= {
                 "error": "Token has been revoked",
                 "resolution": "Please log in again to obtain a new token"   
                },
                
            )

        self.verify_token_data(token_data)
        return token_data
    
    def token_valid(self, token: str) -> bool:
        token_data = decode_access_token(token)
        return token_data is not None 
    
    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please Override this method in child classes")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
                )
        
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )

async def get_current_user(
        token_data = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)
    ) -> dict:
    user = await AuthService.get_user_by_email(session, token_data['user']['email'])
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list) -> None:
        self.allowed_roles = allowed_roles
    
    def __call__(self, user = Depends(get_current_user)) -> bool:
        user_role = user.role
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to access this resource"
            )
        return True
