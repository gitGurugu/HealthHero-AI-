import hashlib
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User:
    """
    根据 email 查找用户
    """
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: int) -> User:
    """
    根据用户ID获取用户
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    创建用户：存储 email、username 和经过 SHA256 处理的密码
    """
    password_hash = hashlib.sha256(obj_in.password.encode()).hexdigest()
    db_user = User(
        email=obj_in.email,
        username=obj_in.username,
        password_hash=password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user