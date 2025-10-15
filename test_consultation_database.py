#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询数据入库功能
"""

import requests
import json
import time
from datetime import datetime
from bson import ObjectId

# 测试配置
BASE_URL = "http://localhost:5000"

def test_consultation_database_insertion():
    """测试咨询数据入库功能"""
    print("=== 测试咨询数据入库功能 ===")
    
    # 1. 测试创建咨询并验证入库
    print("\n1. 测试创建咨询...")
    consultation_id = create_test_consultation()
    if not consultation_id:
        print("❌ 创建咨询失败")
        return False
    
    print(f"✅ 咨询创建成功，ID: {consultation_id}")
    
    # 2. 验证数据是否入库
    print("\n2. 验证数据入库...")
    if verify_consultation_in_database(consultation_id):
        print("✅ 数据已成功入库到MongoDB")
    else:
        print("❌ 数据未找到或入库失败")
        return False
    
    # 3. 测试查询功能
    print("\n3. 测试查询功能...")
    if test_consultation_queries(consultation_id):
        print("✅ 查询功能正常")
    else:
        print("❌ 查询功能异常")
        return False
    
    # 4. 测试更新功能
    print("\n4. 测试更新功能...")
    if test_consultation_update(consultation_id):
        print("✅ 更新功能正常")
    else:
        print("❌ 更新功能异常")
        return False
    
    return True

def create_test_consultation():
    """创建测试咨询"""
    try:
        files = [
            ("attachments", ("test_db.txt", "数据库测试文件", "text/plain"))
        ]
        
        data = {
            "mode": "onetime",
            "disease_description": "数据库入库测试咨询",
            "symptoms": "测试症状描述",
            "medical_history": "测试病史记录",
            "doctor_level": "normal"
        }
        
        print(f"发送请求到: {BASE_URL}/api/consultation/create")
        print(f"请求数据: {data}")
        
        response = requests.post(f"{BASE_URL}/api/consultation/create", files=files, data=data)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        result = response.json()
        
        if result.get("success"):
            return result.get('consultation_id')
        else:
            print(f"创建咨询失败: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"创建咨询异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_consultation_in_database(consultation_id):
    """验证咨询数据是否在数据库中"""
    try:
        # 这里需要直接连接MongoDB验证
        # 由于我们没有直接的MongoDB连接，我们通过API查询来验证
        response = requests.get(f"{BASE_URL}/api/consultation/{consultation_id}")
        
        if response.status_code == 200:
            consultation = response.json()
            print(f"从API查询到咨询数据: {consultation}")
            
            # 验证关键字段
            required_fields = ['id', 'user_id', 'mode', 'status', 'disease_description', 'price_usdt']
            for field in required_fields:
                if field not in consultation:
                    print(f"❌ 缺少必填字段: {field}")
                    return False
                if consultation[field] is None:
                    print(f"❌ 字段值为空: {field}")
                    return False
            
            print("✅ 所有必填字段验证通过")
            return True
        else:
            print(f"❌ API查询失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"验证数据入库异常: {e}")
        return False

def test_consultation_queries(consultation_id):
    """测试咨询查询功能"""
    try:
        # 测试获取咨询详情
        response = requests.get(f"{BASE_URL}/api/consultation/{consultation_id}")
        if response.status_code != 200:
            print(f"❌ 获取咨询详情失败: {response.status_code}")
            return False
        
        consultation = response.json()
        print(f"✅ 获取咨询详情成功: {consultation['disease_description']}")
        
        # 测试获取用户咨询列表
        response = requests.get(f"{BASE_URL}/api/consultation/user/list")
        if response.status_code != 200:
            print(f"❌ 获取咨询列表失败: {response.status_code}")
            return False
        
        consultations = response.json()
        print(f"✅ 获取咨询列表成功，共 {len(consultations)} 条记录")
        
        # 验证列表中包含我们创建的咨询
        found = False
        for cons in consultations:
            if cons['id'] == consultation_id:
                found = True
                break
        
        if found:
            print("✅ 创建的咨询在列表中找到了")
        else:
            print("❌ 创建的咨询未在列表中找到")
            return False
        
        return True
        
    except Exception as e:
        print(f"测试查询功能异常: {e}")
        return False

def test_consultation_update(consultation_id):
    """测试咨询更新功能"""
    try:
        # 测试支付状态更新
        response = requests.post(f"{BASE_URL}/api/payment/test/{consultation_id}")
        if response.status_code != 200:
            print(f"❌ 测试支付失败: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("success"):
            print(f"❌ 测试支付失败: {result.get('error')}")
            return False
        
        print("✅ 支付状态更新成功")
        
        # 验证状态是否更新
        time.sleep(1)  # 等待状态更新
        response = requests.get(f"{BASE_URL}/api/consultation/{consultation_id}")
        if response.status_code == 200:
            consultation = response.json()
            if consultation['status'] == 'paid':
                print("✅ 咨询状态已更新为已支付")
                return True
            else:
                print(f"❌ 咨询状态未正确更新: {consultation['status']}")
                return False
        else:
            print(f"❌ 获取更新后的咨询失败: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"测试更新功能异常: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 测试连接
        collections = mongo_dao.__db.list_collection_names()
        print(f"✅ 数据库连接成功，集合列表: {collections}")
        
        # 检查consultation集合是否存在
        if 'consultation' in collections:
            print("✅ consultation集合已存在")
        else:
            print("❌ consultation集合不存在")
            return False
        
        # 测试插入一条测试数据
        test_data = {
            "test_field": "test_value",
            "created_at": datetime.utcnow()
        }
        
        result = mongo_dao.insert("consultation", test_data)
        if result and result.inserted_id:
            print(f"✅ 测试数据插入成功，ID: {result.inserted_id}")
            
            # 清理测试数据
            mongo_dao.delete("consultation", "_id", result.inserted_id)
            print("✅ 测试数据已清理")
            return True
        else:
            print("❌ 测试数据插入失败")
            return False
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试咨询数据入库功能...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 测试数据库连接
    db_ok = test_database_connection()
    if not db_ok:
        print("❌ 数据库连接失败，无法继续测试")
        return False
    
    # 测试数据入库功能
    insertion_ok = test_consultation_database_insertion()
    
    print("\n=== 测试结果 ===")
    if insertion_ok:
        print("✅ 所有测试通过！咨询数据入库功能正常")
        print("\n功能总结:")
        print("1. ✅ 咨询数据成功入库到MongoDB")
        print("2. ✅ 数据字段结构正确")
        print("3. ✅ 查询功能正常")
        print("4. ✅ 更新功能正常")
        print("5. ✅ 数据库连接稳定")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    
    return insertion_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

