#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理功能测试脚本
"""
 
import requests
import json
from datetime import datetime

# 测试服务器地址
BASE_URL = "http://localhost:5000"

def test_user_stats():
    """测试用户统计API"""
    print("测试用户统计API...")
    try:
        response = requests.get(f"{BASE_URL}/api/user/stats", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        if response.status_code == 200:
            stats = response.json()
            print(f"用户统计: {stats}")
            print("✅ 用户统计API测试通过\n")
        else:
            print(f"❌ 用户统计API测试失败: {response.text}\n")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保FastAPI应用正在运行\n")
    except Exception as e:
        print(f"❌ 用户统计API测试出错: {e}\n")

def test_users_list():
    """测试用户列表API"""
    print("测试用户列表API...")
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            print(f"用户数量: {len(users)}")
            if users:
                print(f"第一个用户: {users[0]}")
            print("✅ 用户列表API测试通过\n")
        else:
            print(f"❌ 用户列表API测试失败: {response.text}\n")
    except Exception as e:
        print(f"❌ 用户列表API测试出错: {e}\n")

def test_user_profile_without_auth():
    """测试未认证访问用户资料API"""
    print("测试未认证访问用户资料API...")
    try:
        response = requests.get(f"{BASE_URL}/api/user/profile")
        print(f"状态码: {response.status_code}")
        if response.status_code == 401:
            print("✅ 未认证访问被正确拒绝\n")
        else:
            print(f"❌ 未认证访问应该被拒绝，但返回: {response.status_code}\n")
    except Exception as e:
        print(f"❌ 用户资料API测试出错: {e}\n")

def test_homepage():
    """测试首页"""
    print("测试首页...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print("✅ 首页测试通过\n")
    except Exception as e:
        print(f"❌ 首页测试出错: {e}\n")

def test_login_page():
    """测试登录页面"""
    print("测试登录页面...")
    try:
        response = requests.get(f"{BASE_URL}/login")
        print(f"状态码: {response.status_code}")
        print("✅ 登录页面测试通过\n")
    except Exception as e:
        print(f"❌ 登录页面测试出错: {e}\n")

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        from services.user_service import user_service
        stats = user_service.get_user_stats()
        print(f"数据库连接成功，用户统计: {stats}")
        print("✅ 数据库连接测试通过\n")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}\n")
        print("请检查MongoDB配置和连接\n")

if __name__ == "__main__":
    print("开始测试用户管理功能...\n")
    
    try:
        # 测试数据库连接
        test_database_connection()
        
        # 测试基本页面
        test_homepage()
        test_login_page()
        
        # 测试API端点
        test_user_stats()
        test_users_list()
        test_user_profile_without_auth()
        
        print("🎉 所有测试完成！")
        print("\n📝 使用说明:")
        print("1. 确保MongoDB服务正在运行")
        print("2. 确保已配置正确的MongoDB连接信息")
        print("3. 在浏览器中访问 http://localhost:5000 进行完整测试")
        print("4. 访问 http://localhost:5000/docs 查看API文档")
        print("5. 使用Google登录后，用户信息将自动保存到MongoDB")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
