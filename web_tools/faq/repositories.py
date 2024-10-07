
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from web_tools.models import UserDB, FAQSectionDB, FAQItemDB
from web_tools.faq.models import FAQSection
from sqlalchemy import func
from sqlalchemy.orm import selectinload



class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> UserDB:
        try:
            user_query = await self.session.execute(select(UserDB).filter(UserDB.email == email))
            user = user_query.scalar_one()
            return user
        except NoResultFound:
            raise ValueError(f"User with email {email} does not exist.")
        
    async def get_user_by_name(self, name: str) -> UserDB:
        try:
            user_query = await self.session.execute(select(UserDB).filter(UserDB.username == name))
            user = user_query.scalar_one()
            return user
        except NoResultFound:
            raise ValueError(f"User with email {name} does not exist.")
        
    async def update_user(self, user: UserDB) -> UserDB:
        existing_user = await self.get_user_by_email(user.email)
        if existing_user:
            existing_user.username = user.username
            existing_user.updated_at = func.now()
            await self.session.commit()
        return existing_user
        

class FAQRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_faq_section( self, section_guid: UUID) -> FAQSectionDB:
        query = select(FAQSectionDB).options(selectinload(FAQSectionDB.items)).where(FAQSectionDB.guid == section_guid)
        
        result = await self.session.execute(
            query
        )
        faq_section = result.scalar_one_or_none()
        return faq_section
    
    async def get_faq_section_by_id(self, section_id: int) -> Optional[FAQSectionDB]:
        result = await self.session.execute(select(FAQSectionDB).where(FAQSectionDB.id == section_id))
        return result.scalar_one_or_none()
    
    async def get_faq_section_by_guid(self, section_guid: str) -> Optional[FAQSectionDB]:
        result = await self.session.execute(select(FAQSectionDB).where(FAQSectionDB.guid == section_guid))
        return result.scalar_one_or_none()

    async def insert_faq_section(self, faq_section: FAQSectionDB, faq_items: List[FAQItemDB]) -> FAQSectionDB:
        self.session.add(faq_section)
        self.session.add_all(faq_items)
        await self.session.commit()
        return faq_section

    async def append_faq_item(self, section_id: int, faq_item: FAQItemDB) -> FAQSectionDB:
        # Retrieve the existing FAQSection
        existing_section = await self.get_faq_section_by_id(section_id)
        if not existing_section:
            raise ValueError(f"FAQ Section with id {section_id} does not exist.")

        # Append the new FAQ item to the section
        faq_item.section = existing_section
        self.session.add(faq_item)

        # Commit the changes
        await self.session.commit()

        return existing_section

    async def update_faq_section(self, faq_section: FAQSectionDB) -> FAQSectionDB:
        existing_section = await self.get_faq_section_by_id(faq_section.id)
        if existing_section:
            existing_section.title = faq_section.title
            existing_section.description = faq_section.description
            await self.session.commit()
        return existing_section
    
    async def update_faq_section_visibility(self, section_guid: UUID, visbility: bool) -> FAQSectionDB:
        existing_section = await self.get_faq_section_by_guid(section_guid)
        if existing_section:
            existing_section.is_public = visbility
            await self.session.commit()
        return existing_section

    async def delete_faq_section(self, section_guid: UUID) -> None:
        print(section_guid)
        section = await self.get_faq_section_by_guid(section_guid)
        if section:
            await self.session.delete(section)
            await self.session.commit()




async def insert_faq_section(
    user_repo: UserRepository,
    faq_repo: FAQRepository,
    user_email: str,
    faq_section: FAQSection
) -> FAQSectionDB:
    # Step 1: Retrieve the user by email using UserRepository
    user = await user_repo.get_user_by_email(user_email)

    # Step 2: Create FAQSectionDB instance
    faq_section_db = FAQSectionDB(
        title=faq_section.title,
        description=faq_section.description,
        user_id=user.id
    )

    # Step 3: Convert FAQItems and associate them with the FAQSectionDB
    faq_items_db = [
        FAQItemDB(
            question=item.question,
            answer=item.answer,
            order=item.order,
            section=faq_section_db
        ) for item in faq_section.items
    ]

    # Step 4: Insert the FAQ section and items using FAQRepository
    inserted_faq_section = await faq_repo.insert_faq_section(faq_section_db, faq_items_db)

    return inserted_faq_section