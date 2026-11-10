
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Article, Review, User
from backend.schemas import ArticleOut, ReviewAction, ReviewOut
from backend.auth import require_role

router = APIRouter(prefix="/api/editor/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ArticleOut])
def get_pending_articles(
    editor: User = Depends(require_role("editor")),
    db: Session = Depends(get_db)
):
    return db.query(Article).filter(
        Article.status == "under_review"
    ).order_by(Article.created_at.asc()).all()


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(
    article_id: int,
    editor: User = Depends(require_role("editor")),
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(
        Article.article_id == article_id,
        Article.status == "under_review"
    ).first()

    if not article:
        raise HTTPException(404, "Pending article not found")

    return article


@router.get("/{article_id}/history", response_model=list[ReviewOut])
def get_review_history(
    article_id: int,
    editor: User = Depends(require_role("editor")),
    db: Session = Depends(get_db)
):
    return db.query(Review).filter(
        Review.article_id == article_id
    ).order_by(Review.reviewed_at.desc()).all()


def process_review(
    article_id,
    decision,
    data,
    editor,
    db
):
    article = db.query(Article).filter(
        Article.article_id == article_id,
        Article.status == "under_review"
    ).first()

    if not article:
        raise HTTPException(
            404,
            "Pending article not found"
        )

    review = Review(
        article_id=article_id,
        editor_id=editor.user_id,
        comment=data.comment,
        decision=decision
    )

    article.status = (
        "approved" if decision == "approved" else "editing"
    )

    db.add(review)
    db.commit()
    db.refresh(article)

    return article


@router.post("/{article_id}/approve", response_model=ArticleOut)
def approve_article(
    article_id: int,
    data: ReviewAction,
    editor: User = Depends(require_role("editor")),
    db: Session = Depends(get_db)
):
    return process_review(
        article_id, "approved", data, editor, db
    )


@router.post("/{article_id}/return", response_model=ArticleOut)
def return_article(
    article_id: int,
    data: ReviewAction,
    editor: User = Depends(require_role("editor")),
    db: Session = Depends(get_db)
):
    return process_review(
        article_id, "returned", data, editor, db
    )
