from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as HttpException
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime

from src.auth.schemas import CreateUser, LoginUser
from src.db.main import get_session
from src.auth.service import AuthService
from src.auth.utils import verify_password, create_access_token
from src.auth.dependencies import RefreshTokenBearer

# Define the expiry time for the refresh token (2 days)
REFRESH_TOKEN_EXPIRY = timedelta(days=2)

# Create a router for authentication-related endpoints
auth_router = APIRouter()

# POST /signup - Create a new user account
@auth_router.post("/signup")
async def create_user_account(create_user: CreateUser, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to create a new user account.

    - Checks if the user already exists using the provided email.
    - If not, creates a new user record.
    """
    check_user = await AuthService.user_exist(session, create_user.email)
    if check_user:
        raise HttpException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already exists"
        )
    new_user = await AuthService.create_user(session, create_user)
    return new_user

# POST /login - Log in an existing user and return access/refresh tokens
@auth_router.post("/login")
async def login_user(user_login: LoginUser, session: AsyncSession = Depends(get_session)):
    """
    Endpoint to authenticate a user.

    - Verifies the user exists using the provided email.
    - Checks the provided password against the stored password hash.
    - If valid, generates and returns an access token and a refresh token.
    """
    print(user_login)  # Useful for debugging; remove in production

    # Fetch user by email
    user = await AuthService.get_user_by_email(session, user_login.email)

    if user is not None:
        # Verify the provided password against the stored hash
        if verify_password(user_login.password, user.password_hash):
            # Create token payload
            payload = {
                "uid": str(user.uid),
                "email": user.email
            }

            # Generate access and refresh tokens
            access_token = create_access_token(payload)
            refresh_token = create_access_token(payload, expiry=REFRESH_TOKEN_EXPIRY, refresh=True)

            # Return tokens and user info in response
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "uid": str(user.uid),
                        "email": user.email
                    }
                }
            )

    # If user doesn't exist or password is invalid, raise 401
    raise HttpException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

# POST /refresh - Refresh the access token using a valid refresh token
@auth_router.post("/refresh-token")
async def refresh_access_token(token_detials = Depends(RefreshTokenBearer())):
    """
    Endpoint to refresh the access token.

    - Requires a valid refresh token.
    - Generates and returns a new access token.
    """
    token_exp = token_detials['exp']
    if datetime.fromtimestamp(token_exp) > datetime.now():
        user_data = token_detials['user']
        new_access_token = create_access_token(user_data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": new_access_token
            }
        )
    
    raise HttpException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token"
    )