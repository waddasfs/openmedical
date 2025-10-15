#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查MongoDB配置和连接
"""

import os
import sys
from datetime import datetime

def check_environment():
    """检查环境变量"""
    print("=== 检查环境变量 ===")
    
    # 检查.env文件
    if os.path.exists(".env"):
        print("✅ .env文件存在")
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            print("环境变量内容:")
            for line in content.split("\n"):
                if line.strip() and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if "PASSWORD" in key:
                        display_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                    else:
                        display_value = value
                    print(f"  {key}: {display_value}")
    else:
        print("❌ .env文件不存在")
        print("请创建.env文件，内容如下:")
        print("MONGODB_IP=localhost")
        print("MONGODB_PORT=27017")
        print("MONGODB_DATABASE=medical")
        print("MONGODB_COLLECTION=users")
        print("MONGODB_USERNAME=")
        print("MONGODB_PASSWORD=")
        return False
    
    return True

def test_mongodb_connection():
    """测试MongoDB连接"""
    print("\n=== 测试MongoDB连接 ===")
    
    try:
        from utils.mongo_config import mongo_config
        print(f"MongoDB配置: {mongo_config}")
        
        from utils.mongo_dao import mongo_dao
        print("✅ 成功导入mongo_dao")
        
        # 测试连接
        client = mongo_dao._MongoDao__client
        print(f"✅ MongoDB客户端: {client}")
        
        # 测试数据库
        db = mongo_dao._MongoDao__db
        print(f"✅ 数据库: {db.name}")
        
        # 列出集合
        collections = db.list_collection_names()
        print(f"✅ 集合列表: {collections}")
        
        # 检查consultation集合
        if 'consultation' in collections:
            print("✅ consultation集合存在")
            
            # 获取统计信息
            stats = db.command("collStats", "consultation")
            print(f"  - 文档数量: {stats.get('count', 0)}")
            print(f"  - 集合大小: {stats.get('size', 0)} 字节")
        else:
            print("❌ consultation集合不存在")
            print("将自动创建consultation集合")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_insert():
    """测试简单插入"""
    print("\n=== 测试简单插入 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 准备测试数据
        test_data = {
            "test_type": "config_test",
            "timestamp": datetime.utcnow(),
            "message": "配置测试数据"
        }
        
        print(f"准备插入测试数据: {test_data}")
        
        # 插入数据
        result = mongo_dao.insert("consultation", test_data)
        print(f"插入结果: {result}")
        
        if result and hasattr(result, 'inserted_id') and result.inserted_id:
            print(f"✅ 插入成功，ID: {result.inserted_id}")
            
            # 验证插入
            found = mongo_dao.search("consultation", "_id", result.inserted_id)
            if found:
                print(f"✅ 验证成功，找到数据: {found[0]}")
            else:
                print("❌ 验证失败")
            
            # 清理测试数据
            mongo_dao.delete("consultation", "_id", result.inserted_id)
            print("✅ 测试数据已清理")
            
            return True
        else:
            print("❌ 插入失败")
            return False
            
    except Exception as e:
        print(f"❌ 简单插入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始检查MongoDB配置...")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境变量
    env_ok = check_environment()
    
    if env_ok:
        # 测试MongoDB连接
        connection_ok = test_mongodb_connection()
        
        if connection_ok:
            # 测试简单插入
            insert_ok = test_simple_insert()
            
            print("\n=== 检查结果 ===")
            if insert_ok:
                print("✅ 所有检查通过！MongoDB配置正确")
                print("\n建议:")
                print("1. 确保MongoDB服务正在运行")
                print("2. 检查防火墙设置")
                print("3. 验证数据库权限")
            else:
                print("❌ 插入测试失败")
        else:
            print("❌ MongoDB连接失败")
    else:
        print("❌ 环境配置问题")
    
    return env_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

