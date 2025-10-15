#!/usr/bin/env python3
"""
更新现有医生记录，添加current_consultation_count字段
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.mongo_dao import mongo_dao
from bson import ObjectId

def update_doctor_records():
    """更新医生记录"""
    print("=== 更新医生记录，添加current_consultation_count字段 ===")
    
    try:
        # 获取所有医生记录
        doctors = mongo_dao._MongoDao__db["doctors"].find({})
        updated_count = 0
        
        for doctor in doctors:
            doctor_id = str(doctor["_id"])
            
            # 检查是否已经有current_consultation_count字段
            if "current_consultation_count" not in doctor:
                # 计算当前咨询数量
                current_count = mongo_dao._MongoDao__db["consultations"].count_documents({
                    "assigned_doctor_id": doctor_id,
                    "status": {"$in": ["in_progress", "paid"]}
                })
                
                # 更新医生记录
                mongo_dao._MongoDao__db["doctors"].update_one(
                    {"_id": ObjectId(doctor_id)},
                    {"$set": {"current_consultation_count": current_count}}
                )
                
                print(f"✅ 更新医生 {doctor.get('name', 'Unknown')} (ID: {doctor_id}) - 当前咨询数: {current_count}")
                updated_count += 1
            else:
                print(f"⏭️  医生 {doctor.get('name', 'Unknown')} (ID: {doctor_id}) 已有current_consultation_count字段")
        
        print(f"\n=== 更新完成 ===")
        print(f"总共更新了 {updated_count} 个医生记录")
        
    except Exception as e:
        print(f"❌ 更新医生记录时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_doctor_records()
