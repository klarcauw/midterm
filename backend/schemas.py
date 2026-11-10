
from pydantic import BaseModel, ConfigDict
from typing import Optional


# USER
class UserRegister(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ARTICLE
class ArticleCreate(BaseModel):
    title: str
    content: str
    category_id: int


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    article_id: int
    author_id: int
    category_id: int
    title: str
    content: str
    status: str


# REVIEW
class ReviewAction(BaseModel):
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
    article_id: int
    editor_id: int
    comment: Optional[str]
    decision: str
