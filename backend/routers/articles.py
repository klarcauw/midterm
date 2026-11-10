
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Article, User, Category
from backend.schemas import ArticleCreate, ArticleUpdate, ArticleOut
from backend.auth import require_role

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("/my", response_model=list[ArticleOut])
def get_my_articles(
    user: User = Depends(require_role("author")),
    db: Session = Depends(get_db)
):
    return db.query(Article).filter(
        Article.author_id == user.user_id
    ).order_by(Article.created_at.desc()).all()


@router.post("/", response_model=ArticleOut)
def create_article(
    data: ArticleCreate,
    user: User = Depends(require_role("author")),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.category_id == data.category_id
    ).first()

    if not category:
        raise HTTPException(404, "Category not found")

    article = Article(
        author_id=user.user_id,
        category_id=data.category_id,
        title=data.title,
        content=data.content,
        status="editing"
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    data: ArticleUpdate,
    user: User = Depends(require_role("author")),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(
        Article.article_id == article_id,
        Article.author_id == user.user_id
    ).first()

    if not article:
        raise HTTPException(404, "Article not found")

    if article.status != "editing":
        raise HTTPException(
            400,
            "Only editing articles can be modified"
        )

    updates = data.model_dump(exclude_unset=True)

    if "category_id" in updates:
        category = db.query(Category).filter(
            Category.category_id == updates["category_id"]
        ).first()

        if not category:
            raise HTTPException(404, "Category not found")

    for key, value in updates.items():
        setattr(article, key, value)

    db.commit()
    db.refresh(article)

    return article


@router.delete("/{article_id}")
def delete_article(
    article_id: int,
    user: User = Depends(require_role("author")),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(
        Article.article_id == article_id,
        Article.author_id == user.user_id
    ).first()

    if not article:
        raise HTTPException(404, "Article not found")

    if article.status != "editing":
        raise HTTPException(
            400,
            "Only editing articles can be deleted"
        )

    db.delete(article)
    db.commit()

    return {"message": "Article deleted successfully"}


@router.post("/{article_id}/submit", response_model=ArticleOut)
def submit_article(
    article_id: int,
    user: User = Depends(require_role("author")),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(
        Article.article_id == article_id,
        Article.author_id == user.user_id
    ).first()

    if not article:
        raise HTTPException(404, "Article not found")

    if article.status != "editing":
        raise HTTPException(
            400,
            "Article cannot be submitted in its current status"
        )

    article.status = "under_review"

    db.commit()
    db.refresh(article)

    return article
