#!/usr/bin/env python3
"""
修复医生记录，添加缺失的字段
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_doctor_records():
    """修复医生记录"""
    print("=== 修复医生记录 ===")
    
    try:
        from utils.mongo_dao import mongo_dao
        from bson import ObjectId
        
        # 获取所有医生记录
        doctors = list(mongo_dao._MongoDao__db["doctors"].find({}))
        print(f"找到 {len(doctors)} 个医生记录")
        
        updated_count = 0
        for doctor in doctors:
            doctor_id = str(doctor["_id"])
            doctor_name = doctor.get("name", "Unknown")
            
            # 检查并添加缺失的字段
            updates = {}
            
            # 添加current_consultation_count字段
            if "current_consultation_count" not in doctor:
                # 计算当前咨询数量
                current_count = mongo_dao._MongoDao__db["consultations"].count_documents({
                    "assigned_doctor_id": doctor_id,
                    "status": {"$in": ["in_progress", "paid"]}
                })
                updates["current_consultation_count"] = current_count
                print(f"  - {doctor_name}: 添加current_consultation_count = {current_count}")
            
            # 添加其他可能缺失的字段
            if "total_consultations" not in doctor:
                updates["total_consultations"] = 0
                print(f"  - {doctor_name}: 添加total_consultations = 0")
            
            if "total_earnings" not in doctor:
                updates["total_earnings"] = 0.0
                print(f"  - {doctor_name}: 添加total_earnings = 0.0")
            
            if "rating" not in doctor:
                updates["rating"] = 5.0
                print(f"  - {doctor_name}: 添加rating = 5.0")
            
            if "rating_count" not in doctor:
                updates["rating_count"] = 0
                print(f"  - {doctor_name}: 添加rating_count = 0")
            
            if "is_active" not in doctor:
                updates["is_active"] = True
                print(f"  - {doctor_name}: 添加is_active = True")
            
            # 执行更新
            if updates:
                mongo_dao._MongoDao__db["doctors"].update_one(
                    {"_id": ObjectId(doctor_id)},
                    {"$set": updates}
                )
                updated_count += 1
                print(f"✅ 更新完成: {doctor_name}")
            else:
                print(f"⏭️  无需更新: {doctor_name}")
        
        print(f"\n=== 修复完成 ===")
        print(f"总共更新了 {updated_count} 个医生记录")
        
    except Exception as e:
        print(f"❌ 修复医生记录时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_doctor_records()
