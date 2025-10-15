#!/usr/bin/env python3
"""
简单的医生分配策略测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.consultation_service import consultation_service
from services.doctor_service import doctor_service
from models.consultation import ConsultationStatus, DoctorLevel
from models.doctor import DoctorStatus

def test_assignment_basic():
    """基本分配测试"""
    print("=== 简单医生分配策略测试 ===\n")
    
    # 1. 检查在线医生
    print("1. 检查在线医生...")
    try:
        active_doctors = doctor_service.get_available_doctors()
        print(f"在线医生数量: {len(active_doctors)}")
        for doctor in active_doctors:
            print(f"  - {doctor['name']} ({doctor['level']}级) - 状态: {doctor['status']}")
    except Exception as e:
        print(f"获取在线医生失败: {e}")
    
    # 2. 检查未分配的咨询
    print("\n2. 检查未分配的咨询...")
    try:
        unassigned = consultation_service.get_unassigned_consultations()
        print(f"未分配咨询数量: {len(unassigned)}")
        for consultation in unassigned[:3]:  # 只显示前3个
            print(f"  - 咨询ID: {consultation['id']} - 等级要求: {consultation['doctor_level']} - 状态: {consultation['status']}")
    except Exception as e:
        print(f"获取未分配咨询失败: {e}")
    
    # 3. 测试按等级获取医生
    print("\n3. 测试按等级获取医生...")
    try:
        for level in [DoctorLevel.NORMAL, DoctorLevel.SENIOR, DoctorLevel.EXPERT]:
            doctors = consultation_service.get_available_doctors_by_level(level)
            print(f"{level.value}级医生数量: {len(doctors)}")
            for doctor in doctors[:2]:  # 只显示前2个
                print(f"  - {doctor['name']} - 当前咨询数: {doctor.get('current_consultation_count', 0)}")
    except Exception as e:
        print(f"按等级获取医生失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_assignment_basic()
