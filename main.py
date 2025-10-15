#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: yulong
@Date: 2025/10/13
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import os
from functools import wraps
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.user_service import user_service
from services.consultation_service import consultation_service
from services.payment_service import payment_service
from services.doctor_service import doctor_service
from models.user import UserInDB, UserCreate, UserResponse
from models.doctor import DoctorInDB, DoctorCreate, DoctorResponse, DoctorEarnings, DoctorStatus
from models.consultation import (
    ConsultationCreate, ConsultationResponse, PaymentOrderResponse,
    ChatMessageResponse, ConsultationMode, DoctorLevel
)

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

# 创建调度器
scheduler = AsyncIOScheduler()

async def check_unassigned_consultations():
    """检查未分配的咨询并尝试分配"""
    try:
        print("开始检查未分配的咨询...")
        # 获取支付成功但未分配的咨询
        unassigned_consultations = consultation_service.get_unassigned_consultations(limit=20)
        
        if not unassigned_consultations:
            print("没有未分配的咨询")
            return
        
        print(f"发现 {len(unassigned_consultations)} 个未分配的咨询")
        
        for consultation in unassigned_consultations:
            print(f"尝试分配咨询: {consultation['id']}")
            success = consultation_service.auto_assign_doctor(consultation['id'])
            if success:
                print(f"✅ 成功分配咨询: {consultation['id']}")
            else:
                print(f"❌ 分配失败，咨询: {consultation['id']}")
                
    except Exception as e:
        print(f"检查未分配咨询时出错: {e}")

# Pydantic模型
class GoogleAuthRequest(BaseModel):
    token: str
    user_info: Optional[dict] = None

class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = ""

class DoctorInfo(BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = ""
    license_number: str
    hospital: str
    department: str
    level: str
    status: str

class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserInfo] = None
    doctor: Optional[DoctorInfo] = None
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

def get_current_doctor(request: Request) -> Optional[DoctorInfo]:
    """获取当前登录医生"""
    session_id = get_session_id(request)
    session_data = sessions.get(session_id)
    if session_data and 'doctor' in session_data:
        return DoctorInfo(**session_data['doctor'])
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

def doctor_login_required(request: Request):
    """医生登录验证装饰器"""
    doctor = get_current_doctor(request)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要医生登录才能访问此页面"
        )
    return doctor

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
        print(f"开始创建/更新用户: {user_create.email}")
        db_user = user_service.create_user(user_create)
        
        if not db_user:
            print(f"用户创建失败: {user_create.email}")
            return AuthResponse(success=False, error="用户创建失败")
        
        print(f"用户创建/更新成功: {db_user.email}, ID: {db_user.id}")
        
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

@app.post("/auth/doctor/google", response_model=AuthResponse)
async def auth_doctor_google(request: Request, response: Response, auth_data: GoogleAuthRequest):
    """医生Google OAuth2认证"""
    try:
        # 如果提供了用户信息，直接使用
        if auth_data.user_info:
            idinfo = auth_data.user_info
        else:
            # 否则尝试验证token
            try:
                idinfo = id_token.verify_oauth2_token(
                    auth_data.token, 
                    requests.Request(), 
                    GOOGLE_CLIENT_ID
                )
            except:
                # 如果token验证失败，尝试作为访问令牌使用
                import requests as http_requests
                user_info_response = http_requests.get(
                    f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={auth_data.token}'
                )
                if user_info_response.status_code == 200:
                    idinfo = user_info_response.json()
                else:
                    return AuthResponse(success=False, error="无效的访问令牌")
        
        # 检查是否已存在医生记录
        existing_doctor = doctor_service.get_doctor_by_google_id(idinfo['sub'])
        if not existing_doctor:
            return AuthResponse(success=False, error="医生账户不存在，请联系管理员注册")
        
        # 更新医生登录信息
        updated_doctor = doctor_service.update_doctor_login(str(existing_doctor.id))
        if not updated_doctor:
            return AuthResponse(success=False, error="医生登录失败")
        
        # 创建会话医生信息
        doctor_info = DoctorInfo(
            id=str(updated_doctor.id),
            name=updated_doctor.name,
            email=updated_doctor.email,
            picture=updated_doctor.picture or "",
            license_number=updated_doctor.license_number,
            hospital=updated_doctor.hospital,
            department=updated_doctor.department,
            level=updated_doctor.level.value,
            status=updated_doctor.status.value
        )
        
        # 保存医生信息到会话
        session_id = get_session_id(request)
        sessions[session_id] = {
            'doctor': doctor_info.dict(),
            'db_doctor_id': str(updated_doctor.id)
        }
        
        # 设置Cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=3600 * 24,  # 24小时
            httponly=True,
            secure=False  # 在HTTPS环境中应设置为True
        )
        
        return AuthResponse(success=True, doctor=doctor_info)
        
    except ValueError as e:
        return AuthResponse(success=False, error=str(e))
    except Exception as e:
        return AuthResponse(success=False, error=f"医生认证过程中出现错误: {str(e)}")

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

