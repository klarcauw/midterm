
from getpass import getpass

from backend.database import SessionLocal
from backend.models import User
from backend.auth import hash_password


db = SessionLocal()

try:
    username = input("Editor username: ")
    password = getpass("Editor password: ")

    existing = db.query(User).filter(
        User.username == username
    ).first()

    if existing:
        print("Username already exists.")

    elif len(password) < 8:
        print("Password must be at least 8 characters.")

    else:
        editor = User(
            username=username,
            password=hash_password(password),
            role="editor"
        )

        db.add(editor)
        db.commit()

        print("Editor account created successfully!")

finally:
    db.close()
