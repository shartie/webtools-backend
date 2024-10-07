from fastapi import APIRouter
from alembic.config import Config
from alembic import command

api_router = APIRouter()


def apply_migrations():
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")


apply_migrations()
