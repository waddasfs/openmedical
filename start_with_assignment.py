#!/usr/bin/env python3
"""
启动带有医生分配策略的系统
"""
import subprocess
import sys
import time
import requests
import json

def test_assignment_api():
    """测试分配API"""
    try:
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(3)
        
        # 测试手动触发分配
        print("测试手动触发分配...")
        response = requests.post("http://localhost:5000/api/admin/trigger-assignment")
        if response.status_code == 200:
            print("✅ 手动触发分配成功")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 手动触发分配失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"测试API时出错: {e}")

def main():
    """主函数"""
    print("=== 启动带有医生分配策略的系统 ===")
    
    try:
        # 启动FastAPI服务
        print("启动FastAPI服务...")
        process = subprocess.Popen([sys.executable, "main.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 测试API
        test_assignment_api()
        
        print("\n系统已启动，访问以下地址：")
        print("- 患者端: http://localhost:5000/")
        print("- 医生端: http://localhost:5000/doctor/login")
        print("- 医生仪表板: http://localhost:5000/doctor/dashboard")
        
        print("\n按 Ctrl+C 停止服务")
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止服务...")
            process.terminate()
            process.wait()
            print("服务已停止")
            
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()
