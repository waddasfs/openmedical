#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询创建完整流程
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"

def test_consultation_creation_flow():
    """测试咨询创建完整流程"""
    print("=== 测试咨询创建完整流程 ===")
    
    # 1. 测试创建咨询
    print("\n1. 创建咨询...")
    consultation_id = create_consultation()
    if not consultation_id:
        print("❌ 咨询创建失败")
        return False
    
    print(f"✅ 咨询创建成功，ID: {consultation_id}")
    
    # 2. 验证咨询是否在数据库中
    print("\n2. 验证咨询数据...")
    if verify_consultation_exists(consultation_id):
        print("✅ 咨询数据验证成功")
    else:
        print("❌ 咨询数据验证失败")
        return False
    
    # 3. 测试获取咨询列表
    print("\n3. 测试获取咨询列表...")
    if test_get_consultation_list():
        print("✅ 咨询列表获取成功")
    else:
        print("❌ 咨询列表获取失败")
        return False
    
    return True

def create_consultation():
    """创建咨询"""
    try:
        files = [
            ("attachments", ("test_flow.txt", "流程测试文件", "text/plain"))
        ]
        
        data = {
            "mode": "onetime",
            "disease_description": "完整流程测试咨询",
            "symptoms": "测试症状描述",
            "medical_history": "测试病史记录",
            "doctor_level": "normal"
        }
        
        print(f"发送请求到: {BASE_URL}/api/consultation/create")
        print(f"请求数据: {data}")
        
        response = requests.post(f"{BASE_URL}/api/consultation/create", files=files, data=data)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get('consultation_id')
            else:
                print(f"API返回失败: {result.get('error')}")
                return None
        else:
            print(f"HTTP请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"创建咨询异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_consultation_exists(consultation_id):
    """验证咨询是否存在"""
    try:
        response = requests.get(f"{BASE_URL}/api/consultation/{consultation_id}")
        
        if response.status_code == 200:
            consultation = response.json()
            print(f"✅ 找到咨询记录: {consultation.get('disease_description')}")
            print(f"状态: {consultation.get('status')}")
            print(f"价格: {consultation.get('price_usdt')} USDT")
            return True
        else:
            print(f"❌ 获取咨询详情失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"验证咨询存在异常: {e}")
        return False

def test_get_consultation_list():
    """测试获取咨询列表"""
    try:
        response = requests.get(f"{BASE_URL}/api/consultation/user/list")
        
        if response.status_code == 200:
            consultations = response.json()
            print(f"✅ 获取咨询列表成功，共 {len(consultations)} 条记录")
            
            for i, cons in enumerate(consultations[:3]):  # 只显示前3条
                print(f"  {i+1}. ID: {cons.get('id')}, 描述: {cons.get('disease_description')[:50]}...")
            
            return True
        else:
            print(f"❌ 获取咨询列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"获取咨询列表异常: {e}")
        return False

def test_direct_database_check():
    """直接检查数据库"""
    print("\n=== 直接检查数据库 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 查询所有咨询记录
        consultations = mongo_dao.find_all("consultation")
        print(f"数据库中咨询记录总数: {len(consultations)}")
        
        if consultations:
            print("最近的咨询记录:")
            for i, cons in enumerate(consultations[-3:]):  # 显示最近3条
                print(f"  {i+1}. ID: {cons.get('_id')}")
                print(f"     用户ID: {cons.get('user_id')}")
                print(f"     模式: {cons.get('mode')}")
                print(f"     状态: {cons.get('status')}")
                print(f"     描述: {cons.get('disease_description', '')[:50]}...")
                print(f"     创建时间: {cons.get('created_at')}")
                print()
        else:
            print("❌ 数据库中没有咨询记录")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 直接数据库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试咨询创建完整流程...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 直接检查数据库
    db_ok = test_direct_database_check()
    
    if db_ok:
        # 测试完整流程
        flow_ok = test_consultation_creation_flow()
        
        print("\n=== 测试结果 ===")
        if flow_ok:
            print("✅ 所有测试通过！咨询创建流程正常")
        else:
            print("❌ 部分测试失败")
    else:
        print("❌ 数据库检查失败")
    
    return db_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

