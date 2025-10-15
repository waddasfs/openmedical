#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试医生功能
"""

import requests
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_GOOGLE_TOKEN = "test_token_123"  # 实际测试时需要真实的Google token

def test_doctor_endpoints():
    """测试医生相关端点"""
    print("=== 测试医生功能 ===")
    
    # 测试医生登录端点（需要真实的Google token）
    print("\n1. 测试医生登录端点...")
    try:
        response = requests.post(f"{BASE_URL}/auth/doctor/google", 
                               json={"token": TEST_GOOGLE_TOKEN})
        print(f"医生登录响应状态: {response.status_code}")
        if response.status_code != 200:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"医生登录测试失败: {e}")
    
    # 测试医生页面路由
    print("\n2. 测试医生页面路由...")
    doctor_pages = [
        "/doctor/login",
        "/doctor/dashboard", 
        "/doctor/consultations",
        "/doctor/earnings"
    ]
    
    for page in doctor_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            print(f"{page}: {response.status_code}")
        except Exception as e:
            print(f"{page}: 错误 - {e}")
    
    # 测试医生API端点（需要登录状态）
    print("\n3. 测试医生API端点...")
    doctor_apis = [
        "/api/doctor/profile",
        "/api/doctor/consultations", 
        "/api/doctor/earnings"
    ]
    
    for api in doctor_apis:
        try:
            response = requests.get(f"{BASE_URL}{api}")
            print(f"{api}: {response.status_code}")
            if response.status_code == 401:
                print("  -> 需要医生登录")
        except Exception as e:
            print(f"{api}: 错误 - {e}")

def test_doctor_models():
    """测试医生模型"""
    print("\n=== 测试医生模型 ===")
    
    try:
        from models.doctor import DoctorCreate, DoctorLevel, DoctorSpecialty, DoctorStatus
        
        # 测试创建医生数据
        doctor_data = DoctorCreate(
            google_id="test_google_123",
            name="测试医生",
            email="doctor@test.com",
            picture="https://example.com/avatar.jpg",
            license_number="DOC123456",
            hospital="测试医院",
            department="内科",
            specialties=[DoctorSpecialty.GENERAL],
            level=DoctorLevel.NORMAL,
            experience_years=5,
            introduction="测试医生简介",
            consultation_fee=50.0
        )
        
        print("✅ 医生模型创建成功")
        print(f"医生姓名: {doctor_data.name}")
        print(f"医生等级: {doctor_data.level}")
        print(f"专业领域: {doctor_data.specialties}")
        
    except Exception as e:
        print(f"❌ 医生模型测试失败: {e}")

def test_doctor_service():
    """测试医生服务"""
    print("\n=== 测试医生服务 ===")
    
    try:
        from services.doctor_service import doctor_service
        from models.doctor import DoctorCreate, DoctorLevel, DoctorSpecialty
        
        # 测试创建医生
        doctor_data = DoctorCreate(
            google_id="test_google_456",
            name="服务测试医生",
            email="service@test.com",
            picture="https://example.com/avatar.jpg",
            license_number="DOC789012",
            hospital="服务测试医院",
            department="外科",
            specialties=[DoctorSpecialty.ORTHOPEDICS],
            level=DoctorLevel.SENIOR,
            experience_years=10,
            introduction="服务测试医生简介",
            consultation_fee=100.0
        )
        
        print("✅ 医生服务初始化成功")
        print(f"服务实例: {doctor_service}")
        
    except Exception as e:
        print(f"❌ 医生服务测试失败: {e}")

def main():
    """主测试函数"""
    print("开始测试医生功能...")
    
    # 测试模型和服务
    test_doctor_models()
    test_doctor_service()
    
    # 测试API端点
    test_doctor_endpoints()
    
    print("\n=== 测试完成 ===")
    print("\n注意事项:")
    print("1. 医生登录需要真实的Google OAuth2 token")
    print("2. 需要先创建医生账户才能测试登录功能")
    print("3. 确保MongoDB服务正在运行")
    print("4. 确保FastAPI服务正在运行在 http://localhost:5000")

if __name__ == "__main__":
    main()
