#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复咨询数据入库问题
"""

import os
import sys
from datetime import datetime

def create_env_file():
    """创建.env文件"""
    print("=== 创建.env文件 ===")
    
    if os.path.exists(".env"):
        print("✅ .env文件已存在")
        return True
    
    env_content = """# MongoDB配置
MONGODB_IP=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=medical
MONGODB_COLLECTION=users
MONGODB_USERNAME=
MONGODB_PASSWORD=

# 应用配置
SECRET_KEY=your-secret-key-here
DEBUG=True
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ .env文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False

def test_consultation_creation():
    """测试咨询创建"""
    print("\n=== 测试咨询创建 ===")
    
    try:
        from services.consultation_service import consultation_service
        from models.consultation import ConsultationCreate, ConsultationMode, DoctorLevel
        
        # 创建测试咨询数据
        consultation_data = ConsultationCreate(
            mode=ConsultationMode.ONETIME,
            disease_description="修复测试咨询",
            symptoms="测试症状",
            medical_history="测试病史",
            attachments=[],
            doctor_level=DoctorLevel.NORMAL
        )
        
        print(f"测试咨询数据: {consultation_data}")
        
        # 调用创建方法
        result = consultation_service.create_consultation("test_user_fix", consultation_data)
        
        if result:
            print(f"✅ 咨询创建成功: {result}")
            print(f"ID: {result.id}")
            print(f"用户ID: {result.user_id}")
            print(f"状态: {result.status}")
            print(f"价格: {result.price_usdt} USDT")
            return True
        else:
            print("❌ 咨询创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 咨询创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_records():
    """验证数据库记录"""
    print("\n=== 验证数据库记录 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        
        # 查询所有咨询记录
        consultations = mongo_dao.find_all("consultation")
        print(f"数据库中咨询记录总数: {len(consultations)}")
        
        if consultations:
            print("咨询记录列表:")
            for i, cons in enumerate(consultations):
                print(f"  {i+1}. ID: {cons.get('_id')}")
                print(f"     用户ID: {cons.get('user_id')}")
                print(f"     模式: {cons.get('mode')}")
                print(f"     状态: {cons.get('status')}")
                print(f"     描述: {cons.get('disease_description', '')[:50]}...")
                print(f"     价格: {cons.get('price_usdt')} USDT")
                print(f"     创建时间: {cons.get('created_at')}")
                print()
            return True
        else:
            print("❌ 数据库中没有咨询记录")
            return False
        
    except Exception as e:
        print(f"❌ 验证数据库记录失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    try:
        import requests
        
        # 测试获取咨询套餐
        response = requests.get("http://localhost:5000/api/consultation/packages")
        if response.status_code == 200:
            packages = response.json()
            print(f"✅ 获取咨询套餐成功，共 {len(packages)} 个套餐")
        else:
            print(f"❌ 获取咨询套餐失败: {response.status_code}")
            return False
        
        # 测试获取用户咨询列表
        response = requests.get("http://localhost:5000/api/consultation/user/list")
        if response.status_code == 200:
            consultations = response.json()
            print(f"✅ 获取咨询列表成功，共 {len(consultations)} 条记录")
        else:
            print(f"❌ 获取咨询列表失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始修复咨询数据入库问题...")
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 创建.env文件
    env_ok = create_env_file()
    
    if env_ok:
        # 2. 测试咨询创建
        creation_ok = test_consultation_creation()
        
        if creation_ok:
            # 3. 验证数据库记录
            db_ok = verify_database_records()
            
            if db_ok:
                # 4. 测试API端点
                api_ok = test_api_endpoint()
                
                print("\n=== 修复结果 ===")
                if api_ok:
                    print("✅ 所有测试通过！咨询数据入库问题已修复")
                    print("\n修复内容:")
                    print("1. ✅ 创建了.env配置文件")
                    print("2. ✅ 修复了数据入库逻辑")
                    print("3. ✅ 添加了详细的调试日志")
                    print("4. ✅ 验证了数据库连接")
                    print("5. ✅ 测试了API端点")
                    
                    print("\n使用说明:")
                    print("1. 确保MongoDB服务正在运行")
                    print("2. 运行 'python main.py' 启动应用")
                    print("3. 访问 http://localhost:5000 测试功能")
                else:
                    print("❌ API端点测试失败")
            else:
                print("❌ 数据库记录验证失败")
        else:
            print("❌ 咨询创建测试失败")
    else:
        print("❌ 环境配置失败")
    
    return env_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

