#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医疗咨询系统测试脚本
"""

import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@example.com"

def test_consultation_system():
    """测试医疗咨询系统"""
    print("🏥 开始测试医疗咨询系统...")
    
    # 测试1: 获取咨询套餐
    print("\n1. 测试获取咨询套餐...")
    try:
        response = requests.get(f"{BASE_URL}/api/consultation/packages")
        if response.status_code == 200:
            packages = response.json()
            print(f"✅ 成功获取 {len(packages)} 个咨询套餐")
            for pkg in packages:
                print(f"   - {pkg['name']}: {pkg['price_eth']} ETH")
        else:
            print(f"❌ 获取套餐失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取套餐异常: {e}")
    
    # 测试2: 测试支付服务
    print("\n2. 测试支付服务...")
    try:
        from services.payment_service import payment_service
        
        # 测试二维码生成
        test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        test_amount = 0.01
        qr_code = payment_service.generate_qr_code(test_address, test_amount)
        
        if qr_code.startswith("data:image/png;base64,"):
            print("✅ 二维码生成成功")
        else:
            print("❌ 二维码生成失败")
            
    except Exception as e:
        print(f"❌ 支付服务测试异常: {e}")
    
    # 测试3: 测试咨询服务
    print("\n3. 测试咨询服务...")
    try:
        from services.consultation_service import consultation_service
        
        # 测试获取套餐
        packages = consultation_service.get_consultation_packages()
        print(f"✅ 咨询服务正常，共有 {len(packages)} 个套餐")
        
        # 测试获取普通医生套餐
        normal_package = consultation_service.get_package_by_level("normal")
        if normal_package:
            print(f"✅ 普通医生套餐: {normal_package.name} - {normal_package.price_eth} ETH")
        else:
            print("❌ 获取普通医生套餐失败")
            
    except Exception as e:
        print(f"❌ 咨询服务测试异常: {e}")
    
    # 测试4: 测试数据模型
    print("\n4. 测试数据模型...")
    try:
        from models.consultation import ConsultationCreate, ConsultationMode, DoctorLevel
        
        # 创建测试咨询数据
        test_consultation = ConsultationCreate(
            mode=ConsultationMode.ONETIME,
            disease_description="测试疾病描述",
            symptoms="测试症状",
            medical_history="测试病史",
            doctor_level=DoctorLevel.NORMAL
        )
        
        print("✅ 数据模型创建成功")
        print(f"   - 模式: {test_consultation.mode}")
        print(f"   - 医生等级: {test_consultation.doctor_level}")
        
    except Exception as e:
        print(f"❌ 数据模型测试异常: {e}")
    
    print("\n🎉 测试完成！")
    print("\n📝 使用说明:")
    print("1. 确保MongoDB服务正在运行")
    print("2. 配置.env文件中的环境变量")
    print("3. 运行 'python main.py' 启动服务")
    print("4. 访问 http://localhost:5000 开始使用")

if __name__ == "__main__":
    test_consultation_system()

