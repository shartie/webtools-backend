from collections.abc import AsyncGenerator

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from web_tools.core import database_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with database_session.get_async_session() as session:
        yield session


@asynccontextmanager
async def get_session_manager() -> AsyncGenerator[AsyncSession, None]:
    async with database_session.get_async_session() as session:
        yield session
