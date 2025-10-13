#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yulong
@Date: 2025/10/13
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import os
from functools import wraps
from services.user_service import user_service
from models.user import UserInDB, UserCreate, UserResponse

load_dotenv(".env")

app = FastAPI()

# 配置模板
templates = Jinja2Templates(directory="templates")

# CORS配置
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
SECRET_KEY = os.getenv('SECRET_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

# 简单的内存会话存储（生产环境建议使用Redis或数据库）
sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic模型
class GoogleAuthRequest(BaseModel):
    token: str

class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = ""

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserInfo] = None
    error: Optional[str] = None

class RequestData(BaseModel):
    channel_id: str

# 会话管理函数
def get_session_id(request: Request) -> str:
    """从请求中获取或创建会话ID"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    return session_id

def get_current_user(request: Request) -> Optional[UserInfo]:
    """获取当前登录用户"""
    session_id = get_session_id(request)
    session_data = sessions.get(session_id)
    if session_data and 'user' in session_data:
        return UserInfo(**session_data['user'])
    return None

def login_required(request: Request):
    """登录验证装饰器"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录才能访问此页面"
        )
    return user

# 路由实现
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "client_id": GOOGLE_CLIENT_ID
    })

@app.post("/auth/google", response_model=AuthResponse)
async def auth_google(request: Request, response: Response, auth_data: GoogleAuthRequest):
    """Google OAuth2认证"""
    try:
        # 验证Google ID token
        idinfo = id_token.verify_oauth2_token(
            auth_data.token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # 创建用户数据
        user_create = UserCreate(
            google_id=idinfo['sub'],
            name=idinfo['name'],
            email=idinfo['email'],
            picture=idinfo.get('picture', '')
        )
        
        # 保存或更新用户到数据库
        db_user = user_service.create_user(user_create)
        
        if not db_user:
            return AuthResponse(success=False, error="用户创建失败")
        
        # 创建会话用户信息
        user_info = UserInfo(
            id=str(db_user.id),
            name=db_user.name,
            email=db_user.email,
            picture=db_user.picture or ""
        )
        
        # 保存用户信息到会话
        session_id = get_session_id(request)
        sessions[session_id] = {
            'user': user_info.dict(),
            'db_user_id': str(db_user.id)
        }
        
        # 设置Cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=3600 * 24,  # 24小时
            httponly=True,
            secure=False  # 在HTTPS环境中应设置为True
        )
        
        return AuthResponse(success=True, user=user_info)
        
    except ValueError as e:
        return AuthResponse(success=False, error=str(e))
    except Exception as e:
        return AuthResponse(success=False, error=f"认证过程中出现错误: {str(e)}")

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: UserInfo = Depends(login_required)):
    """用户资料页面"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@app.get("/logout")
async def logout(request: Request, response: Response):
    """退出登录"""
    session_id = get_session_id(request)
    if session_id in sessions:
        del sessions[session_id]
    
    # 清除Cookie
    response.delete_cookie(key="session_id")
    
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# 新增的用户管理API端点
@app.get("/api/user/profile", response_model=UserResponse)
async def get_user_profile(request: Request, user: UserInfo = Depends(login_required)):
    """获取当前用户详细信息"""
    session_id = get_session_id(request)
    session_data = sessions.get(session_id, {})
    db_user_id = session_data.get('db_user_id')
    
    if not db_user_id:
        raise HTTPException(status_code=404, detail="用户信息未找到")
    
    db_user = user_service.get_user_by_id(db_user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=str(db_user.id),
        google_id=db_user.google_id,
        name=db_user.name,
        email=db_user.email,
        picture=db_user.picture,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
        last_login=db_user.last_login,
        login_count=db_user.login_count,
        is_active=db_user.is_active
    )

@app.get("/api/user/stats")
async def get_user_stats():
    """获取用户统计信息（管理员功能）"""
    stats = user_service.get_user_stats()
    return stats

@app.get("/api/users")
async def get_users(skip: int = 0, limit: int = 100):
    """获取用户列表（管理员功能）"""
    users = user_service.get_all_users(skip=skip, limit=limit)
    return [UserResponse(
        id=str(user.id),
        google_id=user.google_id,
        name=user.name,
        email=user.email,
        picture=user.picture,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        login_count=user.login_count,
        is_active=user.is_active
    ) for user in users]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

