import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from web_tools.core import database_session  # Import your session creator
from web_tools.models import UserDB, FAQSectionDB, FAQItemDB  # Replace with the actual path to your models
from sqlalchemy.exc import NoResultFound

# Function to get the user by email
async def get_user_by_email(session: AsyncSession, email: str) -> UserDB:
    try:
        user_query = await session.execute(select(UserDB).filter(UserDB.email == email))
        user = user_query.scalar_one()
        return user
    except NoResultFound:
        raise ValueError(f"User with email {email} does not exist.")

# Function to populate the database with synthetic FAQs for a specific user
async def insert_synthetic_faqs_for_user(email: str):
    async with database_session.get_async_session() as session:
        try:
            # Retrieve the user by email
            user = await get_user_by_email(session, email)

            # Create new FAQ Sections
            faq_section1 = FAQSectionDB(
                title="Synthetic General Questions 1",
                description="Synthetic frequently asked questions about general topics.",
                user=user
            )

            faq_section2 = FAQSectionDB(
                title="Synthetic Technical Support 2",
                description="Synthetic questions related to technical issues and support.",
                user=user
            )

            faq_section3 = FAQSectionDB(
                title="Synthetic Technical Support 3",
                description="Synthetic questions related to technical issues and support.",
                user=user
            )

            session.add(faq_section1)
            session.add(faq_section2)
            session.add(faq_section3)
            await session.commit()  # Commit to generate IDs for FAQ sections

            # Create new FAQ Items
            faq_item1 = FAQItemDB(
                question="What is a synthetic question?",
                answer="A synthetic question is automatically generated for testing purposes.",
                order=1,
                section=faq_section1
                
            )

            faq_item2 = FAQItemDB(
                question="How do I generate synthetic data?",
                answer="Synthetic data can be generated using various tools and scripts.",
                order=2,
                section=faq_section1
            )

            faq_item3 = FAQItemDB(
                question="How do I contact synthetic support?",
                answer="Synthetic support can be contacted via the synthetic support page.",
                order=1,
                section=faq_section2
            )

            faq_item4 = FAQItemDB(
                question="What is the purpose of synthetic FAQs?",
                answer="Synthetic FAQs are used for testing and simulation.",
                order=2,
                section=faq_section2
            )

            session.add_all([faq_item1, faq_item2, faq_item3, faq_item4])
            await session.commit()

            print(f"Synthetic FAQs have been inserted for user: {email}")
        except ValueError as e:
            print(str(e))

# Main entry point to run the script
if __name__ == "__main__":
    user_email = "alice@faq-generator.com"  # Replace with the desired email
    asyncio.run(insert_synthetic_faqs_for_user(user_email))
