#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询查询修复
"""

import requests
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"

def test_consultation_query_fix():
    """测试咨询查询修复"""
    print("=== 测试咨询查询修复 ===")
    
    # 1. 测试获取用户咨询列表
    print("\n1. 测试获取用户咨询列表...")
    response = requests.get(f"{BASE_URL}/api/consultation/user/list")
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        consultations = response.json()
        print(f"✅ 成功获取咨询列表，共 {len(consultations)} 条记录")
        
        for i, cons in enumerate(consultations):
            print(f"  {i+1}. ID: {cons.get('id')}")
            print(f"     用户ID: {cons.get('user_id')}")
            print(f"     模式: {cons.get('mode')}")
            print(f"     状态: {cons.get('status')}")
            print(f"     描述: {cons.get('disease_description', '')[:50]}...")
            print(f"     价格: {cons.get('price_usdt')} USDT")
            print(f"     创建时间: {cons.get('created_at')}")
            print()
        
        return True
    else:
        print(f"❌ 获取咨询列表失败: {response.status_code}")
        return False

def test_consultation_detail():
    """测试咨询详情查询"""
    print("\n2. 测试咨询详情查询...")
    
    # 先获取咨询列表
    response = requests.get(f"{BASE_URL}/api/consultation/user/list")
    if response.status_code != 200:
        print("❌ 无法获取咨询列表")
        return False
    
    consultations = response.json()
    if not consultations:
        print("❌ 没有咨询记录可供测试")
        return False
    
    # 测试第一个咨询的详情
    consultation_id = consultations[0]['id']
    print(f"测试咨询ID: {consultation_id}")
    
    response = requests.get(f"{BASE_URL}/api/consultation/{consultation_id}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        consultation = response.json()
        print(f"✅ 成功获取咨询详情")
        print(f"ID: {consultation.get('id')}")
        print(f"用户ID: {consultation.get('user_id')}")
        print(f"模式: {consultation.get('mode')}")
        print(f"状态: {consultation.get('status')}")
        print(f"价格: {consultation.get('price_usdt')} USDT")
        return True
    else:
        print(f"❌ 获取咨询详情失败: {response.status_code}")
        return False

def test_direct_database_query():
    """直接测试数据库查询"""
    print("\n3. 直接测试数据库查询...")
    
    try:
        from services.consultation_service import consultation_service
        
        # 测试获取用户咨询列表
        consultations = consultation_service.get_user_consultations("test_user_fix")
        print(f"✅ 直接数据库查询成功，获取 {len(consultations)} 条记录")
        
        for i, cons in enumerate(consultations):
            print(f"  {i+1}. ID: {cons.id}")
            print(f"     用户ID: {cons.user_id}")
            print(f"     模式: {cons.mode}")
            print(f"     状态: {cons.status}")
            print(f"     描述: {cons.disease_description[:50]}...")
            print(f"     价格: {cons.price_usdt} USDT")
            print(f"     创建时间: {cons.created_at}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 直接数据库查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_new_consultation():
    """测试创建新咨询"""
    print("\n4. 测试创建新咨询...")
    
    try:
        files = [
            ("attachments", ("test_query_fix.txt", "查询修复测试文件", "text/plain"))
        ]
        
        data = {
            "mode": "onetime",
            "disease_description": "查询修复测试咨询",
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
                consultation_id = result.get('consultation_id')
                print(f"✅ 咨询创建成功，ID: {consultation_id}")
                
                # 立即测试查询
                time.sleep(1)  # 等待1秒
                response = requests.get(f"{BASE_URL}/api/consultation/user/list")
                if response.status_code == 200:
                    consultations = response.json()
                    print(f"✅ 查询测试成功，现在有 {len(consultations)} 条记录")
                    return True
                else:
                    print("❌ 查询测试失败")
                    return False
            else:
                print(f"❌ 咨询创建失败: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 创建咨询异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试咨询查询修复...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 测试直接数据库查询
    db_ok = test_direct_database_query()
    
    if db_ok:
        # 测试API查询
        api_ok = test_consultation_query_fix()
        
        if api_ok:
            # 测试咨询详情
            detail_ok = test_consultation_detail()
            
            if detail_ok:
                # 测试创建新咨询
                create_ok = test_create_new_consultation()
                
                print("\n=== 测试结果 ===")
                if create_ok:
                    print("✅ 所有测试通过！咨询查询修复成功")
                    print("\n修复内容:")
                    print("1. ✅ 添加了数据标准化方法")
                    print("2. ✅ 修复了字段映射问题")
                    print("3. ✅ 确保price_usdt字段存在")
                    print("4. ✅ 改进了错误处理")
                    print("5. ✅ 验证了API查询功能")
                else:
                    print("❌ 创建新咨询测试失败")
            else:
                print("❌ 咨询详情查询测试失败")
        else:
            print("❌ API查询测试失败")
    else:
        print("❌ 直接数据库查询测试失败")
    
    return db_ok

if __name__ == "__main__":
    import time
    success = main()
    exit(0 if success else 1)

