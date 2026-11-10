
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import engine, SessionLocal, Base
from backend.models import Category

from backend.routers import users, articles, reviews

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Submission Review System API",
    description="API for authors and editors",
    version="1.0.0"
)

# Allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(reviews.router)


# Insert default categories
@app.on_event("startup")
def seed_categories():
    db: Session = SessionLocal()

    try:
        categories = [
            "Technology",
            "Education",
            "Lifestyle",
            "Business",
            "Science"
        ]

        for name in categories:
            exists = db.query(Category).filter(
                Category.category_name == name
            ).first()

            if not exists:
                db.add(Category(category_name=name))

        db.commit()

    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Submission Review System API is running!"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
