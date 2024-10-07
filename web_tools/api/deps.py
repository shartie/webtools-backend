from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from web_tools.core   import database_session
from contextlib import asynccontextmanager


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with database_session.get_async_session() as session:
        yield session

@asynccontextmanager
async def get_session_manager() -> AsyncGenerator[AsyncSession, None]:
    async with database_session.get_async_session() as session:
        yield session

