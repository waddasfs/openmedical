#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医生端演示启动脚本
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    try:
        import fastapi
        import pymongo
        import pydantic
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_mongodb():
    """检查MongoDB连接"""
    print("检查MongoDB连接...")
    try:
        from utils.mongo_dao import mongo_dao
        # 尝试连接数据库
        mongo_dao._MongoDao__db.list_collection_names()
        print("✅ MongoDB连接正常")
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        print("请确保MongoDB服务正在运行")
        return False

def create_test_data():
    """创建测试数据"""
    print("创建测试医生账户...")
    try:
        from create_test_doctor import create_test_doctors
        doctors = create_test_doctors()
        if doctors:
            print(f"✅ 成功创建 {len(doctors)} 个测试医生账户")
            return True
        else:
            print("❌ 创建测试医生账户失败")
            return False
    except Exception as e:
        print(f"❌ 创建测试数据时出错: {e}")
        return False

def start_server():
    """启动服务器"""
    print("启动FastAPI服务器...")
    try:
        # 启动服务器
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(3)
        
        # 检查服务器是否启动成功
        import requests
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器启动成功")
                return process
            else:
                print("❌ 服务器启动失败")
                return None
        except:
            print("❌ 无法连接到服务器")
            return None
            
    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        return None

def open_browser():
    """打开浏览器"""
    print("打开浏览器...")
    try:
        webbrowser.open("http://localhost:5000")
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"❌ 打开浏览器失败: {e}")

def main():
    """主函数"""
    print("=== 医生端演示启动脚本 ===")
    print()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查MongoDB
    if not check_mongodb():
        return
    
    # 创建测试数据
    if not create_test_data():
        return
    
    print()
    print("=== 启动服务器 ===")
    
    # 启动服务器
    process = start_server()
    if not process:
        return
    
    print()
    print("=== 服务器信息 ===")
    print("服务器地址: http://localhost:5000")
    print("患者端入口: http://localhost:5000/")
    print("医生端入口: http://localhost:5000/doctor/login")
    print()
    print("测试医生账户:")
    print("- 张医生: test_google_doctor_001")
    print("- 李医生: test_google_doctor_002") 
    print("- 王医生: test_google_doctor_003")
    print()
    print("按 Ctrl+C 停止服务器")
    
    # 打开浏览器
    open_browser()
    
    try:
        # 保持服务器运行
        process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        process.terminate()
        print("服务器已停止")

if __name__ == "__main__":
    main()
