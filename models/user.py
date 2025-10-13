#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

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

class UserBase(BaseModel):
    """用户基础模型"""
    google_id: str = Field(..., description="Google用户ID")
    name: str = Field(..., description="用户姓名")
    email: str = Field(..., description="用户邮箱")
    picture: Optional[str] = Field(None, description="用户头像URL")
    
class UserCreate(UserBase):
    """创建用户模型"""
    pass

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[str] = Field(None, description="用户姓名")
    picture: Optional[str] = Field(None, description="用户头像URL")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(default=0, description="登录次数")
    is_active: bool = Field(default=True, description="是否激活")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    """用户响应模型"""
    id: str = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(..., description="登录次数")
    is_active: bool = Field(..., description="是否激活")
    
    class Config:
        from_attributes = True
