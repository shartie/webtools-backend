import os
import asyncio

from openai import AsyncOpenAI
from web_tools.faq.generation import AsyncFAQGenerator

from web_tools.core import database_session
from web_tools.faq.repositories import UserRepository, FAQRepository
from web_tools.faq.services import FAQSectionService

from web_tools.utils.github_utils import parse_github_url, read_file_from_github
from web_tools.utils.text_utils import clean_markdown_content


async def main():
    # Assuming AsyncOpenAI client is correctly configured and available as `client`

    token = os.getenv("GITHUB_ACCESS_TOKEN")
    repo_name, file_name = parse_github_url(
        "https://github.com/assafelovic/gpt-researcher/blob/master/README.md"
    )
    # Replace with the repository name in 'owner/repo' format
    # file_content = read_file_from_github(token, "assafelovic/gpt-researcher", "README.md")
    file_content = read_file_from_github(token, repo_name, file_name)
    cleaned_file_content = clean_markdown_content(file_content)

    # print(file_content)
    print(cleaned_file_content)

    client = AsyncOpenAI()

    faq_generator = AsyncFAQGenerator(client)
    faq_section = await faq_generator.generate_faq_section(topic=cleaned_file_content)

    print(faq_section)
    user_email = "alice@faq-generator.com"  # Example email

    async with database_session.get_async_session() as session:
        user_repo = UserRepository(session)
        faq_repo = FAQRepository(session)

        faq_service = FAQSectionService(user_repo, faq_repo=faq_repo)

        inserted_faq_section = await faq_service.insert_faq_section(
            user_email, faq_section
        )
        print(f"Inserted FAQ Section ID: {inserted_faq_section.id}")

        # inserted_faq_section = await insert_faq_section(session, user_email, faq_section)
        # print(f"Inserted FAQ Section ID: {inserted_faq_section.id}")


if __name__ == "__main__":
    asyncio.run(main())
