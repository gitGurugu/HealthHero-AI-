from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib
from pydantic import BaseModel, EmailStr

from app.services import user_service
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core import security
from app.db.session import get_db

router = APIRouter()

# 用于注册的请求模型
class UserCreateIn(BaseModel):
    email: EmailStr
    username: str
    password: str
    # 如果有额外字段（如 is_superuser），需要修改数据库模型，否则这里可忽略

# 用于登录的请求模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/", response_model=UserOut, summary="用户注册")
def register(user_in: UserCreateIn, db: Session = Depends(get_db)):
    """
    用户注册端点  
    检查用户是否存在（根据 email 查找），若不存在则创建用户  
    """
    if user_service.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在"
        )
    # 将注册请求转换为 UserCreate 对象
    user_create = UserCreate(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password
    )
    db_user = user_service.create_user(db, obj_in=user_create)
    return db_user

@router.post("/login", response_model=Token, summary="用户登录")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录端点  
    根据传入的 email 与 password 验证用户，验证成功返回 JWT 令牌  
    """
    db_user = user_service.get_user_by_email(db, email=user_login.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的凭证"
        )
    password_hash = hashlib.sha256(user_login.password.encode()).hexdigest()
    if password_hash != db_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的凭证"
        )
    access_token = security.create_access_token(subject=db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}