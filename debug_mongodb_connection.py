#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试MongoDB连接和数据入库问题
"""

import os
import sys
from datetime import datetime

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("=== 测试MongoDB连接 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        print("✅ 成功导入mongo_dao")
        
        # 测试连接
        client = mongo_dao._MongoDao__client
        print(f"✅ MongoDB客户端连接成功: {client}")
        
        # 测试数据库
        db = mongo_dao._MongoDao__db
        print(f"✅ 数据库连接成功: {db.name}")
        
        # 列出所有集合
        collections = db.list_collection_names()
        print(f"✅ 数据库中的集合: {collections}")
        
        # 检查consultation集合
        if 'consultation' in collections:
            print("✅ consultation集合已存在")
            
            # 获取集合统计信息
            stats = db.command("collStats", "consultation")
            print(f"consultation集合统计:")
            print(f"  - 文档数量: {stats.get('count', 0)}")
            print(f"  - 集合大小: {stats.get('size', 0)} 字节")
        else:
            print("❌ consultation集合不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_insertion():
    """测试数据插入"""
    print("\n=== 测试数据插入 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 准备测试数据
        test_data = {
            "user_id": "test_user_001",
            "mode": "onetime",
            "status": "pending",
            "disease_description": "测试疾病描述",
            "symptoms": "测试症状",
            "medical_history": "测试病史",
            "attachments": [],
            "doctor_level": "normal",
            "assigned_doctor_id": None,
            "package_id": None,
            "price_usdt": 10.0,
            "payment_order_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None
        }
        
        print(f"准备插入测试数据: {test_data}")
        
        # 插入数据
        result = mongo_dao.insert("consultation", test_data)
        print(f"插入结果: {result}")
        
        if result and result.inserted_id:
            print(f"✅ 数据插入成功，ID: {result.inserted_id}")
            
            # 验证数据是否真的插入
            inserted_data = mongo_dao.search("consultation", "_id", result.inserted_id)
            if inserted_data:
                print(f"✅ 数据验证成功，找到插入的数据: {inserted_data[0]}")
                return True
            else:
                print("❌ 数据验证失败，未找到插入的数据")
                return False
        else:
            print("❌ 数据插入失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据插入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consultation_service():
    """测试咨询服务"""
    print("\n=== 测试咨询服务 ===")
    
    try:
        from services.consultation_service import consultation_service
        from models.consultation import ConsultationCreate, ConsultationMode, DoctorLevel
        
        print("✅ 成功导入consultation_service")
        
        # 创建测试咨询数据
        consultation_data = ConsultationCreate(
            mode=ConsultationMode.ONETIME,
            disease_description="咨询服务测试",
            symptoms="测试症状描述",
            medical_history="测试病史记录",
            attachments=[],
            doctor_level=DoctorLevel.NORMAL
        )
        
        print(f"测试咨询数据: {consultation_data}")
        
        # 调用创建咨询方法
        result = consultation_service.create_consultation("test_user_002", consultation_data)
        
        if result:
            print(f"✅ 咨询服务测试成功，返回结果: {result}")
            print(f"咨询ID: {result.id}")
            print(f"用户ID: {result.user_id}")
            print(f"状态: {result.status}")
            return True
        else:
            print("❌ 咨询服务测试失败，返回None")
            return False
            
    except Exception as e:
        print(f"❌ 咨询服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n=== 检查环境变量 ===")
    
    env_vars = [
        "MONGODB_IP",
        "MONGODB_PORT", 
        "MONGODB_DATABASE",
        "MONGODB_USERNAME",
        "MONGODB_PASSWORD"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 对于密码，只显示前几位
            if "PASSWORD" in var:
                display_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未设置")
    
    # 检查.env文件是否存在
    if os.path.exists(".env"):
        print("✅ .env文件存在")
    else:
        print("❌ .env文件不存在")

def main():
    """主函数"""
    print("开始调试MongoDB连接和数据入库问题...")
    print(f"调试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境变量
    check_environment_variables()
    
    # 测试MongoDB连接
    connection_ok = test_mongodb_connection()
    
    if connection_ok:
        # 测试数据插入
        insertion_ok = test_data_insertion()
        
        if insertion_ok:
            # 测试咨询服务
            service_ok = test_consultation_service()
            
            print("\n=== 调试结果 ===")
            if service_ok:
                print("✅ 所有测试通过！MongoDB连接和数据入库功能正常")
            else:
                print("❌ 咨询服务测试失败")
        else:
            print("❌ 数据插入测试失败")
    else:
        print("❌ MongoDB连接测试失败")
    
    return connection_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

