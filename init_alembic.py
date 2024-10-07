

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware


from alembic.config import Config
from alembic import command


from sqlalchemy.ext.asyncio import AsyncSession





api_router = APIRouter()


def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    
    command.upgrade(alembic_cfg, "head")


apply_migrations()