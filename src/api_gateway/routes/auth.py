"""Authentication Routes"""
from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import jwt

from src.shared.common.config import settings
from src.api_gateway.db.database import get_db
from src.api_gateway.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=32)
    confirm_password: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class ProfileUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=32)


class ProfileResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


def hash_password(password: str) -> str:
    """简单密码哈希（生产环境应使用 bcrypt）"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    """Create JWT token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def user_to_dict(user: User) -> dict:
    """Convert User model to dictionary"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Validate password confirmation
    if request.password != request.confirm_password:
        return RegisterResponse(
            success=False,
            message="密码不一致",
            data=None
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        return RegisterResponse(
            success=False,
            message="邮箱已被注册",
            data=None
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        return RegisterResponse(
            success=False,
            message="用户名已存在",
            data=None
        )

    # Create new user
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()

    new_user = User(
        id=user_id,
        username=request.username,
        email=request.email,
        password=hash_password(request.password),
        created_at=now
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token
    token = create_token(user_id)

    return RegisterResponse(
        success=True,
        message="注册成功",
        data={
            "user": user_to_dict(new_user),
            "token": token
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        return LoginResponse(
            success=False,
            message="邮箱或密码错误",
            data=None
        )

    # Check password
    if not verify_password(request.password, user.password):
        return LoginResponse(
            success=False,
            message="邮箱或密码错误",
            data=None
        )

    # Generate token
    token = create_token(user.id)

    return LoginResponse(
        success=True,
        message="登录成功",
        data={
            "user": user_to_dict(user),
            "token": token
        }
    )


@router.get("/me")
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get current user info"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        return {
            "success": True,
            "data": {
                "user": user_to_dict(user)
            }
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except Exception:
        raise HTTPException(status_code=401, detail="无效的Token")


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        # Check if email is already used by another user
        existing_email = db.query(User).filter(
            User.email == request.email,
            User.id != user_id
        ).first()
        if existing_email:
            return ProfileResponse(
                success=False,
                message="邮箱已被使用",
                data=None
            )

        # Check if username is already used by another user
        existing_username = db.query(User).filter(
            User.username == request.username,
            User.id != user_id
        ).first()
        if existing_username:
            return ProfileResponse(
                success=False,
                message="用户名已存在",
                data=None
            )

        # Update user data
        user.username = request.username
        user.email = request.email
        db.commit()
        db.refresh(user)

        return ProfileResponse(
            success=True,
            message="更新成功",
            data={
                "user": user_to_dict(user)
            }
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"无效的Token: {str(e)}")


@router.put("/password", response_model=ProfileResponse)
async def update_password(
    request: PasswordUpdateRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Update user password"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        # Verify current password
        if user.password != request.current_password:
            return ProfileResponse(
                success=False,
                message="当前密码错误",
                data=None
            )

        # Update password
        user.password = request.new_password
        db.commit()

        return ProfileResponse(
            success=True,
            message="密码修改成功",
            data=None
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"无效的Token: {str(e)}")
