import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Assuming you've imported the Base, User, FAQSection, FAQItem from your models
from web_tools.core import database_session  # Import your session creator
from web_tools.models import UserDB, FAQSectionDB, FAQItemDB  # Replace with the actual path to your models

# Function to populate the database
async def populate_database():
    

    async with database_session.get_async_session() as session:
        # Create users
        user1 = UserDB(username="alice", email="alice@faq-generator.com")
        user2 = UserDB(username="bob", email="bob@faq-generator.com")

        session.add(user1)
        session.add(user2)
        await session.commit()  # Commit to generate IDs for users

        # Create FAQ Sections
        faq_section1 = FAQSectionDB(
            title="General Questions",
            description="Frequently asked questions about general topics.",
            user=user1
        )

        faq_section2 = FAQSectionDB(
            title="Technical Support",
            description="Questions related to technical issues and support.",
            user=user2
        )

        session.add(faq_section1)
        session.add(faq_section2)
        await session.commit()  # Commit to generate IDs for FAQ sections

        # Create FAQ Items
        faq_item1 = FAQItemDB(
            question="What is this platform?",
            answer="This platform provides a variety of services.",
            order=1,
            section=faq_section1
        )

        faq_item2 = FAQItemDB(
            question="How do I reset my password?",
            answer="Click on 'Forgot password' on the login page.",
            order=2,
            section=faq_section1
        )

        faq_item3 = FAQItemDB(
            question="How do I contact support?",
            answer="You can contact support via the support page.",
            order=1,
            section=faq_section2
        )

        session.add_all([faq_item1, faq_item2, faq_item3])
        await session.commit()

        print("Database populated with sample data.")

# Main entry point to run the script
if __name__ == "__main__":
    asyncio.run(populate_database())
