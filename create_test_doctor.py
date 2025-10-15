#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试医生账户
"""

from services.doctor_service import doctor_service
from models.doctor import DoctorCreate, DoctorLevel, DoctorSpecialty

def create_test_doctors():
    """创建测试医生账户"""
    print("=== 创建测试医生账户 ===")
    
    # 测试医生数据
    test_doctors = [
        {
            "google_id": "test_google_doctor_001",
            "name": "张医生",
            "email": "zhang.doctor@test.com",
            "picture": "https://via.placeholder.com/150/667eea/ffffff?text=张",
            "license_number": "DOC001",
            "hospital": "北京协和医院",
            "department": "内科",
            "specialties": [DoctorSpecialty.GENERAL],
            "level": DoctorLevel.NORMAL,
            "experience_years": 5,
            "introduction": "擅长内科常见疾病的诊断和治疗，具有丰富的临床经验。",
            "consultation_fee": 50.0
        },
        {
            "google_id": "test_google_doctor_002", 
            "name": "李医生",
            "email": "li.doctor@test.com",
            "picture": "https://via.placeholder.com/150/764ba2/ffffff?text=李",
            "license_number": "DOC002",
            "hospital": "上海华山医院",
            "department": "心内科",
            "specialties": [DoctorSpecialty.CARDIOLOGY],
            "level": DoctorLevel.SENIOR,
            "experience_years": 12,
            "introduction": "心内科专家，擅长心血管疾病的诊断和治疗，在介入治疗方面有丰富经验。",
            "consultation_fee": 100.0
        },
        {
            "google_id": "test_google_doctor_003",
            "name": "王医生", 
            "email": "wang.doctor@test.com",
            "picture": "https://via.placeholder.com/150/28a745/ffffff?text=王",
            "license_number": "DOC003",
            "hospital": "广州中山医院",
            "department": "神经科",
            "specialties": [DoctorSpecialty.NEUROLOGY],
            "level": DoctorLevel.EXPERT,
            "experience_years": 20,
            "introduction": "神经科专家，在脑血管疾病、癫痫等神经系统疾病方面有深入研究。",
            "consultation_fee": 200.0
        }
    ]
    
    created_doctors = []
    
    for doctor_data in test_doctors:
        try:
            # 检查医生是否已存在
            existing_doctor = doctor_service.get_doctor_by_google_id(doctor_data["google_id"])
            if existing_doctor:
                print(f"⚠️  医生 {doctor_data['name']} 已存在，跳过创建")
                created_doctors.append(existing_doctor)
                continue
            
            # 创建医生
            doctor_create = DoctorCreate(**doctor_data)
            doctor = doctor_service.create_doctor(doctor_create)
            
            if doctor:
                print(f"✅ 成功创建医生: {doctor.name}")
                print(f"   - 邮箱: {doctor.email}")
                print(f"   - 执业证号: {doctor.license_number}")
                print(f"   - 医院: {doctor.hospital}")
                print(f"   - 科室: {doctor.department}")
                print(f"   - 等级: {doctor.level.value}")
                print(f"   - 专业: {[s.value for s in doctor.specialties]}")
                print(f"   - 咨询费: {doctor.consultation_fee} USDT")
                print()
                created_doctors.append(doctor)
            else:
                print(f"❌ 创建医生 {doctor_data['name']} 失败")
                
        except Exception as e:
            print(f"❌ 创建医生 {doctor_data['name']} 时出错: {e}")
    
    print(f"\n=== 创建完成 ===")
    print(f"成功创建 {len(created_doctors)} 个医生账户")
    
    if created_doctors:
        print("\n测试登录信息:")
        print("可以使用以下Google ID进行测试登录:")
        for doctor in created_doctors:
            print(f"- {doctor.name}: {doctor.google_id}")
    
    return created_doctors

def main():
    """主函数"""
    try:
        created_doctors = create_test_doctors()
        
        print("\n=== 使用说明 ===")
        print("1. 启动FastAPI服务: python main.py")
        print("2. 访问医生登录页面: http://localhost:5000/doctor/login")
        print("3. 使用上述Google ID进行登录测试")
        print("4. 登录成功后可以访问医生仪表板等功能")
        
    except Exception as e:
        print(f"❌ 创建测试医生时出错: {e}")
        print("请确保:")
        print("1. MongoDB服务正在运行")
        print("2. 已正确配置数据库连接")
        print("3. 已安装所有必要的依赖包")

if __name__ == "__main__":
    main()
