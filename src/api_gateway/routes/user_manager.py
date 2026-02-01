# -*- coding: utf-8 -*-
"""
User Manager API routes - 用户管理API
功能：用户列表、用户详情、添加用户、删除用户、修改用户信息
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr, validator

from src.api_gateway.db.database import get_db
from src.api_gateway.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/db-manager/users", tags=["user-manager"])


# ========== Pydantic Models ==========

class UserItem(BaseModel):
    """用户信息项"""
    id: str
    username: str
    email: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str
    email: EmailStr
    password: str

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('用户名长度至少为3个字符')
        if len(v.strip()) > 20:
            raise ValueError('用户名长度不能超过20个字符')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('密码长度至少为6个字符')
        return v


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v.strip()) < 3:
                raise ValueError('用户名长度至少为3个字符')
            if len(v.strip()) > 20:
                raise ValueError('用户名长度不能超过20个字符')
            return v.strip()
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('密码长度至少为6个字符')
        return v


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: str
    created_at: str
    updated_at: str


# ========== 辅助函数 ==========

def hash_password(password: str) -> str:
    """简单密码哈希（生产环境应使用 bcrypt）"""
    # TODO: 使用 bcrypt 进行密码哈希
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


# ========== API 端点 ==========

@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = 1,
    page_size: int = 20,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）

    参数：
    - page: 页码（从1开始）
    - page_size: 每页数量（10/20/50）

    返回用户列表，包含：id, username, email, created_at, updated_at
    """
    try:
        # 计算总数
        total = db.query(User).count()

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        # 限制分页参数范围
        page = max(1, min(page, total_pages))
        page_size = max(10, min(page_size, 100))

        # 查询用户列表
        offset = (page - 1) * page_size
        users = (
            db.query(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        items = []
        for user in users:
            items.append(UserItem(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
                updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
            ))

        return UserListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取单个用户详情
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    创建新用户

    参数：
    - username: 用户名（3-20个字符）
    - email: 邮箱地址
    - password: 密码（至少6个字符）
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")

        # 创建新用户
        new_user = User(
            id=str(uuid.uuid4()),
            username=request.username,
            email=request.email,
            password=hash_password(request.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"创建用户成功: {new_user.username}")

        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            created_at=new_user.created_at.strftime("%Y-%m-%d %H:%M:%S") if new_user.created_at else "",
            updated_at=new_user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if new_user.updated_at else ""
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    删除用户

    删除后该用户无法再登录系统
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        username = user.username
        db.delete(user)
        db.commit()

        logger.info(f"删除用户成功: {username}")

        return {
            "success": True,
            "message": f"用户 '{username}' 已删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    修改用户信息

    可修改字段：
    - username: 用户名（可选）
    - email: 邮箱（可选）
    - password: 密码（可选，留空表示不修改）

    注意：
    - 用户名和邮箱必须唯一（排除当前用户自身）
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新用户名
        if request.username is not None:
            # 检查用户名是否被其他用户使用
            existing_user = db.query(User).filter(
                User.username == request.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已被使用")
            user.username = request.username

        # 更新邮箱
        if request.email is not None:
            # 检查邮箱是否被其他用户使用
            existing_email = db.query(User).filter(
                User.email == request.email,
                User.id != user_id
            ).first()
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱已被使用")
            user.email = request.email

        # 更新密码
        if request.password is not None and request.password.strip():
            user.password = hash_password(request.password)

        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)

        logger.info(f"更新用户成功: {user.username}")

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else ""
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")
