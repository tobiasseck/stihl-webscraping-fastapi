from sqlmodel import Session, select
from app.models.database import engine
from app.models.user import User
from app.auth import get_password_hash

def reset_password(username: str, new_password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user:
            user.hashed_password = get_password_hash(new_password)
            session.add(user)
            session.commit()
            print(f"Password reset successfully for user: {username}")
        else:
            print(f"User not found: {username}")

if __name__ == "__main__":
    username = input("Enter username: ")
    new_password = input("Enter new password: ")
    reset_password(username, new_password)