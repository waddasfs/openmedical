#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医生数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
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

class DoctorLevel(str, Enum):
    """医生等级"""
    NORMAL = "normal"      # 普通医生
    SENIOR = "senior"      # 高级医生
    EXPERT = "expert"      # 专家医生

class DoctorStatus(str, Enum):
    """医生状态"""
    ACTIVE = "active"          # 活跃
    BUSY = "busy"             # 忙碌
    OFFLINE = "offline"       # 离线
    SUSPENDED = "suspended"   # 暂停

class DoctorSpecialty(str, Enum):
    """医生专业"""
    GENERAL = "general"           # 全科
    CARDIOLOGY = "cardiology"     # 心内科
    NEUROLOGY = "neurology"       # 神经科
    DERMATOLOGY = "dermatology"   # 皮肤科
    PEDIATRICS = "pediatrics"     # 儿科
    GYNECOLOGY = "gynecology"     # 妇科
    ORTHOPEDICS = "orthopedics"   # 骨科
    PSYCHIATRY = "psychiatry"     # 精神科
    OPHTHALMOLOGY = "ophthalmology"  # 眼科
    ENT = "ent"                   # 耳鼻喉科

class DoctorBase(BaseModel):
    """医生基础模型"""
    google_id: str = Field(..., description="Google用户ID")
    name: str = Field(..., description="医生姓名")
    email: str = Field(..., description="医生邮箱")
    picture: Optional[str] = Field(None, description="医生头像URL")
    license_number: str = Field(..., description="医师执业证号")
    hospital: str = Field(..., description="所属医院")
    department: str = Field(..., description="所属科室")
    specialties: List[DoctorSpecialty] = Field(..., description="专业领域")
    level: DoctorLevel = Field(..., description="医生等级")
    experience_years: int = Field(..., description="从业年限")
    introduction: str = Field(..., description="医生简介")
    consultation_fee: float = Field(..., description="咨询费用(USDT)")

class DoctorCreate(DoctorBase):
    """创建医生模型"""
    pass

class DoctorUpdate(BaseModel):
    """更新医生模型"""
    name: Optional[str] = Field(None, description="医生姓名")
    picture: Optional[str] = Field(None, description="医生头像URL")
    hospital: Optional[str] = Field(None, description="所属医院")
    department: Optional[str] = Field(None, description="所属科室")
    specialties: Optional[List[DoctorSpecialty]] = Field(None, description="专业领域")
    level: Optional[DoctorLevel] = Field(None, description="医生等级")
    experience_years: Optional[int] = Field(None, description="从业年限")
    introduction: Optional[str] = Field(None, description="医生简介")
    consultation_fee: Optional[float] = Field(None, description="咨询费用(USDT)")
    status: Optional[DoctorStatus] = Field(None, description="医生状态")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

class DoctorInDB(DoctorBase):
    """数据库中的医生模型"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: DoctorStatus = Field(default=DoctorStatus.OFFLINE, description="医生状态")
    total_consultations: int = Field(default=0, description="总咨询次数")
    current_consultation_count: int = Field(default=0, description="当前进行中的咨询数量")
    total_earnings: float = Field(default=0.0, description="总收入(USDT)")
    rating: float = Field(default=5.0, description="评分")
    rating_count: int = Field(default=0, description="评分次数")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(default=0, description="登录次数")
    is_active: bool = Field(default=True, description="是否激活")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DoctorResponse(DoctorBase):
    """医生响应模型"""
    id: str = Field(..., description="医生ID")
    status: DoctorStatus = Field(..., description="医生状态")
    total_consultations: int = Field(..., description="总咨询次数")
    current_consultation_count: int = Field(..., description="当前进行中的咨询数量")
    total_earnings: float = Field(..., description="总收入(USDT)")
    rating: float = Field(..., description="评分")
    rating_count: int = Field(..., description="评分次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(..., description="登录次数")
    is_active: bool = Field(..., description="是否激活")
    
    class Config:
        from_attributes = True

class DoctorEarnings(BaseModel):
    """医生收入统计"""
    doctor_id: str = Field(..., description="医生ID")
    total_earnings: float = Field(..., description="总收入(USDT)")
    monthly_earnings: float = Field(..., description="本月收入(USDT)")
    weekly_earnings: float = Field(..., description="本周收入(USDT)")
    daily_earnings: float = Field(..., description="今日收入(USDT)")
    total_consultations: int = Field(..., description="总咨询次数")
    completed_consultations: int = Field(..., description="已完成咨询次数")
    pending_consultations: int = Field(..., description="待处理咨询次数")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="最后更新时间")
    
    class Config:
        from_attributes = True

class DoctorAssignment(BaseModel):
    """医生分配记录"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    doctor_id: str = Field(..., description="医生ID")
    consultation_id: str = Field(..., description="咨询ID")
    assigned_at: datetime = Field(default_factory=datetime.utcnow, description="分配时间")
    status: str = Field(default="assigned", description="分配状态")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
