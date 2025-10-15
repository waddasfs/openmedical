#!/usr/bin/env python3
"""
简单的医生测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doctor_simple():
    """简单测试医生功能"""
    print("=== 简单医生测试 ===\n")
    
    try:
        from services.doctor_service import doctor_service
        from models.doctor import DoctorInDB
        
        # 直接使用MongoDB查询获取医生
        doctors = doctor_service.dao._MongoDao__db["doctors"].find({})
        doctor_list = list(doctors)
        print(f"数据库中的医生数量: {len(doctor_list)}")
        
        if doctor_list:
            # 测试第一个医生
            doctor_data = doctor_list[0]
            doctor_id = str(doctor_data["_id"])
            print(f"测试医生ID: {doctor_id}")
            print(f"医生姓名: {doctor_data.get('name', 'Unknown')}")
            
            # 确保包含current_consultation_count字段
            if "current_consultation_count" not in doctor_data:
                doctor_data["current_consultation_count"] = 0
                print("添加了current_consultation_count字段")
            else:
                print(f"已有current_consultation_count字段: {doctor_data['current_consultation_count']}")
            
            # 尝试创建DoctorInDB对象
            doctor_data["id"] = doctor_data.pop("_id")
            try:
                doctor = DoctorInDB(**doctor_data)
                print(f"✅ 成功创建DoctorInDB对象: {doctor.name}")
                print(f"  - 当前咨询数: {doctor.current_consultation_count}")
                print(f"  - 总咨询数: {doctor.total_consultations}")
                print(f"  - 状态: {doctor.status}")
            except Exception as e:
                print(f"❌ 创建DoctorInDB对象失败: {e}")
                print(f"医生数据字段: {list(doctor_data.keys())}")
            
            # 测试get_doctor_by_id方法
            print(f"\n测试get_doctor_by_id方法...")
            try:
                doctor_by_id = doctor_service.get_doctor_by_id(doctor_id)
                if doctor_by_id:
                    print(f"✅ 成功获取医生: {doctor_by_id.name}")
                    print(f"  - 当前咨询数: {doctor_by_id.current_consultation_count}")
                else:
                    print("❌ 获取医生失败")
            except Exception as e:
                print(f"❌ get_doctor_by_id失败: {e}")
        else:
            print("❌ 没有找到医生记录")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_doctor_simple()
