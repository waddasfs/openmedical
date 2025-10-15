#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医疗咨询服务类
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from utils.mongo_dao import mongo_dao
from models.consultation import (
    ConsultationInDB, ConsultationCreate, ConsultationResponse,
    PaymentOrder, PaymentOrderResponse, ChatMessage, ChatMessageResponse,
    ConsultationMode, DoctorLevel, ConsultationStatus, PaymentStatus,
    ConsultationPackage
)
from models.doctor import DoctorStatus

class ConsultationService:
    """医疗咨询服务类"""
    
    CONSULTATION_COLLECTION = "consultations"
    PAYMENT_ORDER_COLLECTION = "payment_orders"
    CHAT_MESSAGE_COLLECTION = "chat_messages"
    
    # 咨询套餐配置
    CONSULTATION_PACKAGES = {
        "normal": ConsultationPackage(
            level=DoctorLevel.NORMAL,
            name="普通医生咨询",
            price_usdt=10.0,
            description="普通医生提供基础医疗咨询服务",
            features=["基础诊断", "用药建议", "生活指导"],
            response_time="24小时内",
            consultation_duration="30分钟"
        ),
        "senior": ConsultationPackage(
            level=DoctorLevel.SENIOR,
            name="高级医生咨询",
            price_usdt=50.0,
            description="高级医生提供专业医疗咨询服务",
            features=["专业诊断", "详细治疗方案", "复查建议", "紧急情况处理"],
            response_time="12小时内",
            consultation_duration="60分钟"
        ),
        "expert": ConsultationPackage(
            level=DoctorLevel.EXPERT,
            name="专家医生咨询",
            price_usdt=100.0,
            description="专家医生提供顶级医疗咨询服务",
            features=["专家诊断", "个性化治疗方案", "长期跟踪", "多学科会诊"],
            response_time="6小时内",
            consultation_duration="90分钟"
        )
    }
    
    def __init__(self):
        self.dao = mongo_dao
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """确保数据库索引存在"""
        try:
            # 为consultation_id创建索引
            self.dao.create_index(self.CONSULTATION_COLLECTION, "user_id")
            self.dao.create_index(self.CONSULTATION_COLLECTION, "status")
            self.dao.create_index(self.PAYMENT_ORDER_COLLECTION, "consultation_id")
            self.dao.create_index(self.PAYMENT_ORDER_COLLECTION, "user_id")
            self.dao.create_index(self.CHAT_MESSAGE_COLLECTION, "consultation_id")
        except Exception as e:
            print(f"创建索引时出错: {e}")
    
    def get_consultation_packages(self) -> List[ConsultationPackage]:
        """获取所有咨询套餐"""
        return list(self.CONSULTATION_PACKAGES.values())
    
    def get_package_by_level(self, level: DoctorLevel) -> Optional[ConsultationPackage]:
        """根据等级获取咨询套餐"""
        return self.CONSULTATION_PACKAGES.get(level.value)
    
    def _normalize_consultation_data(self, consultation_data: dict) -> dict:
        """标准化咨询数据，确保所有必需字段都存在"""
        try:
            # 确保必需字段存在
            normalized = {
                "id": consultation_data.get("id"),
                "user_id": consultation_data.get("user_id", ""),
                "mode": consultation_data.get("mode", "onetime"),
                "disease_description": consultation_data.get("disease_description", ""),
                "symptoms": consultation_data.get("symptoms", ""),
                "medical_history": consultation_data.get("medical_history", ""),
                "attachments": consultation_data.get("attachments", []),
                "package_id": consultation_data.get("package_id"),
                "doctor_level": consultation_data.get("doctor_level"),
                "status": consultation_data.get("status", "pending"),
                "assigned_doctor_id": consultation_data.get("assigned_doctor_id"),
                "price_usdt": consultation_data.get("price_usdt", 0.0),  # 确保price_usdt字段存在
                "payment_order_id": consultation_data.get("payment_order_id"),
                "created_at": consultation_data.get("created_at"),
                "updated_at": consultation_data.get("updated_at"),
                "started_at": consultation_data.get("started_at"),
                "completed_at": consultation_data.get("completed_at")
            }
            
            # 确保price_usdt是数字类型
            if normalized["price_usdt"] is None:
                normalized["price_usdt"] = 0.0
            else:
                normalized["price_usdt"] = float(normalized["price_usdt"])
            
            # 确保attachments是列表
            if not isinstance(normalized["attachments"], list):
                normalized["attachments"] = []
            
            print(f"标准化后的咨询数据: {normalized}")
            return normalized
            
        except Exception as e:
            print(f"标准化咨询数据失败: {e}")
            print(f"原始数据: {consultation_data}")
            # 返回一个基本的有效数据结构
            return {
                "id": consultation_data.get("id", ""),
                "user_id": consultation_data.get("user_id", ""),
                "mode": "onetime",
                "disease_description": consultation_data.get("disease_description", ""),
                "symptoms": "",
                "medical_history": "",
                "attachments": [],
                "package_id": None,
                "doctor_level": None,
                "status": "pending",
                "assigned_doctor_id": None,
                "price_usdt": 0.0,
                "payment_order_id": None,
                "created_at": consultation_data.get("created_at"),
                "updated_at": consultation_data.get("updated_at"),
                "started_at": None,
                "completed_at": None
            }
    
    def create_consultation(self, user_id: str, consultation_data: ConsultationCreate) -> ConsultationInDB:
        """创建医疗咨询"""
        try:
            # 计算价格
            if consultation_data.mode == ConsultationMode.REALTIME:
                # 实时聊天模式：按分钟计费，先收取基础费用
                price_usdt = 20.0  # 基础费用
            else:
                # 一次性咨询模式：根据医生等级定价
                if not consultation_data.doctor_level:
                    raise ValueError("一次性咨询必须选择医生等级")
                package = self.get_package_by_level(consultation_data.doctor_level)
                if not package:
                    raise ValueError("无效的医生等级")
                price_usdt = package.price_usdt
            
            # 创建咨询记录字典
            consultation_dict = {
                "user_id": str(user_id),  # 确保是字符串
                "mode": consultation_data.mode.value,
                "disease_description": consultation_data.disease_description,
                "symptoms": consultation_data.symptoms or "",
                "medical_history": consultation_data.medical_history or "",
                "attachments": consultation_data.attachments or [],
                "package_id": consultation_data.package_id,
                "doctor_level": consultation_data.doctor_level.value if consultation_data.doctor_level else None,
                "status": ConsultationStatus.PENDING.value,
                "assigned_doctor_id": None,
                "price_usdt": float(price_usdt),  # 确保是浮点数
                "payment_order_id": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None
            }
            
            print(f"准备插入咨询记录到MongoDB: {consultation_dict}")
            
            # 插入数据库
            print(f"开始插入到集合: {self.CONSULTATION_COLLECTION}")
            result = self.dao.insert(self.CONSULTATION_COLLECTION, consultation_dict)
            print(f"MongoDB插入结果: {result}")
            print(f"插入结果类型: {type(result)}")
            
            # 验证数据是否插入成功
            if result and hasattr(result, 'inserted_id') and result.inserted_id:
                print(f"✅ 咨询记录已成功插入到MongoDB，文档ID: {result.inserted_id}")
                # 将插入的ID添加到字典中，用于后续查询
                consultation_dict["_id"] = result.inserted_id
            else:
                print("❌ 插入操作失败")
                print(f"结果详情: {result}")
                # 尝试直接查询验证
                print("尝试直接查询验证...")
                recent_consultations = self.dao.search(self.CONSULTATION_COLLECTION, "user_id", str(user_id))
                print(f"用户 {user_id} 的咨询记录数量: {len(recent_consultations)}")
                if recent_consultations:
                    latest = max(recent_consultations, key=lambda x: x.get('created_at', datetime.min))
                    print(f"最新的咨询记录: {latest}")
                    consultation_dict["_id"] = latest.get("_id")
                else:
                    print("❌ 未找到任何咨询记录")
                    return None
            
            # 直接使用插入的数据创建返回对象
            try:
                consultation_dict["id"] = consultation_dict.pop("_id")
                consultation = ConsultationInDB(**consultation_dict)
                print(f"咨询记录创建成功，ID: {consultation.id}")
                return consultation
            except Exception as e:
                print(f"创建ConsultationInDB对象失败: {e}")
                # 如果直接创建失败，尝试从数据库查询
                consultation = self.get_consultation_by_user_and_latest(user_id)
                if consultation:
                    print(f"从数据库查询到咨询记录，ID: {consultation.id}")
                    return consultation
                else:
                    print("无法获取创建的咨询记录")
                    return None
                
        except Exception as e:
            print(f"创建咨询时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_consultation_by_id(self, consultation_id: str) -> Optional[ConsultationInDB]:
        """根据ID获取咨询记录"""
        try:
            consultations = self.dao.search(self.CONSULTATION_COLLECTION, "_id", ObjectId(consultation_id))
            if consultations:
                consultation_data = consultations[0]
                consultation_data["id"] = consultation_data.pop("_id")
                
                # 使用标准化方法处理数据
                normalized_data = self._normalize_consultation_data(consultation_data)
                return ConsultationInDB(**normalized_data)
        except Exception as e:
            print(f"获取咨询记录时出错: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    def get_consultation_by_user_and_latest(self, user_id: str) -> Optional[ConsultationInDB]:
        """获取用户最新的咨询记录"""
        try:
            consultations = self.dao._MongoDao__db[self.CONSULTATION_COLLECTION].find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(1)
            
            for consultation in consultations:
                consultation["id"] = consultation.pop("_id")
                
                # 使用标准化方法处理数据
                normalized_data = self._normalize_consultation_data(consultation)
                return ConsultationInDB(**normalized_data)
        except Exception as e:
            print(f"获取用户咨询记录时出错: {e}")
        return None
    
    def get_user_consultations(self, user_id: str, skip: int = 0, limit: int = 20) -> List[ConsultationInDB]:
        """获取用户的咨询记录列表"""
        try:
            consultations = self.dao._MongoDao__db[self.CONSULTATION_COLLECTION].find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            result = []
            for consultation in consultations:
                # 转换_id为id
                consultation["id"] = consultation.pop("_id")
                
                # 确保所有必需字段都存在
                consultation_data = self._normalize_consultation_data(consultation)
                
                try:
                    consultation_obj = ConsultationInDB(**consultation_data)
                    result.append(consultation_obj)
                except Exception as e:
                    print(f"转换咨询记录失败: {e}")
                    print(f"问题数据: {consultation_data}")
                    # 跳过有问题的记录，继续处理其他记录
                    continue
            
            print(f"成功获取 {len(result)} 条咨询记录")
            return result
        except Exception as e:
            print(f"获取用户咨询列表时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def create_payment_order(self, consultation_id: str, user_id: str, usdt_address: str) -> PaymentOrder:
        """创建支付订单"""
        # 获取咨询记录
        consultation = self.get_consultation_by_id(consultation_id)
        if not consultation:
            raise ValueError("咨询记录不存在")
        
        if consultation.user_id != user_id:
            raise ValueError("无权限访问此咨询记录")
        
        # 生成二维码URL（这里使用在线二维码生成服务）
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={usdt_address}"
        
        # 创建支付订单
        payment_order_dict = {
            "consultation_id": consultation_id,
            "user_id": user_id,
            "amount_usdt": consultation.price_usdt,
            "usdt_address": usdt_address,
            "qr_code_url": qr_code_url,
            "status": PaymentStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24)  # 24小时过期
        }
        
        # 插入数据库
        self.dao.insert(self.PAYMENT_ORDER_COLLECTION, payment_order_dict)
        
        # 返回创建的支付订单
        return self.get_payment_order_by_consultation(consultation_id)
    
    def get_payment_order_by_consultation(self, consultation_id: str) -> Optional[PaymentOrder]:
        """根据咨询ID获取支付订单"""
        try:
            orders = self.dao.search(self.PAYMENT_ORDER_COLLECTION, "consultation_id", consultation_id)
            if orders:
                order_data = orders[0]
                order_data["id"] = order_data.pop("_id")
                return PaymentOrder(**order_data)
        except Exception as e:
            print(f"获取支付订单时出错: {e}")
        return None
    
    def check_payment_status(self, consultation_id: str) -> PaymentStatus:
        """检查支付状态（模拟实现，实际需要连接以太坊网络）"""
        # 这里应该连接以太坊网络检查交易状态
        # 为了演示，我们模拟一个简单的检查逻辑
        payment_order = self.get_payment_order_by_consultation(consultation_id)
        if not payment_order:
            return PaymentStatus.FAILED
        
        # 检查是否过期
        if datetime.utcnow() > payment_order.expires_at:
            self.update_payment_status(consultation_id, PaymentStatus.EXPIRED)
            return PaymentStatus.EXPIRED
        
        # 如果已经有支付状态，直接返回
        if payment_order.status != PaymentStatus.PENDING:
            return payment_order.status
        
        # 模拟支付检查（实际应该查询以太坊网络）
        # 为了演示，我们使用一个更保守的检查逻辑
        # 只有在特定条件下才认为支付成功（比如有交易哈希）
        if hasattr(payment_order, 'transaction_hash') and payment_order.transaction_hash:
            # 如果有交易哈希，验证交易
            self.update_payment_status(consultation_id, PaymentStatus.PAID)
            self.update_consultation_status(consultation_id, ConsultationStatus.PAID)
            return PaymentStatus.PAID
        
        # 默认返回待支付状态，不会随机显示支付成功
        return PaymentStatus.PENDING
    
    def update_payment_status(self, consultation_id: str, status: PaymentStatus, transaction_hash: str = None):
        """更新支付状态"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            if transaction_hash:
                update_data["transaction_hash"] = transaction_hash
            
            self.dao.update(
                self.PAYMENT_ORDER_COLLECTION,
                "consultation_id",
                consultation_id,
                update_data
            )
        except Exception as e:
            print(f"更新支付状态时出错: {e}")
    
    def update_consultation_status(self, consultation_id: str, status: ConsultationStatus):
        """更新咨询状态"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if status == ConsultationStatus.IN_PROGRESS:
                update_data["started_at"] = datetime.utcnow()
            elif status == ConsultationStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow()
            
            self.dao.update(
                self.CONSULTATION_COLLECTION,
                "_id",
                ObjectId(consultation_id),
                update_data
            )
        except Exception as e:
            print(f"更新咨询状态时出错: {e}")
    
    def send_chat_message(self, consultation_id: str, sender_id: str, sender_type: str, 
                         message: str, message_type: str = "text", attachments: List[str] = None) -> ChatMessage:
        """发送聊天消息"""
        if attachments is None:
            attachments = []
        
        message_dict = {
            "consultation_id": consultation_id,
            "sender_id": sender_id,
            "sender_type": sender_type,
            "message": message,
            "message_type": message_type,
            "attachments": attachments,
            "created_at": datetime.utcnow()
        }
        
        # 插入数据库
        self.dao.insert(self.CHAT_MESSAGE_COLLECTION, message_dict)
        
        # 返回创建的消息
        return self.get_latest_message_by_consultation(consultation_id)
    
    def get_chat_messages(self, consultation_id: str, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
        """获取聊天消息列表"""
        try:
            messages = self.dao._MongoDao__db[self.CHAT_MESSAGE_COLLECTION].find(
                {"consultation_id": consultation_id}
            ).sort("created_at", 1).skip(skip).limit(limit)
            
            result = []
            for message in messages:
                message["id"] = message.pop("_id")
                result.append(ChatMessage(**message))
            return result
        except Exception as e:
            print(f"获取聊天消息时出错: {e}")
            return []
    
    def get_latest_message_by_consultation(self, consultation_id: str) -> Optional[ChatMessage]:
        """获取咨询的最新消息"""
        try:
            messages = self.dao._MongoDao__db[self.CHAT_MESSAGE_COLLECTION].find(
                {"consultation_id": consultation_id}
            ).sort("created_at", -1).limit(1)
            
            for message in messages:
                message["id"] = message.pop("_id")
                return ChatMessage(**message)
        except Exception as e:
            print(f"获取最新消息时出错: {e}")
        return None
    
    def auto_assign_doctor(self, consultation_id: str) -> bool:
        """自动分配医生到咨询"""
        try:
            consultation = self.get_consultation_by_id(consultation_id)
            if not consultation or consultation.assigned_doctor_id:
                print(f"咨询 {consultation_id} 不存在或已分配医生")
                return False
            
            # 获取符合等级要求的在线医生
            # 确保doctor_level是DoctorLevel枚举
            if isinstance(consultation.doctor_level, str):
                from models.consultation import DoctorLevel as ConsultationDoctorLevel
                doctor_level = ConsultationDoctorLevel(consultation.doctor_level)
            else:
                doctor_level = consultation.doctor_level
                
            available_doctors = self.get_available_doctors_by_level(
                doctor_level=doctor_level,
                status=DoctorStatus.ACTIVE
            )
            
            if not available_doctors:
                level_str = doctor_level.value if hasattr(doctor_level, 'value') else str(doctor_level)
                print(f"没有可用的{level_str}级医生")
                return False
            
            # 选择当前咨询数量最少的医生
            selected_doctor = min(
                available_doctors,
                key=lambda doctor: doctor.get("current_consultation_count", 0)
            )
            
            # 分配医生
            from services.doctor_service import doctor_service
            from bson import ObjectId
            success = doctor_service.assign_doctor_to_consultation(
                selected_doctor["id"], 
                consultation_id
            )
            
            if success:
                # 更新咨询状态
                self.update_consultation_status(
                    consultation_id, 
                    ConsultationStatus.IN_PROGRESS
                )
                print(f"成功分配医生 {selected_doctor['name']} 到咨询 {consultation_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"自动分配医生失败: {e}")
            return False
    
    def get_available_doctors_by_level(self, doctor_level: DoctorLevel, 
                                     status: DoctorStatus = DoctorStatus.ACTIVE):
        """根据等级获取可用医生"""
        try:
            query = {
                "level": doctor_level.value,
                "status": status.value,
                "is_active": True
            }
            
            doctors = self.dao._MongoDao__db["doctors"].find(query)
            result = []
            for doctor in doctors:
                doctor["id"] = str(doctor.pop("_id"))
                # 计算当前咨询数量
                current_count = self.dao._MongoDao__db["consultations"].count_documents({
                    "assigned_doctor_id": doctor["id"],
                    "status": {"$in": [ConsultationStatus.IN_PROGRESS.value, ConsultationStatus.PAID.value]}
                })
                doctor["current_consultation_count"] = current_count
                result.append(doctor)
            
            return result
        except Exception as e:
            print(f"获取可用医生失败: {e}")
            return []
    
    def get_unassigned_consultations(self, limit: int = 50):
        """获取未分配的咨询列表"""
        try:
            consultations = self.dao._MongoDao__db[self.CONSULTATION_COLLECTION].find({
                "status": ConsultationStatus.PAID.value,
                "assigned_doctor_id": None
            }).sort("created_at", 1).limit(limit)
            
            result = []
            for consultation in consultations:
                consultation["id"] = str(consultation.pop("_id"))
                result.append(consultation)
            
            return result
        except Exception as e:
            print(f"获取未分配咨询失败: {e}")
            return []

# 创建全局咨询服务实例
consultation_service = ConsultationService()
