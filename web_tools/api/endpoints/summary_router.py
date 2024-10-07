from typing import List, Optional
import asyncio
from sqlalchemy.orm import selectinload
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from uuid import UUID


from web_tools.api.deps import get_session, get_session_manager

# Usage example


# Assuming the necessary imports and models are available
from web_tools.summaries.models import (
    WebSummaryResponse,
    CreateWebSummaryRequest,
    SummaryData,
    AuthorRead,
    SummaryCreate,
    SummaryRead,
)

from web_tools.models import SummaryDB, AuthorDB
from web_tools.summaries.summaries import summary_agent

import logging


logger = logging.getLogger("summary_router")
router = APIRouter()


class WebSummaryUpdate(BaseModel):
    type: str
    message: str
    result: Optional[str] = None
    summary_data: Optional[SummaryData] = None


async def process_llm_responses(queue: asyncio.Queue, text: str):
    """Background task that processes LLM responses and puts updates into the queue."""
    try:
        await queue.put(
            WebSummaryUpdate(
                type="info", message="Generating summary...", result=None
            ).model_dump_json()
            + "\n"
        )
        await queue.put(
            WebSummaryUpdate(
                type="info", message="Summary generated successfully...", result=None
            ).model_dump_json()
            + "\n"
        )
        async for chunk in summary_agent.astream(
            {
                "content": text,
                "summary": "",
                "critic": "",
                "grounded_summary": "",
                "revise_iterations": 0,
            },
            stream_mode="updates",
        ):
            for node, values in chunk.items():
                print("-----------------")
                print(f"Receiving update from node: '{node}'")
                print("\n\n")

                if node == "grounding":
                    await queue.put(
                        WebSummaryUpdate(
                            type="result",
                            message="Grounding summary...",
                            result=values["grounded_summary"],
                        ).model_dump_json()
                        + "\n"
                    )
                elif node == "summary_data":
                    await queue.put(
                        WebSummaryUpdate(
                            type="result",
                            message="Summary generated successfully...",
                            summary_data=values["summary_preview"],
                        ).model_dump_json()
                        + "\n"
                    )

                    try:
                        summary_data = values["summary_preview"]
                        summary_content = values["grounded_summary"]

                        async with get_session_manager() as session:
                            new_summary = SummaryDB(
                                title=summary_data.title,
                                short_description=summary_data.short_description,
                                content=summary_content,
                            )

                            # Handle authors
                            authors = []
                            for author_name in summary_data.authors:
                                stmt = select(AuthorDB).where(
                                    AuthorDB.name == author_name
                                )
                                result = await session.execute(stmt)
                                author = result.scalars().first()
                                if not author:
                                    author = AuthorDB(name=author_name)
                                    session.add(author)
                                    await (
                                        session.flush()
                                    )  # Ensure author.id is populated
                                authors.append(author)

                            new_summary.authors = authors
                            session.add(new_summary)

                            await session.commit()
                            await (
                                session.flush()
                            )  # Ensure all pending operations are executed

                    except Exception as e:
                        print(e)

                else:
                    await queue.put(
                        WebSummaryUpdate(
                            type="info",
                            message=f"Summary is currently processed by {node}",
                            result=None,
                        ).model_dump_json()
                        + "\n"
                    )
            await asyncio.sleep(0.1)  # Simulating async work
    except Exception as e:
        # Optionally handle the exception
        await queue.put(
            WebSummaryUpdate(
                type="error",
                message=f"An error occurred: {e}",
                result=None,
            ).model_dump_json()
            + "\n"
        )
    finally:
        await queue.put(None)  # Signal completion


async def generate_llm_responses_ndjson(queue: asyncio.Queue):
    """Generator that yields newline-delimited JSON responses from the queue."""
    while True:
        item = await queue.get()
        if item is None:
            break
        yield item


@router.post("/summary/create", response_model=WebSummaryResponse)
async def generate_summary(
    request: CreateWebSummaryRequest, session: AsyncSession = Depends(get_session)
):
    try:
        # print("inside generate_faq")
        # async def generate_llm_responses_ndjson(text: str):
        #     """Generator that yields newline-delimited JSON responses from the LLM."""
        #     yield WebSummaryUpdate(type="info", message="Generating summary...", result=None).model_dump_json() + "\n"
        #     yield WebSummaryUpdate(type="info", message="Summary generated successfully...", result=None).model_dump_json() + "\n"
        #     async for chunk in summary_agent.astream({"content": content_web, "summary": "" , "critic": "", "grounded_summary": "", "revise_iterations": 0}, stream_mode="updates"):
        #         for node, values in chunk.items():
        #             print('-----------------')
        #             print(f"Receiving update from node: '{node}'")
        #             print("\n\n")

        #             if node == "grounding":
        #                 yield WebSummaryUpdate(type="result", message="Grounding summary...", result=values["grounded_summary"]).model_dump_json() + "\n"

        #             else :
        #                 yield WebSummaryUpdate(type="info", message=f"Summary is current processed by {node}", result=None).model_dump_json() + "\n"

        #         await asyncio.sleep(0.1)  # Simulating async work

        # return StreamingResponse(
        #     generate_llm_responses_ndjson(request.text),
        #     media_type="application/x-ndjson",
        # )

        text = request.text
        queue = asyncio.Queue()
        asyncio.create_task(process_llm_responses(queue, text))
        return StreamingResponse(
            generate_llm_responses_ndjson(queue),
            media_type="application/x-ndjson",
        )

    except ValueError:
        # Log the error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format."
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
            detail="Internal server error.",
        )


@router.post("/summaries/", response_model=SummaryRead)
async def create_summary(
    summary: SummaryCreate, session: AsyncSession = Depends(get_session)
):
    # Create Summary instance
    new_summary = SummaryDB(
        title=summary.title,
        short_description=summary.short_description,
        content=summary.content,
        status=summary.status,
        is_deleted=summary.is_deleted,
        user_id=summary.user_id,
    )

    # Handle authors
    authors = []
    for author_name in summary.authors:
        stmt = select(AuthorDB).where(AuthorDB.name == author_name)
        result = await session.execute(stmt)
        author = result.scalars().first()
        if not author:
            author = AuthorDB(name=author_name)
            session.add(author)
            await session.flush()  # Ensure author.id is populated
        authors.append(author)

    new_summary.authors = authors
    session.add(new_summary)

    await session.commit()
    await session.flush()  # Ensure all pending operations are executed
    # await session.refresh(new_summary)
    return new_summary


@router.get("/summaries", response_model=List[SummaryRead])
async def get_summaries(db: AsyncSession = Depends(get_session)):
    stmt = select(SummaryDB).options(
        # Ensure authors are loaded
        selectinload(SummaryDB.authors)
    )
    result = await db.execute(stmt)
    summaries = result.scalars().all()
    print(summaries)
    if not summaries:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summaries


@router.get("/summaries/{summary_id}", response_model=SummaryRead)
async def get_summary(summary_id: UUID, db: AsyncSession = Depends(get_session)):
    stmt = (
        select(SummaryDB)
        .where(SummaryDB.id == summary_id)
        .options(
            # Ensure authors are loaded
            selectinload(SummaryDB.authors)
        )
    )
    result = await db.execute(stmt)
    summary = result.scalars().first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/authors/", response_model=List[AuthorRead])
async def list_authors(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)
):
    stmt = select(AuthorDB).offset(skip).limit(limit)
    result = await db.execute(stmt)
    authors = result.scalars().all()
    return authors
