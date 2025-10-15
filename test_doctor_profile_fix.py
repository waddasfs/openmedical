#!/usr/bin/env python3
"""
测试医生档案修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doctor_profile():
    """测试医生档案获取"""
    print("=== 测试医生档案修复 ===\n")
    
    try:
        from services.doctor_service import doctor_service
        from models.doctor import DoctorInDB
        
        # 获取所有医生 - 使用search_multi_filter方法
        doctors = doctor_service.dao.search_multi_filter("doctors", {})
        print(f"数据库中的医生数量: {len(doctors)}")
        
        if doctors:
            # 测试第一个医生
            doctor_data = doctors[0]
            doctor_id = str(doctor_data["_id"])
            print(f"测试医生ID: {doctor_id}")
            
            # 确保包含current_consultation_count字段
            if "current_consultation_count" not in doctor_data:
                doctor_data["current_consultation_count"] = 0
                print("添加了current_consultation_count字段")
            
            # 尝试创建DoctorInDB对象
            doctor_data["id"] = doctor_data.pop("_id")
            doctor = DoctorInDB(**doctor_data)
            print(f"✅ 成功创建DoctorInDB对象: {doctor.name}")
            print(f"  - 当前咨询数: {doctor.current_consultation_count}")
            print(f"  - 总咨询数: {doctor.total_consultations}")
            print(f"  - 状态: {doctor.status}")
            
            # 测试get_doctor_by_id方法
            print(f"\n测试get_doctor_by_id方法...")
            doctor_by_id = doctor_service.get_doctor_by_id(doctor_id)
            if doctor_by_id:
                print(f"✅ 成功获取医生: {doctor_by_id.name}")
                print(f"  - 当前咨询数: {doctor_by_id.current_consultation_count}")
            else:
                print("❌ 获取医生失败")
        else:
            print("❌ 没有找到医生记录")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_doctor_profile()
