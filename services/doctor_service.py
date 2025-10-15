#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医生服务类
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from utils.mongo_dao import mongo_dao
from models.doctor import (
    DoctorInDB, DoctorCreate, DoctorUpdate, DoctorResponse, 
    DoctorEarnings, DoctorAssignment, DoctorLevel, DoctorStatus, DoctorSpecialty
)
from models.consultation import ConsultationStatus

class DoctorService:
    """医生服务类"""
    
    COLLECTION_NAME = "doctors"
    ASSIGNMENT_COLLECTION = "doctor_assignments"
    
    def __init__(self):
        self.dao = mongo_dao
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保数据库索引存在"""
        try:
            # 为google_id创建唯一索引
            self.dao.create_index(self.COLLECTION_NAME, "google_id")
            # 为email创建索引
            self.dao.create_index(self.COLLECTION_NAME, "email")
            # 为license_number创建唯一索引
            self.dao.create_index(self.COLLECTION_NAME, "license_number")
            # 为status创建索引
            self.dao.create_index(self.COLLECTION_NAME, "status")
            # 为specialties创建索引
            self.dao.create_index(self.COLLECTION_NAME, "specialties")
            # 为level创建索引
            self.dao.create_index(self.COLLECTION_NAME, "level")
        except Exception as e:
            print(f"创建医生索引时出错: {e}")
    
    def create_doctor(self, doctor_data: DoctorCreate) -> DoctorInDB:
        """创建新医生"""
        try:
            # 检查医生是否已存在
            existing_doctor = self.get_doctor_by_google_id(doctor_data.google_id)
            if existing_doctor:
                # 更新最后登录时间
                print(f"医生已存在，更新登录信息: {existing_doctor.id}")
                updated_doctor = self.update_doctor_login(str(existing_doctor.id))
                if updated_doctor:
                    return updated_doctor
                else:
                    print("更新医生登录信息失败，返回原医生信息")
                    return existing_doctor
            
            # 创建新医生
            doctor_dict = doctor_data.dict()
            doctor_dict.update({
                "status": DoctorStatus.OFFLINE,
                "total_consultations": 0,
                "total_earnings": 0.0,
                "rating": 5.0,
                "rating_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                "login_count": 1,
                "is_active": True
            })
            
            # 插入数据库
            self.dao.insert(self.COLLECTION_NAME, doctor_dict)
            print(f"新医生创建成功: {doctor_data.email}")
            
            # 返回创建的医生
            new_doctor = self.get_doctor_by_google_id(doctor_data.google_id)
            if new_doctor:
                return new_doctor
            else:
                print("创建医生后无法获取医生信息")
                return None
                
        except Exception as e:
            print(f"创建医生时出错: {e}")
            return None
    
    def get_doctor_by_google_id(self, google_id: str) -> Optional[DoctorInDB]:
        """根据Google ID获取医生"""
        doctors = self.dao.search(self.COLLECTION_NAME, "google_id", google_id)
        if doctors:
            doctor_data = doctors[0]
            doctor_data["id"] = doctor_data.pop("_id")
            
            # 确保包含current_consultation_count字段
            if "current_consultation_count" not in doctor_data:
                doctor_data["current_consultation_count"] = 0
                
            return DoctorInDB(**doctor_data)
        return None
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[DoctorInDB]:
        """根据医生ID获取医生"""
        try:
            # 确保doctor_id是有效的ObjectId
            if isinstance(doctor_id, str):
                doctor_id = ObjectId(doctor_id)
            
            doctors = self.dao.search(self.COLLECTION_NAME, "_id", doctor_id)
            if doctors:
                doctor_data = doctors[0]
                doctor_data["id"] = doctor_data.pop("_id")
                
                # 确保包含current_consultation_count字段
                if "current_consultation_count" not in doctor_data:
                    doctor_data["current_consultation_count"] = 0
                
                return DoctorInDB(**doctor_data)
        except Exception as e:
            print(f"获取医生时出错: {e}, doctor_id: {doctor_id}")
        return None
    
    def get_doctor_by_email(self, email: str) -> Optional[DoctorInDB]:
        """根据邮箱获取医生"""
        doctors = self.dao.search(self.COLLECTION_NAME, "email", email)
        if doctors:
            doctor_data = doctors[0]
            doctor_data["id"] = doctor_data.pop("_id")
            
            # 确保包含current_consultation_count字段
            if "current_consultation_count" not in doctor_data:
                doctor_data["current_consultation_count"] = 0
                
            return DoctorInDB(**doctor_data)
        return None
    
    def update_doctor_login(self, doctor_id: str) -> Optional[DoctorInDB]:
        """更新医生登录信息"""
        try:
            # 使用MongoDB的$inc操作符增加登录次数
            result = self.dao._MongoDao__db[self.COLLECTION_NAME].update_one(
                {"_id": ObjectId(doctor_id)}, 
                {
                    "$set": {
                        "last_login": datetime.utcnow(), 
                        "updated_at": datetime.utcnow(),
                        "status": DoctorStatus.ACTIVE
                    }, 
                    "$inc": {"login_count": 1}
                }
            )
            
            if result.modified_count > 0:
                return self.get_doctor_by_id(doctor_id)
            else:
                print(f"更新医生登录信息失败，医生ID: {doctor_id}")
        except Exception as e:
            print(f"更新医生登录信息时出错: {e}")
        return None
    
    def update_doctor(self, doctor_id: str, doctor_data: DoctorUpdate) -> Optional[DoctorInDB]:
        """更新医生信息"""
        try:
            update_dict = doctor_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            result = self.dao.update(
                self.COLLECTION_NAME, 
                "_id", 
                ObjectId(doctor_id), 
                update_dict
            )
            
            if result:
                return self.get_doctor_by_id(doctor_id)
        except Exception as e:
            print(f"更新医生时出错: {e}")
        return None
    
    def get_available_doctors(self, specialty: Optional[DoctorSpecialty] = None, 
                            level: Optional[DoctorLevel] = None) -> List[DoctorInDB]:
        """获取可用的医生列表"""
        try:
            query = {
                "status": {"$in": [DoctorStatus.ACTIVE, DoctorStatus.BUSY]},
                "is_active": True
            }
            
            if specialty:
                query["specialties"] = specialty.value
            
            if level:
                query["level"] = level.value
            
            doctors = self.dao._MongoDao__db[self.COLLECTION_NAME].find(query)
            result = []
            for doctor in doctors:
                doctor["id"] = str(doctor.pop("_id"))
                # 计算当前咨询数量
                current_count = self.dao._MongoDao__db["consultations"].count_documents({
                    "assigned_doctor_id": doctor["id"],
                    "status": {"$in": [ConsultationStatus.IN_PROGRESS.value, ConsultationStatus.PAID.value]}
                })
                doctor["current_consultation_count"] = current_count
                result.append(doctor)  # 返回字典而不是DoctorInDB对象
            return result
        except Exception as e:
            print(f"获取可用医生时出错: {e}")
            return []
    
    def assign_doctor_to_consultation(self, doctor_id: str, consultation_id: str) -> bool:
        """分配医生到咨询"""
        try:
            # 创建分配记录
            assignment_dict = {
                "doctor_id": doctor_id,
                "consultation_id": consultation_id,
                "assigned_at": datetime.utcnow(),
                "status": "assigned",
                "created_at": datetime.utcnow()
            }
            
            self.dao.insert(self.ASSIGNMENT_COLLECTION, assignment_dict)
            
            # 更新咨询记录的分配医生ID
            from services.consultation_service import consultation_service
            consultation_service.dao.update(
                "consultations",
                "_id",
                ObjectId(consultation_id),
                {
                    "assigned_doctor_id": doctor_id,
                    "updated_at": datetime.utcnow()
                }
            )
            
            # 更新医生状态为忙碌
            self.dao.update(
                self.COLLECTION_NAME,
                "_id",
                ObjectId(doctor_id),
                {
                    "status": DoctorStatus.BUSY,
                    "updated_at": datetime.utcnow()
                }
            )
            
            # 更新医生当前咨询数量
            self.update_doctor_consultation_count(doctor_id)
            
            return True
        except Exception as e:
            print(f"分配医生时出错: {e}")
            return False
    
    def get_doctor_consultations(self, doctor_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取医生的咨询列表"""
        try:
            # 获取分配给该医生的咨询
            assignments = self.dao._MongoDao__db[self.ASSIGNMENT_COLLECTION].find(
                {"doctor_id": doctor_id}
            ).sort("assigned_at", -1).skip(skip).limit(limit)
            
            consultation_ids = [assignment["consultation_id"] for assignment in assignments]
            
            if not consultation_ids:
                return []
            
            # 获取咨询详情
            consultations = self.dao._MongoDao__db["consultations"].find(
                {"_id": {"$in": [ObjectId(cid) for cid in consultation_ids]}}
            )
            
            result = []
            for consultation in consultations:
                consultation["id"] = str(consultation.pop("_id"))
                result.append(consultation)
            
            return result
        except Exception as e:
            print(f"获取医生咨询列表时出错: {e}")
            return []
    
    def get_doctor_earnings(self, doctor_id: str) -> DoctorEarnings:
        """获取医生收入统计"""
        try:
            # 获取医生基本信息
            doctor = self.get_doctor_by_id(doctor_id)
            if not doctor:
                return None
            
            # 计算时间范围
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=today_start.weekday())
            month_start = today_start.replace(day=1)
            
            # 获取该医生的所有已完成咨询
            completed_consultations = self.dao._MongoDao__db["consultations"].find({
                "assigned_doctor_id": doctor_id,
                "status": ConsultationStatus.COMPLETED.value
            })
            
            total_earnings = 0.0
            monthly_earnings = 0.0
            weekly_earnings = 0.0
            daily_earnings = 0.0
            completed_count = 0
            
            for consultation in completed_consultations:
                earnings = consultation.get("price_usdt", 0.0)
                total_earnings += earnings
                completed_count += 1
                
                created_at = consultation.get("created_at")
                if created_at:
                    if created_at >= month_start:
                        monthly_earnings += earnings
                    if created_at >= week_start:
                        weekly_earnings += earnings
                    if created_at >= today_start:
                        daily_earnings += earnings
            
            # 获取待处理咨询数量
            pending_count = self.dao._MongoDao__db["consultations"].count_documents({
                "assigned_doctor_id": doctor_id,
                "status": {"$in": [ConsultationStatus.PAID.value, ConsultationStatus.IN_PROGRESS.value]}
            })
            
            return DoctorEarnings(
                doctor_id=doctor_id,
                total_earnings=total_earnings,
                monthly_earnings=monthly_earnings,
                weekly_earnings=weekly_earnings,
                daily_earnings=daily_earnings,
                total_consultations=doctor.total_consultations,
                completed_consultations=completed_count,
                pending_consultations=pending_count,
                last_updated=now
            )
        except Exception as e:
            print(f"获取医生收入统计时出错: {e}")
            return None
    
    def update_doctor_earnings(self, doctor_id: str, earnings: float):
        """更新医生收入"""
        try:
            self.dao._MongoDao__db[self.COLLECTION_NAME].update_one(
                {"_id": ObjectId(doctor_id)},
                {
                    "$inc": {
                        "total_earnings": earnings,
                        "total_consultations": 1
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            print(f"更新医生收入时出错: {e}")
    
    def update_doctor_consultation_count(self, doctor_id: str):
        """更新医生当前咨询数量"""
        try:
            # 计算当前进行中的咨询数量
            current_count = self.dao._MongoDao__db["consultations"].count_documents({
                "assigned_doctor_id": doctor_id,
                "status": {"$in": [ConsultationStatus.IN_PROGRESS.value, ConsultationStatus.PAID.value]}
            })
            
            # 更新医生记录
            self.dao._MongoDao__db[self.COLLECTION_NAME].update_one(
                {"_id": ObjectId(doctor_id)},
                {
                    "$set": {
                        "current_consultation_count": current_count,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            print(f"医生 {doctor_id} 当前咨询数量更新为: {current_count}")
        except Exception as e:
            print(f"更新医生咨询数量时出错: {e}")
    
    def set_doctor_status(self, doctor_id: str, status: DoctorStatus):
        """设置医生状态"""
        try:
            self.dao.update(
                self.COLLECTION_NAME,
                "_id",
                ObjectId(doctor_id),
                {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            )
            return True
        except Exception as e:
            print(f"设置医生状态时出错: {e}")
            return False
    
    def get_all_doctors(self, skip: int = 0, limit: int = 100) -> List[DoctorInDB]:
        """获取所有医生（分页）"""
        try:
            doctors = self.dao._MongoDao__db[self.COLLECTION_NAME].find({}).skip(skip).limit(limit)
            result = []
            for doctor in doctors:
                doctor["id"] = doctor.pop("_id")
                result.append(DoctorInDB(**doctor))
            return result
        except Exception as e:
            print(f"获取医生列表时出错: {e}")
            return []
    
    def search_doctors(self, query: dict, skip: int = 0, limit: int = 100) -> List[DoctorInDB]:
        """搜索医生"""
        try:
            doctors = self.dao._MongoDao__db[self.COLLECTION_NAME].find(query).skip(skip).limit(limit)
            result = []
            for doctor in doctors:
                doctor["id"] = doctor.pop("_id")
                result.append(DoctorInDB(**doctor))
            return result
        except Exception as e:
            print(f"搜索医生时出错: {e}")
            return []

# 创建全局医生服务实例
doctor_service = DoctorService()
