
from getpass import getpass

from backend.database import SessionLocal
from backend.models import User
from backend.auth import hash_password


def create_editor():
    db = SessionLocal()

    try:
        print("=== CREATE EDITOR ACCOUNT ===")

        username = input("Editor username: ").strip()
        password = getpass("Editor password: ")
        confirm_password = getpass("Confirm password: ")

        if not username or not password:
            print("Username and password cannot be empty.")
            return

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        existing_user = db.query(User).filter(
            User.username == username
        ).first()

        if existing_user:
            print("Username already exists.")
            return

        editor = User(
            username=username,
            password=hash_password(password),
            role="editor"
        )

        db.add(editor)
        db.commit()

        print("\nEditor account created successfully!")
        print("Username:", username)
        print("Role: editor")

    except Exception as e:
        db.rollback()
        print("\nError creating editor:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_editor()
