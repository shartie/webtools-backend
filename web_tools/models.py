

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ARRAY, func, ForeignKey, Table
import os

from web_tools.config import get_settings

EMBEDDING_DIM = 1536

settings = get_settings()

class Base(DeclarativeBase):
    pass
    # create_time: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )
    # update_time: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    # )

class HotNewsItemDB(Base):
    __tablename__ = 'HotNewsItem'
    __table_args__ = {'schema': os.getenv('DB_SCHEMA', 'hotnews_test')}

    id = Column(Integer, primary_key=True, autoincrement=True)
    guid = Column(String, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    url = Column(String)
    description = Column(Text)
    relevance_score = Column(Float)
    justification = Column(Text)
    html_content = Column(Text)
    hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    author = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    category = Column(String, nullable=True)
    tags = Column(ARRAY(String))  # PostgreSQL specific type
    source = Column(String, nullable=True)
    language = Column(String, nullable=True)
    status = Column(String, default="active")
    content = Column(String, default="")


# class DocumentDB(Base):
#     __tablename__ = 'documents'

#     __table_args__ = {'schema': 'hotnews_test'}
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
#     uploaded_by = Column(UUID(as_uuid=True), nullable=False)
#     title = Column(String(100))
#     description = Column(String(250))
#     url = Column(String)
#     mime_type = Column(String(100))
#     size = Column(Integer)
#     pages = Column(Integer)
#     md5 = Column(String(32))
#     tokens = Column(Integer)
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
    
#     # Assuming a relationship to document_chunks
#     chunks = relationship("DocumentChunkDB", back_populates="document")

# class DocumentChunkDB(Base):
#     __tablename__ = 'document_chunks'

#     __table_args__ = {'schema': 'hotnews_test'}
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
#     document_id = Column(UUID(as_uuid=True), ForeignKey('hotnews_test.documents.id'))
#     content = Column(String)
#     filename = Column(String(250))
#     page = Column(Integer)
#     index = Column(Integer)
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)

#     embedding = mapped_column(Vector(EMBEDDING_DIM))
    
#     # Define the relationship to Document
#     document = relationship("DocumentDB", back_populates="chunks")


# class UserDB(Base):
#     __tablename__ = 'user'
#     __table_args__ = {'schema': settings.database.schema}

#     id = Column(Integer, primary_key=True)
#     guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
#     username = Column(String(255), nullable=False, unique=True)
#     email = Column(String(255), nullable=False, unique=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#     faq_sections = relationship('FAQSectionDB', back_populates='user')

class UserDB(Base):
    __tablename__ = 'User'
    __table_args__ = {'schema': settings.database.schema}

    #id = Column(Integer, primary_key=True)
    id = Column( String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    #id = Column(UUID(as_uuid=True), nullable=True, unique=True, default=uuid.uuid4, primary_key=True)
    guid = Column(UUID(as_uuid=True), nullable=True, unique=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    emailVerified = Column(DateTime(timezone=True), server_default=func.now())
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # New relationships for Account and Session
    accounts = relationship('AccountDB', back_populates='user', cascade='all, delete-orphan')
    sessions = relationship('SessionDB', back_populates='user', cascade='all, delete-orphan')

    faq_sections = relationship('FAQSectionDB', back_populates='user')

class AccountDB(Base):
    __tablename__ = 'Account'
    __table_args__ = (
        UniqueConstraint('provider', 'providerAccountId', name='uq_provider_providerAccountId'),
        {'schema': settings.database.schema}
    )

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column( String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = Column(String, ForeignKey(f'{settings.database.schema}.User.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    providerAccountId = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    refresh_token_expires_in = Column(Integer, nullable=True)
    access_token = Column(String(255), nullable=True)
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String(255), nullable=True)
    scope = Column(String(255), nullable=True)
    id_token = Column(String(255), nullable=True)
    session_state = Column(String(255), nullable=True)
    not_before = Column(Integer, nullable=True)
    id_token_expires_in = Column(Integer, nullable=True)
    profile_info = Column(String(255), nullable=True)

    user = relationship('UserDB', back_populates='accounts')

class SessionDB(Base):
    __tablename__ = 'Session'
    __table_args__ = {'schema': settings.database.schema}

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column( String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    sessionToken = Column(String(255), nullable=False, unique=True)
    userId = Column(String, ForeignKey(f'{settings.database.schema}.User.id', ondelete='CASCADE'), nullable=False)
    expires = Column(DateTime(timezone=True), nullable=False)

    user = relationship('UserDB', back_populates='sessions')

class FAQSectionDB(Base):
    __tablename__ = 'faq_section'
    __table_args__ = {'schema': settings.database.schema}

    id = Column(Integer, primary_key=True)
    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, ForeignKey(f'{settings.database.schema}.User.id', ondelete='SET NULL'), nullable=True)
    user = relationship('UserDB', back_populates='faq_sections')

    items = relationship('FAQItemDB', back_populates='section', order_by='FAQItemDB.order', cascade='all, delete-orphan')

class FAQItemDB(Base):
    __tablename__ = 'faq_item'
    __table_args__ = {'schema': settings.database.schema}

    id = Column(Integer, primary_key=True)
    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    faq_section_id = Column(Integer, ForeignKey(f'{settings.database.schema}.faq_section.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    section = relationship('FAQSectionDB', back_populates='items')


# Association table for many-to-many relationship between summaries and authors
summary_authors = Table(
    'summary_authors',
    Base.metadata,
    Column('summary_id', UUID(as_uuid=True), ForeignKey(f'{settings.database.schema}.summaries.id', ondelete='CASCADE'), primary_key=True),
    Column('author_id', UUID(as_uuid=True), ForeignKey(f'{settings.database.schema}.authors.id', ondelete='CASCADE'), primary_key=True),
    schema=settings.database.schema
)

class AuthorDB(Base):
    __tablename__ = 'authors'
    __table_args__ = {'schema': settings.database.schema}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    summaries = relationship('SummaryDB', secondary=summary_authors, back_populates='authors')
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)


class SourceDB(Base):
    __tablename__ = 'sources'
    __table_args__ = {'schema': settings.database.schema}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    
    url = Column(String(2083), nullable=True)  # Maximum URL length
    summary_id = Column(UUID(as_uuid=True), ForeignKey(f'{settings.database.schema}.summaries.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)

    summary = relationship('SummaryDB', back_populates='sources')

class SummaryDB(Base):
    __tablename__ = 'summaries'
    __table_args__ = (
        UniqueConstraint('title', 'user_id', name='uq_summary_title_user'),
        {'schema': settings.database.schema}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    title = Column(String(255), nullable=False)
    short_description = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Markdown formatted content
    status = Column(String(50), nullable=False, default='draft')  # e.g., draft, published
    is_deleted = Column(Boolean, nullable=False, default=False)
    user_id = Column(String(255), ForeignKey(f'{settings.database.schema}.User.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    authors = relationship('AuthorDB', secondary=summary_authors, back_populates='summaries')
    user = relationship('UserDB')  # Assuming a User model exists
    sources = relationship('SourceDB', back_populates='summary', cascade='all, delete-orphan')

# Async engine and session creation
# DATABASE_URL = os.environ.get("DATABASE_URL_ASYNCPG")  
DATABASE_URL = get_settings().sqlalchemy_database_uri.render_as_string(hide_password=False)
print(DATABASE_URL)
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
