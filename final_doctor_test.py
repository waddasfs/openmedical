#!/usr/bin/env python3
"""
最终医生测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doctor_final():
    """最终测试医生功能"""
    print("=== 最终医生测试 ===\n")
    
    try:
        from services.doctor_service import doctor_service
        from models.doctor import DoctorInDB, DoctorResponse
        
        # 获取所有医生
        doctors = list(doctor_service.dao._MongoDao__db["doctors"].find({}))
        print(f"数据库中的医生数量: {len(doctors)}")
        
        if doctors:
            # 测试第一个医生
            doctor_data = doctors[0]
            doctor_id = str(doctor_data["_id"])
            doctor_name = doctor_data.get("name", "Unknown")
            print(f"测试医生: {doctor_name} (ID: {doctor_id})")
            
            # 显示当前字段
            print(f"当前字段: {list(doctor_data.keys())}")
            
            # 确保包含必要字段
            if "current_consultation_count" not in doctor_data:
                doctor_data["current_consultation_count"] = 0
            if "total_consultations" not in doctor_data:
                doctor_data["total_consultations"] = 0
            if "total_earnings" not in doctor_data:
                doctor_data["total_earnings"] = 0.0
            if "rating" not in doctor_data:
                doctor_data["rating"] = 5.0
            if "rating_count" not in doctor_data:
                doctor_data["rating_count"] = 0
            if "is_active" not in doctor_data:
                doctor_data["is_active"] = True
            
            # 测试创建DoctorInDB对象
            print("\n1. 测试创建DoctorInDB对象...")
            try:
                doctor_data_copy = doctor_data.copy()
                doctor_data_copy["id"] = doctor_data_copy.pop("_id")
                doctor = DoctorInDB(**doctor_data_copy)
                print(f"✅ 成功创建DoctorInDB对象: {doctor.name}")
                print(f"  - 当前咨询数: {doctor.current_consultation_count}")
                print(f"  - 总咨询数: {doctor.total_consultations}")
                print(f"  - 总收入: {doctor.total_earnings}")
                print(f"  - 评分: {doctor.rating}")
                print(f"  - 状态: {doctor.status}")
            except Exception as e:
                print(f"❌ 创建DoctorInDB对象失败: {e}")
                return False
            
            # 测试get_doctor_by_id方法
            print("\n2. 测试get_doctor_by_id方法...")
            try:
                doctor_by_id = doctor_service.get_doctor_by_id(doctor_id)
                if doctor_by_id:
                    print(f"✅ 成功获取医生: {doctor_by_id.name}")
                    print(f"  - 当前咨询数: {doctor_by_id.current_consultation_count}")
                else:
                    print("❌ 获取医生失败")
                    return False
            except Exception as e:
                print(f"❌ get_doctor_by_id失败: {e}")
                return False
            
            # 测试创建DoctorResponse对象
            print("\n3. 测试创建DoctorResponse对象...")
            try:
                doctor_response = DoctorResponse(
                    id=str(doctor.id),
                    google_id=doctor.google_id,
                    name=doctor.name,
                    email=doctor.email,
                    picture=doctor.picture,
                    license_number=doctor.license_number,
                    hospital=doctor.hospital,
                    department=doctor.department,
                    specialties=doctor.specialties,
                    level=doctor.level,
                    experience_years=doctor.experience_years,
                    introduction=doctor.introduction,
                    consultation_fee=doctor.consultation_fee,
                    status=doctor.status,
                    total_consultations=doctor.total_consultations,
                    current_consultation_count=doctor.current_consultation_count,
                    total_earnings=doctor.total_earnings,
                    rating=doctor.rating,
                    rating_count=doctor.rating_count,
                    created_at=doctor.created_at,
                    updated_at=doctor.updated_at,
                    last_login=doctor.last_login,
                    login_count=doctor.login_count,
                    is_active=doctor.is_active
                )
                print(f"✅ 成功创建DoctorResponse对象: {doctor_response.name}")
                print(f"  - 当前咨询数: {doctor_response.current_consultation_count}")
            except Exception as e:
                print(f"❌ 创建DoctorResponse对象失败: {e}")
                return False
            
            print("\n✅ 所有测试通过！")
            return True
        else:
            print("❌ 没有找到医生记录")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_doctor_final()
    if success:
        print("\n🎉 医生档案修复成功！现在可以正常使用医生端功能了。")
    else:
        print("\n❌ 医生档案修复失败，请检查错误信息。")
