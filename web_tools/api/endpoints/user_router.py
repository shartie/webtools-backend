import logging

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from web_tools.api.deps import get_session
from web_tools.faq.repositories import UserRepository
from web_tools.faq.models import UserResponse, GetUserDetailsRequest

logger = logging.getLogger("faq_generator")
router = APIRouter()


@router.post("/users/details", response_model=UserResponse)
async def fetch_user_details(
    request: GetUserDetailsRequest, session: AsyncSession = Depends(get_session)
):
    """
    Fetches user details based on the provided email.
    ### Parameters:
    - request: `GetUserDetailsRequest` - The request object containing the email of the user.
    - session: `AsyncSession` (optional) - The database session to use for querying user details.
    ### Returns:
    - UserResponse - The response object containing the `email`, `guid`, and `username` of the user.
    ### Raises:
    - HTTPException - If the user is not found or if there is an internal server error.
    ### Description:
    This endpoint is used to fetch user details based on the provided email. It takes a `GetUserDetailsRequest` object as input, which contains the email of the user. The function queries the database using the provided email and returns a `UserResponse` object containing the email, guid, and username of the user. If the user is not found, a `HTTPException` with status code 404 is raised. If there is an internal server error, a `HTTPException` with status code 500 is raised.
    """
    try:
        # user_email = "alice@faq-generator.com"  # Example email
        user_email = request.email
        # "https://github.com/assafelovic/gpt-researcher/blob/master/README.md"

        user_repo = UserRepository(session)

        user_db = await user_repo.get_user_by_email(user_email)
        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

        return UserResponse(
            email=user_db.email, guid=user_db.guid, username=user_db.username
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
