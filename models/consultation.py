#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医疗咨询数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """自定义ObjectId类型用于Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return {"type": "string"}

class ConsultationMode(str, Enum):
    """咨询模式"""
    REALTIME = "realtime"  # 实时聊天
    ONETIME = "onetime"    # 一次性咨询

class DoctorLevel(str, Enum):
    """医生等级"""
    NORMAL = "normal"      # 普通医生
    SENIOR = "senior"      # 高级医生
    EXPERT = "expert"      # 专家医生

class ConsultationStatus(str, Enum):
    """咨询状态"""
    PENDING = "pending"        # 待支付
    PAID = "paid"             # 已支付
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"    # 已完成
    CANCELLED = "cancelled"    # 已取消

class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"    # 待支付
    PAID = "paid"         # 已支付
    FAILED = "failed"     # 支付失败
    EXPIRED = "expired"   # 已过期

class ConsultationPackage(BaseModel):
    """咨询套餐"""
    level: DoctorLevel = Field(..., description="医生等级")
    name: str = Field(..., description="套餐名称")
    price_usdt: float = Field(..., description="价格(USDT)")
    description: str = Field(..., description="套餐描述")
    features: List[str] = Field(..., description="套餐特性")
    response_time: str = Field(..., description="响应时间")
    consultation_duration: str = Field(..., description="咨询时长")

class ConsultationCreate(BaseModel):
    """创建咨询请求"""
    mode: ConsultationMode = Field(..., description="咨询模式")
    disease_description: str = Field(..., description="疾病描述")
    symptoms: Optional[str] = Field(None, description="症状描述")
    medical_history: Optional[str] = Field(None, description="病史")
    attachments: List[str] = Field(default=[], description="附件文件路径列表")
    package_id: Optional[str] = Field(None, description="咨询套餐ID（一次性咨询必填）")
    doctor_level: Optional[DoctorLevel] = Field(None, description="医生等级（一次性咨询必填）")

class ConsultationInDB(BaseModel):
    """数据库中的咨询记录"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="用户ID")
    mode: ConsultationMode = Field(..., description="咨询模式")
    disease_description: str = Field(..., description="疾病描述")
    symptoms: Optional[str] = Field(None, description="症状描述")
    medical_history: Optional[str] = Field(None, description="病史")
    attachments: List[str] = Field(default=[], description="附件文件路径列表")
    package_id: Optional[str] = Field(None, description="咨询套餐ID")
    doctor_level: Optional[DoctorLevel] = Field(None, description="医生等级")
    status: ConsultationStatus = Field(default=ConsultationStatus.PENDING, description="咨询状态")
    assigned_doctor_id: Optional[str] = Field(None, description="分配的医生ID")
    price_usdt: float = Field(..., description="价格(USDT)")
    payment_order_id: Optional[str] = Field(None, description="支付订单ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ConsultationResponse(BaseModel):
    """咨询响应模型"""
    id: str = Field(..., description="咨询ID")
    user_id: str = Field(..., description="用户ID")
    mode: ConsultationMode = Field(..., description="咨询模式")
    disease_description: str = Field(..., description="疾病描述")
    symptoms: Optional[str] = Field(None, description="症状描述")
    medical_history: Optional[str] = Field(None, description="病史")
    attachments: List[str] = Field(default=[], description="附件文件路径列表")
    package_id: Optional[str] = Field(None, description="咨询套餐ID")
    doctor_level: Optional[DoctorLevel] = Field(None, description="医生等级")
    status: ConsultationStatus = Field(..., description="咨询状态")
    assigned_doctor_id: Optional[str] = Field(None, description="分配的医生ID")
    price_usdt: float = Field(..., description="价格(USDT)")
    payment_order_id: Optional[str] = Field(None, description="支付订单ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        from_attributes = True

class PaymentOrder(BaseModel):
    """支付订单"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    consultation_id: str = Field(..., description="咨询ID")
    user_id: str = Field(..., description="用户ID")
    amount_usdt: float = Field(..., description="支付金额(USDT)")
    usdt_address: str = Field(..., description="收款USDT(TRC20)地址")
    qr_code_url: str = Field(..., description="二维码URL")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="支付状态")
    transaction_hash: Optional[str] = Field(None, description="交易哈希")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    expires_at: datetime = Field(..., description="过期时间")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PaymentOrderResponse(BaseModel):
    """支付订单响应模型"""
    id: str = Field(..., description="订单ID")
    consultation_id: str = Field(..., description="咨询ID")
    user_id: str = Field(..., description="用户ID")
    amount_usdt: float = Field(..., description="支付金额(USDT)")
    usdt_address: str = Field(..., description="收款USDT(TRC20)地址")
    qr_code_url: str = Field(..., description="二维码URL")
    status: PaymentStatus = Field(..., description="支付状态")
    transaction_hash: Optional[str] = Field(None, description="交易哈希")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    expires_at: datetime = Field(..., description="过期时间")
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    """聊天消息"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    consultation_id: str = Field(..., description="咨询ID")
    sender_id: str = Field(..., description="发送者ID")
    sender_type: str = Field(..., description="发送者类型：user/doctor")
    message: str = Field(..., description="消息内容")
    message_type: str = Field(default="text", description="消息类型：text/image/file")
    attachments: List[str] = Field(default=[], description="附件列表")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ChatMessageResponse(BaseModel):
    """聊天消息响应模型"""
    id: str = Field(..., description="消息ID")
    consultation_id: str = Field(..., description="咨询ID")
    sender_id: str = Field(..., description="发送者ID")
    sender_type: str = Field(..., description="发送者类型")
    message: str = Field(..., description="消息内容")
    message_type: str = Field(..., description="消息类型")
    attachments: List[str] = Field(..., description="附件列表")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
