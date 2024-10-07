
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, APIRouter,  HTTPException, status
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# from hotnews.api.core.config import settings

from sqlalchemy.future import select
from alembic.config import Config
from alembic import command

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from web_tools.models import FAQSectionDB, FAQItemDB, UserDB
from pydantic import BaseModel

from uuid import UUID

# from hotnews.db.models import AsyncSessionLocal
# from hotnews.db.models import HotNewsItem

# from hotnews.models import HotNewsItem as HotNewsItemModel
# from hotnews.api.db import get_session

from web_tools.api.deps import get_session

from openai import OpenAI, AsyncOpenAI
from web_tools.faq.generation import AsyncFAQGenerator

# Usage example
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Assuming the necessary imports and models are available
from web_tools.faq.repositories import UserRepository, FAQRepository
from web_tools.faq.services import FAQSectionService
from web_tools.faq.models import FAQSectionResponse, FAQItemResponse, CreateFromUrlRequest, UpdateFAQSectionRequest

import os

from web_tools.utils.github_utils import parse_github_url, read_file_from_github
from web_tools.utils.text_utils import clean_markdown_content

import logging

logger = logging.getLogger("faq_generator")
router = APIRouter()

def get_faq_service(session: AsyncSession = Depends(get_session)):

    user_repo = UserRepository(session)
    faq_repo = FAQRepository(session)
    return FAQSectionService(user_repo, faq_repo=faq_repo)

@router.post("/users/{user_id}/faqs/create", response_model=FAQSectionResponse)
async def generate_faq( user_id: str, request: CreateFromUrlRequest, session: AsyncSession = Depends(get_session)):

    try:
        user_email = "alice@faq-generator.com"  # Example email
        # "https://github.com/assafelovic/gpt-researcher/blob/master/README.md"
        url = request.url
        token = os.getenv("GITHUB_ACCESS_TOKEN")
        repo_name, file_name = parse_github_url(url=url)
        # Replace with the repository name in 'owner/repo' format
        #file_content = read_file_from_github(token, "assafelovic/gpt-researcher", "README.md")
        file_content = read_file_from_github(token, repo_name, file_name)
        cleaned_file_content = clean_markdown_content(file_content)

        # print(file_content)
        print(cleaned_file_content)

        client = AsyncOpenAI()

        faq_generator = AsyncFAQGenerator(client)
        faq_section = await faq_generator.generate_faq_section(

            topic=cleaned_file_content
        )

        user_repo = UserRepository(session)
        faq_repo = FAQRepository(session)

        faq_service = FAQSectionService(user_repo, faq_repo=faq_repo)

        inserted_faq_section = await faq_service.insert_faq_section( user_email, faq_section)
        logger.info(f"Inserted FAQ Section ID: {inserted_faq_section.guid}")

        return FAQSectionResponse(
            title=inserted_faq_section.title,
            description=inserted_faq_section.description,
            guid=inserted_faq_section.guid,
            items=[
                FAQItemResponse(
                    question=item.question,
                    answer=item.answer,
                    guid=item.guid,
                    order=item.order
                ) for item in inserted_faq_section.items
            ]
        )
        
    except ValueError:
        # Log the error
        logger.error(f"Invalid UUID format for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )

@router.get("/users/{user_id}/faqs", response_model=list[FAQSectionResponse])
async def retrieve_faqs( user_id: str, faq_service: FAQSectionService = Depends(get_faq_service)):

    fags = []
    try:
        
        logger.info(f"Retrieving FAQ sections for user {user_id}")
        user_guid = UUID(user_id)
        logger.info("after uuid confversion")
        faq_sections = await faq_service.get_faq_sections(user_guid=user_guid)
        
        if not faq_sections:
            logger.warning(f"FAQ sections not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ section not found."
            )

        for result in faq_sections:
            faq_section = FAQSectionResponse(title=result.title, description=result.description, guid=result.guid, is_public=result.is_public)
            fags.append(faq_section)

        return fags

    except ValueError as e:
        # Log the error
        logger.error(f"Invalid UUID format for user {user_id}")
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )

