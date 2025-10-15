#!/usr/bin/env python3
"""
测试医生认证状态
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doctor_auth():
    """测试医生认证"""
    print("=== 测试医生认证状态 ===\n")
    
    try:
        from services.doctor_service import doctor_service
        from models.doctor import DoctorInDB
        
        # 获取所有医生
        doctors = list(doctor_service.dao._MongoDao__db["doctors"].find({}))
        print(f"数据库中的医生数量: {len(doctors)}")
        
        if doctors:
            # 测试第一个医生
            doctor_data = doctors[0]
            doctor_id = str(doctor_data["_id"])
            doctor_name = doctor_data.get("name", "Unknown")
            print(f"测试医生: {doctor_name} (ID: {doctor_id})")
            
            # 测试get_doctor_by_id
            print("\n1. 测试get_doctor_by_id...")
            try:
                doctor = doctor_service.get_doctor_by_id(doctor_id)
                if doctor:
                    print(f"✅ 成功获取医生: {doctor.name}")
                    print(f"  - 状态: {doctor.status}")
                    print(f"  - 是否激活: {doctor.is_active}")
                else:
                    print("❌ 获取医生失败")
            except Exception as e:
                print(f"❌ get_doctor_by_id失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 测试医生登录
            print("\n2. 测试医生登录...")
            try:
                updated_doctor = doctor_service.update_doctor_login(doctor_id)
                if updated_doctor:
                    print(f"✅ 医生登录成功: {updated_doctor.name}")
                    print(f"  - 登录次数: {updated_doctor.login_count}")
                    print(f"  - 最后登录: {updated_doctor.last_login}")
                else:
                    print("❌ 医生登录失败")
            except Exception as e:
                print(f"❌ 医生登录失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 测试获取医生咨询
            print("\n3. 测试获取医生咨询...")
            try:
                consultations = doctor_service.get_doctor_consultations(doctor_id, 0, 10)
                print(f"✅ 成功获取咨询列表: {len(consultations)} 个咨询")
                for i, consultation in enumerate(consultations[:3]):
                    print(f"  - 咨询{i+1}: {consultation.get('id', 'Unknown')} - 状态: {consultation.get('status', 'Unknown')}")
            except Exception as e:
                print(f"❌ 获取医生咨询失败: {e}")
                import traceback
                traceback.print_exc()
            
        else:
            print("❌ 没有找到医生记录")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_doctor_auth()
