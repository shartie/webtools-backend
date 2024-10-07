from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from alembic.config import Config
from alembic import command


import asyncio

from web_tools.api.endpoints.fag_router import router as faq_router
from web_tools.api.endpoints.user_router import router as user_router
from web_tools.api.endpoints.summary_router import router as summary_router

import logging
import uvicorn

# Define the logging configuration
# LOGGING_CONFIG = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "default": {
#             "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         },
#         "uvicorn": {
#             "format": "%(levelprefix)s %(message)s",
#         },
#     },
#     "handlers": {
#         "default": {
#             "formatter": "default",
#             "class": "logging.StreamHandler",
#             "stream": "ext://sys.stdout",
#         },
#         "file": {
#             "formatter": "default",
#             "class": "logging.FileHandler",
#             "filename": "app.log",
#         },
#         "uvicorn.access": {
#             "formatter": "uvicorn",
#             "class": "logging.StreamHandler",
#             "stream": "ext://sys.stdout",
#         },
#     },
#     "loggers": {
#         "faq_generator": {
#             "handlers": ["default", "file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "uvicorn": {
#             "handlers": ["default"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "uvicorn.error": {
#             "level": "INFO",
#             "handlers": ["default"],
#             "propagate": False,
#         },
#         "uvicorn.access": {
#             "level": "INFO",
#             "handlers": ["uvicorn.access"],
#             "propagate": False,
#         },
#     },
#     "root": {
#         "level": "INFO",
#         "handlers": ["default", "file"],
#     },
# }

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"],
    },
    "loggers": {
        "faq_generator": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
    },
}

# Apply the logging configuration


logger = logging.getLogger("faq_generator")


async def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    logger.info("Loading the ML model")
    try:
        await apply_migrations()
        print("Migrations applied")
        logging.config.dictConfig(LOGGING_CONFIG)
        logger.info("Life span started")
    except Exception as e:
        logger.error("Error loading the ML model")
        logger.error(e)
        raise e
    # logger = logging.getLogger("uvicorn.error")
    # logger.setLevel(logging.DEBUG)
    # stream_handler = logging.StreamHandler(sys.stdout)
    # log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
    # stream_handler.setFormatter(log_formatter)
    # logger.addHandler(stream_handler)

    # logger.info('API is starting up')
    yield
    # Clean up the ML models and release the resources


api_router = APIRouter()


api_router.include_router(faq_router, tags=["FAQ"])
api_router.include_router(user_router, tags=["User"])
api_router.include_router(summary_router, tags=["Summaries"])

# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


app.include_router(api_router, prefix="/api")


# Define an endpoint that returns a list of strings
@app.post("/items")
def get_items():
    logger.info("Handling /items POST request")
    return {"faq": [["apple", "apple 1"]]}


# Run the app using Uvicorn
if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8080, log_config=LOGGING_CONFIG, log_level="info"
    )