@router.get("/users/{user_id}/faqs/{faq_id}", response_model=FAQSectionResponse)
async def retrieve_individual_faq(
    user_id: str,
    faq_id: str,
    faq_service: FAQSectionService = Depends(get_faq_service)
):
    try:
        # Log the incoming request
        logger.info(f"Retrieving FAQ section for user {user_id} and FAQ {faq_id}")

        # Convert user_id and faq_id to UUID
        user_guid = UUID(user_id)
        faq_guid = UUID(faq_id)

        # Attempt to retrieve the FAQ section
        faq_section = await faq_service.get_faq_section(user_guid=user_guid, faq_guid=faq_guid)

        # If the FAQ section is not found, log and raise a 404 Not Found exception
        if not faq_section:
            logger.warning(f"FAQ section not found for user {user_id} and FAQ {faq_id}")
            raise HTTPException(
                status_code=status.HTTP_405_NOT_FOUND,
                detail="FAQ section not found."
            )

        # Log successful retrieval
        logger.info(f"Successfully retrieved FAQ section for user {user_id} and FAQ {faq_id}")

        # Create and return the response model
        return FAQSectionResponse(
            title=faq_section.title,
            description=faq_section.description,
            guid=faq_section.guid,
            is_public=faq_section.is_public,
            items=[
                FAQItemResponse(
                    question=item.question,
                    answer=item.answer,
                    guid=item.guid,
                    order=item.order
                ) for item in faq_section.items
            ]
        )

    except ValueError:
        # Log the error
        logger.error(f"Invalid UUID format for user {user_id} or FAQ {faq_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )
    
@router.get("/shared/{faq_id}", response_model=FAQSectionResponse)
async def retrieve_shared_faq(
    faq_id: str,
    faq_service: FAQSectionService = Depends(get_faq_service)
):
    try:
        # Log the incoming request
        logger.info(f"Retrieving shared FAQ section and FAQ {faq_id}")

        # Convert user_id and faq_id 
        faq_guid = UUID(faq_id)

        # Attempt to retrieve the FAQ section
        faq_section = await faq_service.get_shared_faq_section(faq_guid=faq_guid)

        # If the FAQ section is not found, log and raise a 404 Not Found exception
        if not faq_section:
            logger.warning(f"FAQ section not found for user {user_id} and FAQ {faq_id}")
            raise HTTPException(
                status_code=status.HTTP_405_NOT_FOUND,
                detail="FAQ section not found."
            )
        
        if faq_section.is_public == False:
            logger.warning(f"FAQ section not found for user {user_id} and FAQ {faq_id}")
            raise HTTPException(
                status_code=status.HTTP_405_NOT_FOUND,
                detail="FAQ section not found."
            )

        # Log successful retrieval
        logger.info(f"Successfully retrieved shared FAQ section fo and FAQ {faq_id}")

        # Create and return the response model
        return FAQSectionResponse(
            title=faq_section.title,
            description=faq_section.description,
            guid=faq_section.guid,
            is_public=faq_section.is_public,
            items=[
                FAQItemResponse(
                    question=item.question,
                    answer=item.answer,
                    guid=item.guid,
                    order=item.order
                ) for item in faq_section.items
            ]
        )

    except ValueError:
        # Log the error
        logger.error(f"Invalid UUID format for or FAQ {faq_id}")
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )
    
@router.put("/users/{user_id}/faqs/{faq_id}", response_model=FAQSectionResponse)
async def update_individual_faq(
    user_id: str,
    faq_id: str,
    update_request: UpdateFAQSectionRequest,
    faq_service: FAQSectionService = Depends(get_faq_service)
):
    try:
        # Log the incoming request
        logger.info(f"Update FAQ section for user {user_id} and FAQ {faq_id}")

        # Convert user_id and faq_id to UUID
        user_guid = UUID(user_id)
        faq_guid = UUID(faq_id)

        # Attempt to retrieve the FAQ section
        faq_section = await faq_service.update_faq_section_visibility(section_guid=faq_guid, visibility=update_request.visibility)
        # faq_section = await faq_service.get_faq_section(user_guid=user_guid, faq_guid=faq_guid)

        # If the FAQ section is not found, log and raise a 404 Not Found exception
        if not faq_section:
            logger.warning(f"FAQ section not found for user {user_id} and FAQ {faq_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ section not found."
            )

        # Log successful retrieval
        logger.info(f"Successfully retrieved FAQ section for user {user_id} and FAQ {faq_id}")

        # Create and return the response model
        return FAQSectionResponse(
            title=faq_section.title,
            description=faq_section.description,
            guid=faq_section.guid,
            is_public=faq_section.is_public,
            items=[
                FAQItemResponse(
                    question=item.question,
                    answer=item.answer,
                    guid=item.guid,
                    order=item.order
                ) for item in faq_section.items
            ]
        )

    except ValueError:
        # Log the error
        logger.error(f"Invalid UUID format for user {user_id} or FAQ {faq_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )

    
@router.delete("/users/{user_id}/faqs/{faq_id}")
async def delete_individual_faq(
    user_id: str,
    faq_id: str,
    faq_service: FAQSectionService = Depends(get_faq_service)
):
    try:
        # Log the incoming request
        logger.info(f"Deleting FAQ section for user {user_id} and FAQ {faq_id}")

        # Convert user_id and faq_id to UUID
        user_guid = UUID(user_id)
        faq_guid = UUID(faq_id)

        # Attempt to retrieve the FAQ section
        await faq_service.delete_faq_section(user_guid=user_guid, faq_guid=faq_guid)

        # If the FAQ section is not found, log and raise a 404 Not Found exception
        
        # Log successful retrieval
        logger.info(f"Successfully retrieved FAQ section for user {user_id} and FAQ {faq_id}")

        # Create and return the response model
        return True
    except ValueError:
        # Log the error
        logger.error(f"Invalid UUID format for user {user_id} or FAQ {faq_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format."
        )

    except HTTPException as http_exc:
        # Log the HTTP exception
        logger.warning(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        # Log the exception
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        # Raise a 500 Internal Server Error for unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )
