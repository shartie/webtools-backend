from uuid import UUID

from sqlalchemy.future import select

from web_tools.models import UserDB, FAQSectionDB, FAQItemDB
from web_tools.faq.models import FAQSection
from web_tools.faq.repositories import UserRepository, FAQRepository


class FAQSectionService:
    def __init__(self, user_repo: UserRepository, faq_repo: FAQRepository):
        self.user_repo = user_repo
        self.faq_repo = faq_repo

    async def insert_faq_section(
        self, user_email: str, faq_section: FAQSection
    ) -> FAQSectionDB:
        # Step 1: Retrieve the user by email using UserRepository
        user = await self.user_repo.get_user_by_email(user_email)

        # Step 2: Create FAQSectionDB instance
        faq_section_db = FAQSectionDB(
            title=faq_section.title,
            description=faq_section.description,
            user_id=user.id,
        )

        # Step 3: Convert FAQItems and associate them with the FAQSectionDB
        faq_items_db = [
            FAQItemDB(
                question=item.question,
                answer=item.answer,
                order=item.order,
                section=faq_section_db,
            )
            for item in faq_section.items
        ]

        # Step 4: Insert the FAQ section and items using FAQRepository
        inserted_faq_section = await self.faq_repo.insert_faq_section(
            faq_section_db, faq_items_db
        )

        return inserted_faq_section

    async def get_faq_sections(self, user_guid: UUID) -> list[FAQSectionDB]:
        query = select(FAQSectionDB, UserDB).where(
            UserDB.guid == user_guid, FAQSectionDB.user_id == UserDB.id
        )
        print(query)
        print(self.faq_repo.session)
        print(user_guid)
        result = await self.faq_repo.session.execute(query)
        results = result.scalars().all()

        return results

    async def get_faq_section(self, user_guid: UUID, faq_guid: UUID) -> FAQSectionDB:
        section = await self.faq_repo.get_faq_section(faq_guid)
        return section

    async def get_shared_faq_section(self, faq_guid: UUID) -> FAQSectionDB:
        section = await self.faq_repo.get_faq_section(faq_guid)
        return section

    async def update_faq_section_visibility(
        self, section_guid: UUID, visibility: bool
    ) -> FAQSectionDB:
        section = await self.faq_repo.update_faq_section_visibility(
            section_guid, visibility
        )
        return section

    async def delete_faq_section(self, user_guid: UUID, faq_guid: UUID) -> FAQSectionDB:
        section = await self.faq_repo.delete_faq_section(faq_guid)
        return section