# 医生端路由
@app.get("/doctor/login", response_class=HTMLResponse)
async def doctor_login(request: Request):
    """医生登录页面"""
    return templates.TemplateResponse("doctor_login_simple.html", {
        "request": request, 
        "client_id": GOOGLE_CLIENT_ID
    })

@app.get("/doctor/dashboard", response_class=HTMLResponse)
async def doctor_dashboard(request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """医生仪表板"""
    return templates.TemplateResponse("doctor_dashboard.html", {
        "request": request,
        "doctor": doctor
    })

@app.get("/doctor/consultations", response_class=HTMLResponse)
async def doctor_consultations(request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """医生咨询列表页面"""
    return templates.TemplateResponse("doctor_consultations.html", {
        "request": request,
        "doctor": doctor
    })

@app.get("/doctor/chat/{consultation_id}", response_class=HTMLResponse)
async def doctor_chat(request: Request, consultation_id: str, doctor: DoctorInfo = Depends(doctor_login_required)):
    """医生聊天页面"""
    return templates.TemplateResponse("doctor_chat.html", {
        "request": request,
        "doctor": doctor,
        "consultation_id": consultation_id
    })

@app.get("/doctor/earnings", response_class=HTMLResponse)
async def doctor_earnings(request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """医生收入页面"""
    return templates.TemplateResponse("doctor_earnings.html", {
        "request": request,
        "doctor": doctor
    })

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

# 医疗咨询相关API端点

@app.get("/consultation", response_class=HTMLResponse)
async def consultation_page(request: Request, user: UserInfo = Depends(login_required)):
    """患者咨询页面"""
    return templates.TemplateResponse("consultation.html", {
        "request": request,
        "user": user
    })

@app.get("/consultation/history", response_class=HTMLResponse)
async def consultation_history_page(request: Request, user: UserInfo = Depends(login_required)):
    """患者历史咨询页面"""
    return templates.TemplateResponse("consultation_history.html", {
        "request": request,
        "user": user
    })

@app.get("/consultation/detail/{consultation_id}", response_class=HTMLResponse)
async def consultation_detail_page(consultation_id: str, request: Request, user: UserInfo = Depends(login_required)):
    """咨询详情页面"""
    return templates.TemplateResponse("consultation_detail.html", {
        "request": request,
        "user": user,
        "consultation_id": consultation_id
    })

@app.get("/api/consultation/packages")
async def get_consultation_packages():
    """获取咨询套餐列表"""
    packages = consultation_service.get_consultation_packages()
    return [package.dict() for package in packages]

@app.post("/api/consultation/create")
async def create_consultation(
    request: Request,
    mode: str = Form(...),
    disease_description: str = Form(...),
    symptoms: Optional[str] = Form(None),
    medical_history: Optional[str] = Form(None),
    doctor_level: Optional[str] = Form(None),
    attachments: List[UploadFile] = File(default=[])
):
    """创建医疗咨询"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 处理文件上传 - 支持多次上传，文件叠加而不是覆盖
    attachment_paths = []
    
    # 确保uploads目录存在
    import os
    os.makedirs("uploads", exist_ok=True)
    
    for file in attachments:
        if file.filename:
            try:
                # 生成唯一文件名，包含时间戳避免冲突
                import uuid
                from datetime import datetime
                file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
                file_path = f"uploads/{unique_filename}"
                
                # 保存文件到服务器
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                attachment_paths.append(file_path)
                print(f"文件上传成功: {file.filename} -> {file_path}")
            except Exception as e:
                print(f"文件上传失败: {file.filename}, 错误: {e}")
                # 即使文件上传失败，也继续处理其他文件
    
    # 创建咨询数据
    consultation_data = ConsultationCreate(
        mode=ConsultationMode(mode),
        disease_description=disease_description,
        symptoms=symptoms,
        medical_history=medical_history,
        attachments=attachment_paths,
        doctor_level=DoctorLevel(doctor_level) if doctor_level else None
    ) 
    
    try:
        print(f"开始创建咨询记录，用户ID: {user.id}, 类型: {type(user.id)}")
        print(f"咨询数据: {consultation_data}")
        
        # 确保user.id是字符串
        user_id = str(user.id)
        print(f"转换后的用户ID: {user_id}")
        
        # 创建咨询记录
        consultation = consultation_service.create_consultation(user_id, consultation_data)
        
        print(f"咨询服务返回结果: {consultation}")
        
        if not consultation:
            print("❌ 咨询记录创建失败，返回None")
            return {
                "success": False,
                "error": "咨询记录创建失败"
            }
        
        # 创建支付订单
        payment_info = payment_service.create_payment_order(
            consultation_id=str(consultation.id),
            user_id=user_id
        )
        
        return {
            "success": True,
            "consultation_id": str(consultation.id),
            "payment_info": payment_info
        }
    except Exception as e:
        print(f"创建咨询时出错: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/consultation/{consultation_id}")
async def get_consultation(consultation_id: str, request: Request):
    """获取咨询详情"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    return ConsultationResponse(
        id=str(consultation.id),
        user_id=consultation.user_id,
        mode=consultation.mode,
        disease_description=consultation.disease_description,
        symptoms=consultation.symptoms,
        medical_history=consultation.medical_history,
        attachments=consultation.attachments,
        package_id=consultation.package_id,
        doctor_level=consultation.doctor_level,
        status=consultation.status,
        assigned_doctor_id=consultation.assigned_doctor_id,
        price_usdt=consultation.price_usdt,
        payment_order_id=consultation.payment_order_id,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at,
        started_at=consultation.started_at,
        completed_at=consultation.completed_at
    )

@app.get("/api/consultation/user/list")
async def get_user_consultations(request: Request, skip: int = 0, limit: int = 20):
    """获取用户的咨询列表"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    consultations = consultation_service.get_user_consultations(user.id, skip, limit)
    return [ConsultationResponse(
        id=str(consultation.id),
        user_id=consultation.user_id,
        mode=consultation.mode,
        disease_description=consultation.disease_description,
        symptoms=consultation.symptoms,
        medical_history=consultation.medical_history,
        attachments=consultation.attachments,
        package_id=consultation.package_id,
        doctor_level=consultation.doctor_level,
        status=consultation.status,
        assigned_doctor_id=consultation.assigned_doctor_id,
        price_usdt=consultation.price_usdt,
        payment_order_id=consultation.payment_order_id,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at,
        started_at=consultation.started_at,
        completed_at=consultation.completed_at
    ) for consultation in consultations]

@app.get("/api/payment/status/{consultation_id}")
async def check_payment_status(consultation_id: str, request: Request):
    """检查支付状态"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    try:
        status_info = payment_service.check_payment_status(consultation_id)
        
        # 如果支付成功，触发自动分配医生
        if status_info.get("status") == "paid":
            print(f"支付成功，开始自动分配医生到咨询 {consultation_id}")
            assignment_success = consultation_service.auto_assign_doctor(consultation_id)
            if assignment_success:
                status_info["assignment"] = "医生已自动分配"
                print(f"咨询 {consultation_id} 医生分配成功")
            else:
                status_info["assignment"] = "暂无可用医生，系统将稍后自动分配"
                print(f"咨询 {consultation_id} 医生分配失败，将稍后重试")
        
        return status_info
    except Exception as e:
        print(f"检查支付状态时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultation/{consultation_id}/messages")
async def get_chat_messages(consultation_id: str, request: Request, skip: int = 0, limit: int = 50):
    """获取聊天消息"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 验证用户权限
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    messages = consultation_service.get_chat_messages(consultation_id, skip, limit)
    return [ChatMessageResponse(
        id=str(message.id),
        consultation_id=message.consultation_id,
        sender_id=message.sender_id,
        sender_type=message.sender_type,
        message=message.message,
        message_type=message.message_type,
        attachments=message.attachments,
        created_at=message.created_at
    ) for message in messages]

@app.post("/api/consultation/{consultation_id}/send-message")
async def send_chat_message(
    consultation_id: str,
    request: Request,
    message_data: dict
):
    """发送聊天消息"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 验证用户权限
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    try:
        message = consultation_service.send_chat_message(
            consultation_id=consultation_id,
            sender_id=user.id,
            sender_type="user",
            message=message_data["message"],
            message_type=message_data.get("message_type", "text"),
            attachments=message_data.get("attachments", [])
        )
        
        return {
            "success": True,
            "message": ChatMessageResponse(
                id=str(message.id),
                consultation_id=message.consultation_id,
                sender_id=message.sender_id,
                sender_type=message.sender_type,
                message=message.message,
                message_type=message.message_type,
                attachments=message.attachments,
                created_at=message.created_at
            )
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/consultation/{consultation_id}/end")
async def end_consultation(consultation_id: str, request: Request):
    """结束咨询"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 验证用户权限
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    try:
        from models.consultation import ConsultationStatus
        consultation_service.update_consultation_status(
            consultation_id, 
            ConsultationStatus.COMPLETED
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/consultation/{consultation_id}/feedback")
async def get_doctor_feedback(consultation_id: str, request: Request):
    """获取医生反馈"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 验证用户权限
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    try:
        # 这里应该从数据库获取医生反馈
        # 暂时返回模拟数据
        feedback = {
            "id": "feedback_123",
            "consultation_id": consultation_id,
            "doctor_id": consultation.assigned_doctor_id or "doctor_001",
            "doctor_name": "张医生",
            "title": "诊断报告",
            "content": "根据您提供的症状描述和检查结果，初步诊断为...",
            "recommendations": [
                "建议多休息，避免过度劳累",
                "按时服药，注意饮食清淡",
                "如有不适请及时就医"
            ],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
        
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultation/{consultation_id}/report")
async def download_consultation_report(consultation_id: str, request: Request):
    """下载咨询报告"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 验证用户权限
    consultation = consultation_service.get_consultation_by_id(consultation_id)
    if not consultation or consultation.user_id != user.id:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    
    if consultation.status != "completed":
        raise HTTPException(status_code=400, detail="咨询尚未完成，无法下载报告")
    
    try:
        # 这里应该生成PDF报告
        # 暂时返回模拟数据
        from fastapi.responses import JSONResponse
        
        report_data = {
            "consultation_id": consultation_id,
            "patient_name": user.name,
            "consultation_date": consultation.created_at.isoformat(),
            "doctor_level": consultation.doctor_level,
            "disease_description": consultation.disease_description,
            "symptoms": consultation.symptoms,
            "medical_history": consultation.medical_history,
            "doctor_feedback": "根据您提供的症状描述和检查结果，初步诊断为...",
            "recommendations": [
                "建议多休息，避免过度劳累",
                "按时服药，注意饮食清淡",
                "如有不适请及时就医"
            ]
        }
        
        return JSONResponse(content=report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/test/{consultation_id}")
async def test_payment_success(consultation_id: str, request: Request):
    """测试支付成功（仅用于测试）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    try:
        # 模拟支付成功
        from models.consultation import PaymentStatus, ConsultationStatus
        consultation_service.update_payment_status(
            consultation_id, 
            PaymentStatus.PAID, 
            "test_transaction_hash_12345"
        )
        consultation_service.update_consultation_status(
            consultation_id, 
            ConsultationStatus.PAID
        )
        return {"success": True, "message": "测试支付成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 医生端API端点

@app.get("/api/doctor/profile", response_model=DoctorResponse)
async def get_doctor_profile(request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """获取当前医生详细信息"""
    session_id = get_session_id(request)
    session_data = sessions.get(session_id, {})
    db_doctor_id = session_data.get('db_doctor_id')
    
    if not db_doctor_id:
        raise HTTPException(status_code=404, detail="医生信息未找到")
    
    db_doctor = doctor_service.get_doctor_by_id(db_doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="医生不存在")
    
    return DoctorResponse(
        id=str(db_doctor.id),
        google_id=db_doctor.google_id,
        name=db_doctor.name,
        email=db_doctor.email,
        picture=db_doctor.picture,
        license_number=db_doctor.license_number,
        hospital=db_doctor.hospital,
        department=db_doctor.department,
        specialties=db_doctor.specialties,
        level=db_doctor.level,
        experience_years=db_doctor.experience_years,
        introduction=db_doctor.introduction,
        consultation_fee=db_doctor.consultation_fee,
        status=db_doctor.status,
        total_consultations=db_doctor.total_consultations,
        current_consultation_count=db_doctor.current_consultation_count,
        total_earnings=db_doctor.total_earnings,
        rating=db_doctor.rating,
        rating_count=db_doctor.rating_count,
        created_at=db_doctor.created_at,
        updated_at=db_doctor.updated_at,
        last_login=db_doctor.last_login,
        login_count=db_doctor.login_count,
        is_active=db_doctor.is_active
    )

@app.get("/api/doctor/consultations")
async def get_doctor_consultations(request: Request, doctor: DoctorInfo = Depends(doctor_login_required), skip: int = 0, limit: int = 20):
    """获取医生的咨询列表"""
    consultations = doctor_service.get_doctor_consultations(doctor.id, skip, limit)
    return consultations

@app.get("/api/doctor/earnings", response_model=DoctorEarnings)
async def get_doctor_earnings(request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """获取医生收入统计"""
    earnings = doctor_service.get_doctor_earnings(doctor.id)
    if not earnings:
        raise HTTPException(status_code=404, detail="收入信息未找到")
    return earnings

@app.post("/api/doctor/status")
async def update_doctor_status(request: Request, status_data: dict, doctor: DoctorInfo = Depends(doctor_login_required)):
    """更新医生状态"""
    try:
        new_status = DoctorStatus(status_data.get("status"))
        success = doctor_service.set_doctor_status(doctor.id, new_status)
        if success:
            return {"success": True, "message": "状态更新成功"}
        else:
            return {"success": False, "error": "状态更新失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/doctor/assign/{consultation_id}")
async def assign_doctor_to_consultation(consultation_id: str, request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """分配医生到咨询"""
    try:
        # 检查咨询是否存在且未分配
        consultation = consultation_service.get_consultation_by_id(consultation_id)
        if not consultation:
            return {"success": False, "error": "咨询不存在"}
        
        if consultation.assigned_doctor_id:
            return {"success": False, "error": "咨询已分配给其他医生"}
        
        # 分配医生
        success = doctor_service.assign_doctor_to_consultation(doctor.id, consultation_id)
        if success:
            # 更新咨询状态
            consultation_service.update_consultation_status(
                consultation_id, 
                ConsultationStatus.IN_PROGRESS
            )
            return {"success": True, "message": "分配成功"}
        else:
            return {"success": False, "error": "分配失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/doctor/consultation/{consultation_id}/send-message")
async def send_doctor_message(
    consultation_id: str,
    request: Request,
    message_data: dict,
    doctor: DoctorInfo = Depends(doctor_login_required)
):
    """医生发送聊天消息"""
    try:
        # 验证医生是否有权限访问此咨询
        consultations = doctor_service.get_doctor_consultations(doctor.id)
        consultation_ids = [c["id"] for c in consultations]
        if consultation_id not in consultation_ids:
            return {"success": False, "error": "无权限访问此咨询"}
        
        message = consultation_service.send_chat_message(
            consultation_id=consultation_id,
            sender_id=doctor.id,
            sender_type="doctor",
            message=message_data["message"],
            message_type=message_data.get("message_type", "text"),
            attachments=message_data.get("attachments", [])
        )
        
        return {
            "success": True,
            "message": ChatMessageResponse(
                id=str(message.id),
                consultation_id=message.consultation_id,
                sender_id=message.sender_id,
                sender_type=message.sender_type,
                message=message.message,
                message_type=message.message_type,
                attachments=message.attachments,
                created_at=message.created_at
            )
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/doctor/consultation/{consultation_id}/complete")
async def complete_consultation(consultation_id: str, request: Request, doctor: DoctorInfo = Depends(doctor_login_required)):
    """完成咨询"""
    try:
        # 验证医生是否有权限访问此咨询
        consultations = doctor_service.get_doctor_consultations(doctor.id)
        consultation_ids = [c["id"] for c in consultations]
        if consultation_id not in consultation_ids:
            return {"success": False, "error": "无权限访问此咨询"}
        
        # 更新咨询状态为已完成
        consultation_service.update_consultation_status(
            consultation_id, 
            ConsultationStatus.COMPLETED
        )
        
        # 更新医生状态为活跃
        doctor_service.set_doctor_status(doctor.id, DoctorStatus.ACTIVE)
        
        # 更新医生收入（这里需要根据实际业务逻辑计算）
        consultation = consultation_service.get_consultation_by_id(consultation_id)
        if consultation:
            doctor_service.update_doctor_earnings(doctor.id, consultation.price_usdt)
        
        return {"success": True, "message": "咨询已完成"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/trigger-assignment")
async def trigger_assignment_check(request: Request):
    """手动触发分配检查（管理员功能）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    try:
        print("手动触发分配检查...")
        await check_unassigned_consultations()
        return {"success": True, "message": "分配检查已触发"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("启动定时任务...")
    # 添加定时任务（每5分钟检查一次未分配的咨询）
    scheduler.add_job(
        check_unassigned_consultations,
        trigger=IntervalTrigger(minutes=5),
        id='check_unassigned_consultations',
        name='检查未分配咨询',
        replace_existing=True
    )
    scheduler.start()
    print("✅ 定时任务已启动")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("停止定时任务...")
    scheduler.shutdown()
    print("✅ 定时任务已停止")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

