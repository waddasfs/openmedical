#!/usr/bin/env python3
"""
快速测试医生分配策略
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试基本功能"""
    print("=== 快速测试医生分配策略 ===\n")
    
    try:
        # 导入必要的模块
        from services.consultation_service import consultation_service
        from services.doctor_service import doctor_service
        from models.doctor import DoctorStatus, DoctorLevel
        from models.consultation import ConsultationStatus
        print("✅ 所有模块导入成功")
        
        # 测试获取在线医生
        print("\n1. 测试获取在线医生...")
        active_doctors = doctor_service.get_available_doctors()
        print(f"在线医生数量: {len(active_doctors)}")
        
        if active_doctors:
            for i, doctor in enumerate(active_doctors[:3]):  # 只显示前3个
                print(f"  医生{i+1}: {doctor.get('name', 'Unknown')} - 等级: {doctor.get('level', 'Unknown')} - 状态: {doctor.get('status', 'Unknown')} - 当前咨询数: {doctor.get('current_consultation_count', 0)}")
        
        # 测试获取未分配咨询
        print("\n2. 测试获取未分配咨询...")
        unassigned = consultation_service.get_unassigned_consultations(limit=5)
        print(f"未分配咨询数量: {len(unassigned)}")
        
        if unassigned:
            for i, consultation in enumerate(unassigned[:3]):  # 只显示前3个
                print(f"  咨询{i+1}: ID={consultation['id']} - 等级要求: {consultation.get('doctor_level', 'None')} - 状态: {consultation.get('status', 'Unknown')}")
        
        # 测试按等级获取医生
        print("\n3. 测试按等级获取医生...")
        for level in [DoctorLevel.NORMAL, DoctorLevel.SENIOR, DoctorLevel.EXPERT]:
            try:
                doctors = consultation_service.get_available_doctors_by_level(level)
                print(f"  {level.value}级医生数量: {len(doctors)}")
                if doctors:
                    for doctor in doctors[:2]:  # 只显示前2个
                        print(f"    - {doctor.get('name', 'Unknown')} - 当前咨询数: {doctor.get('current_consultation_count', 0)}")
            except Exception as e:
                print(f"  {level.value}级医生获取失败: {e}")
        
        # 测试自动分配（如果有未分配咨询）
        if unassigned:
            print("\n4. 测试自动分配...")
            consultation_id = unassigned[0]['id']
            print(f"尝试分配咨询: {consultation_id}")
            try:
                success = consultation_service.auto_assign_doctor(consultation_id)
                if success:
                    print("✅ 分配成功")
                else:
                    print("❌ 分配失败")
            except Exception as e:
                print(f"❌ 分配过程中出错: {e}")
        else:
            print("\n4. 没有未分配咨询可供测试")
        
        print("\n✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_functionality()
