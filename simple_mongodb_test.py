#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的MongoDB测试
"""

import os
import sys
from datetime import datetime

def test_basic_connection():
    """测试基本连接"""
    print("=== 测试基本MongoDB连接 ===")
    
    try:
        # 直接测试MongoDB连接
        import pymongo
        from pymongo import MongoClient
        
        # 使用默认配置
        client = MongoClient('localhost', 27017)
        db = client['medical']
        
        print(f"✅ 连接成功，数据库: {db.name}")
        
        # 测试插入
        collection = db['consultation']
        test_doc = {
            "test": "simple_test",
            "timestamp": datetime.utcnow(),
            "user_id": "test_user_simple"
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ 插入成功，ID: {result.inserted_id}")
        
        # 验证插入
        found = collection.find_one({"_id": result.inserted_id})
        if found:
            print(f"✅ 验证成功，找到文档: {found}")
        else:
            print("❌ 验证失败，未找到文档")
        
        # 清理测试数据
        collection.delete_one({"_id": result.inserted_id})
        print("✅ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dao_connection():
    """测试DAO连接"""
    print("\n=== 测试DAO连接 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 测试基本操作
        test_data = {
            "test_field": "dao_test",
            "timestamp": datetime.utcnow(),
            "user_id": "test_user_dao"
        }
        
        print(f"准备插入数据: {test_data}")
        result = mongo_dao.insert("consultation", test_data)
        print(f"插入结果: {result}")
        
        if result and result.inserted_id:
            print(f"✅ DAO插入成功，ID: {result.inserted_id}")
            
            # 验证数据
            found = mongo_dao.search("consultation", "_id", result.inserted_id)
            if found:
                print(f"✅ DAO验证成功，找到数据: {found[0]}")
            else:
                print("❌ DAO验证失败")
            
            # 清理数据
            mongo_dao.delete("consultation", "_id", result.inserted_id)
            print("✅ DAO测试数据已清理")
            
            return True
        else:
            print("❌ DAO插入失败")
            return False
            
    except Exception as e:
        print(f"❌ DAO连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consultation_creation():
    """测试咨询创建"""
    print("\n=== 测试咨询创建 ===")
    
    try:
        from services.consultation_service import consultation_service
        from models.consultation import ConsultationCreate, ConsultationMode, DoctorLevel
        
        # 创建测试数据
        consultation_data = ConsultationCreate(
            mode=ConsultationMode.ONETIME,
            disease_description="简单测试咨询",
            symptoms="测试症状",
            medical_history="测试病史",
            attachments=[],
            doctor_level=DoctorLevel.NORMAL
        )
        
        print(f"测试咨询数据: {consultation_data}")
        
        # 调用创建方法
        result = consultation_service.create_consultation("test_user_creation", consultation_data)
        
        if result:
            print(f"✅ 咨询创建成功: {result}")
            print(f"ID: {result.id}")
            print(f"状态: {result.status}")
            print(f"价格: {result.price_usdt}")
            return True
        else:
            print("❌ 咨询创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 咨询创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始简单MongoDB测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试基本连接
    basic_ok = test_basic_connection()
    
    if basic_ok:
        # 测试DAO连接
        dao_ok = test_dao_connection()
        
        if dao_ok:
            # 测试咨询创建
            creation_ok = test_consultation_creation()
            
            print("\n=== 测试结果 ===")
            if creation_ok:
                print("✅ 所有测试通过！")
            else:
                print("❌ 咨询创建测试失败")
        else:
            print("❌ DAO连接测试失败")
    else:
        print("❌ 基本连接测试失败")
    
    return basic_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

