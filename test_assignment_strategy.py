#!/usr/bin/env python3
"""
测试医生分配策略
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.consultation_service import consultation_service
from services.doctor_service import doctor_service
from models.consultation import ConsultationStatus, DoctorLevel
from models.doctor import DoctorStatus
import asyncio

async def test_assignment_strategy():
    """测试分配策略"""
    print("=== 测试医生分配策略 ===\n")
    
    # 1. 检查在线医生
    print("1. 检查在线医生...")
    active_doctors = doctor_service.get_available_doctors()
    print(f"在线医生数量: {len(active_doctors)}")
    for doctor in active_doctors:
        print(f"  - {doctor['name']} ({doctor['level']}级) - 当前咨询数: {doctor.get('current_consultation_count', 0)}")
    
    # 2. 检查未分配的咨询
    print("\n2. 检查未分配的咨询...")
    unassigned = consultation_service.get_unassigned_consultations()
    print(f"未分配咨询数量: {len(unassigned)}")
    for consultation in unassigned:
        print(f"  - 咨询ID: {consultation['id']} - 等级要求: {consultation['doctor_level']} - 状态: {consultation['status']}")
    
    # 3. 测试按等级获取医生
    print("\n3. 测试按等级获取医生...")
    for level in [DoctorLevel.NORMAL, DoctorLevel.SENIOR, DoctorLevel.EXPERT]:
        doctors = consultation_service.get_available_doctors_by_level(level)
        print(f"{level.value}级医生数量: {len(doctors)}")
        for doctor in doctors:
            print(f"  - {doctor['name']} - 当前咨询数: {doctor.get('current_consultation_count', 0)}")
    
    # 4. 测试自动分配
    print("\n4. 测试自动分配...")
    if unassigned:
        consultation_id = unassigned[0]['id']
        print(f"尝试分配咨询: {consultation_id}")
        success = consultation_service.auto_assign_doctor(consultation_id)
        if success:
            print("✅ 分配成功")
        else:
            print("❌ 分配失败")
    else:
        print("没有未分配的咨询可供测试")
    
    # 5. 再次检查未分配咨询
    print("\n5. 再次检查未分配咨询...")
    unassigned_after = consultation_service.get_unassigned_consultations()
    print(f"未分配咨询数量: {len(unassigned_after)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_assignment_strategy())
