#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试医生登录功能
"""

import requests
import json

def test_doctor_login():
    """测试医生登录"""
    base_url = "http://localhost:5000"
    
    print("=== 测试医生登录功能 ===")
    
    # 测试医生登录API
    test_cases = [
        {
            "name": "张医生",
            "google_id": "test_google_doctor_001",
            "email": "zhang.doctor@test.com"
        },
        {
            "name": "李医生", 
            "google_id": "test_google_doctor_002",
            "email": "li.doctor@test.com"
        },
        {
            "name": "王医生",
            "google_id": "test_google_doctor_003", 
            "email": "wang.doctor@test.com"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试 {test_case['name']} 登录...")
        
        # 模拟用户信息
        user_info = {
            "sub": test_case["google_id"],
            "name": test_case["name"],
            "email": test_case["email"],
            "picture": f"https://via.placeholder.com/150/667eea/ffffff?text={test_case['name'][0]}"
        }
        
        # 发送登录请求
        try:
            response = requests.post(f"{base_url}/auth/doctor/google", 
                                   json={
                                       "token": f"test_token_{test_case['google_id']}",
                                       "user_info": user_info
                                   })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ {test_case['name']} 登录成功")
                    print(f"   医生信息: {data.get('doctor', {}).get('name', 'N/A')}")
                else:
                    print(f"❌ {test_case['name']} 登录失败: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ {test_case['name']} 请求失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ {test_case['name']} 测试异常: {e}")

def test_doctor_pages():
    """测试医生页面"""
    base_url = "http://localhost:5000"
    
    print("\n=== 测试医生页面 ===")
    
    pages = [
        "/doctor/login",
        "/doctor/dashboard",
        "/doctor/consultations", 
        "/doctor/earnings"
    ]
    
    for page in pages:
        try:
            response = requests.get(f"{base_url}{page}")
            print(f"{page}: {response.status_code}")
            if response.status_code == 401:
                print("  -> 需要医生登录")
        except Exception as e:
            print(f"{page}: 错误 - {e}")

def main():
    """主函数"""
    print("开始测试医生登录功能...")
    print("请确保服务器正在运行: python main.py")
    print()
    
    # 测试页面
    test_doctor_pages()
    
    # 测试登录
    test_doctor_login()
    
    print("\n=== 测试完成 ===")
    print("\n使用说明:")
    print("1. 访问 http://localhost:5000/doctor/login")
    print("2. 点击测试医生按钮进行快速登录")
    print("3. 或使用Google登录（需要配置Google OAuth2）")

if __name__ == "__main__":
    main()
