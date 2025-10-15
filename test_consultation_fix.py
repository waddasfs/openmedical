#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询创建修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.consultation_service import consultation_service
from models.consultation import ConsultationCreate, ConsultationMode, DoctorLevel

def test_consultation_creation():
    """测试咨询创建"""
    print("🧪 测试咨询创建...")
    
    try:
        # 测试实时聊天咨询
        print("\n1. 测试实时聊天咨询...")
        realtime_consultation = ConsultationCreate(
            mode=ConsultationMode.REALTIME,
            disease_description="测试疾病描述",
            symptoms="测试症状",
            medical_history="测试病史"
        )
        
        print(f"实时咨询数据: {realtime_consultation.dict()}")
        
        # 测试一次性咨询
        print("\n2. 测试一次性咨询...")
        onetime_consultation = ConsultationCreate(
            mode=ConsultationMode.ONETIME,
            disease_description="测试疾病描述",
            symptoms="测试症状",
            medical_history="测试病史",
            doctor_level=DoctorLevel.NORMAL
        )
        
        print(f"一次性咨询数据: {onetime_consultation.dict()}")
        
        # 测试套餐获取
        print("\n3. 测试套餐获取...")
        packages = consultation_service.get_consultation_packages()
        print(f"获取到 {len(packages)} 个套餐:")
        for pkg in packages:
            print(f"  - {pkg.name}: {pkg.price_eth} ETH")
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consultation_creation()

