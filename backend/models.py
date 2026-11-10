
from sqlalchemy import (
    Column, Integer, String, Text,
    ForeignKey, DateTime, CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("Article", back_populates="author")

    __table_args__ = (
        CheckConstraint(
            "role IN ('author', 'editor')",
            name="valid_user_role"
        ),
    )


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False)

    articles = relationship("Article", back_populates="category")


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True, index=True)

    author_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    status = Column(String(30), default="editing", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    reviews = relationship("Review", back_populates="article")

    __table_args__ = (
        CheckConstraint(
            "status IN ('editing', 'under_review', 'approved')",
            name="valid_article_status"
        ),
    )


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)

    article_id = Column(
        Integer,
        ForeignKey("articles.article_id"),
        nullable=False
    )

    editor_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    comment = Column(Text)

    decision = Column(String(20), nullable=False)

    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    article = relationship("Article", back_populates="reviews")

    __table_args__ = (
        CheckConstraint(
            "decision IN ('approved', 'returned')",
            name="valid_review_decision"
        ),
    )
