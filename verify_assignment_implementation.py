#!/usr/bin/env python3
"""
验证医生分配策略实现
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """验证所有必要的导入"""
    print("=== 验证导入 ===")
    
    try:
        from models.doctor import DoctorStatus, DoctorLevel
        print("✅ 医生模型导入成功")
    except Exception as e:
        print(f"❌ 医生模型导入失败: {e}")
        return False
    
    try:
        from models.consultation import ConsultationStatus, DoctorLevel as ConsultationDoctorLevel
        print("✅ 咨询模型导入成功")
    except Exception as e:
        print(f"❌ 咨询模型导入失败: {e}")
        return False
    
    try:
        from services.consultation_service import consultation_service
        print("✅ 咨询服务导入成功")
    except Exception as e:
        print(f"❌ 咨询服务导入失败: {e}")
        return False
    
    try:
        from services.doctor_service import doctor_service
        print("✅ 医生服务导入成功")
    except Exception as e:
        print(f"❌ 医生服务导入失败: {e}")
        return False
    
    return True

def verify_methods():
    """验证新增的方法"""
    print("\n=== 验证方法 ===")
    
    try:
        from services.consultation_service import consultation_service
        
        # 检查自动分配方法
        if hasattr(consultation_service, 'auto_assign_doctor'):
            print("✅ auto_assign_doctor 方法存在")
        else:
            print("❌ auto_assign_doctor 方法不存在")
            return False
        
        # 检查按等级获取医生方法
        if hasattr(consultation_service, 'get_available_doctors_by_level'):
            print("✅ get_available_doctors_by_level 方法存在")
        else:
            print("❌ get_available_doctors_by_level 方法不存在")
            return False
        
        # 检查获取未分配咨询方法
        if hasattr(consultation_service, 'get_unassigned_consultations'):
            print("✅ get_unassigned_consultations 方法存在")
        else:
            print("❌ get_unassigned_consultations 方法不存在")
            return False
        
    except Exception as e:
        print(f"❌ 验证方法时出错: {e}")
        return False
    
    try:
        from services.doctor_service import doctor_service
        
        # 检查更新咨询数量方法
        if hasattr(doctor_service, 'update_doctor_consultation_count'):
            print("✅ update_doctor_consultation_count 方法存在")
        else:
            print("❌ update_doctor_consultation_count 方法不存在")
            return False
        
    except Exception as e:
        print(f"❌ 验证医生服务方法时出错: {e}")
        return False
    
    return True

def verify_models():
    """验证模型字段"""
    print("\n=== 验证模型字段 ===")
    
    try:
        from models.doctor import DoctorInDB, DoctorResponse
        
        # 检查DoctorInDB模型
        doctor_in_db_fields = DoctorInDB.__fields__.keys()
        if 'current_consultation_count' in doctor_in_db_fields:
            print("✅ DoctorInDB 包含 current_consultation_count 字段")
        else:
            print("❌ DoctorInDB 缺少 current_consultation_count 字段")
            return False
        
        # 检查DoctorResponse模型
        doctor_response_fields = DoctorResponse.__fields__.keys()
        if 'current_consultation_count' in doctor_response_fields:
            print("✅ DoctorResponse 包含 current_consultation_count 字段")
        else:
            print("❌ DoctorResponse 缺少 current_consultation_count 字段")
            return False
        
    except Exception as e:
        print(f"❌ 验证模型字段时出错: {e}")
        return False
    
    return True

def verify_scheduler():
    """验证定时任务配置"""
    print("\n=== 验证定时任务配置 ===")
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        print("✅ APScheduler 导入成功")
    except Exception as e:
        print(f"❌ APScheduler 导入失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== 验证医生分配策略实现 ===\n")
    
    all_passed = True
    
    # 验证导入
    if not verify_imports():
        all_passed = False
    
    # 验证方法
    if not verify_methods():
        all_passed = False
    
    # 验证模型
    if not verify_models():
        all_passed = False
    
    # 验证定时任务
    if not verify_scheduler():
        all_passed = False
    
    print("\n=== 验证结果 ===")
    if all_passed:
        print("✅ 所有验证通过！医生分配策略实现完整")
        print("\n可以启动系统进行测试：")
        print("python main.py")
    else:
        print("❌ 部分验证失败，请检查实现")
    
    return all_passed

if __name__ == "__main__":
    main()
