#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户服务类
"""

from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from utils.mongo_dao import mongo_dao
from models.user import UserInDB, UserCreate, UserUpdate, UserResponse

class UserService:
    """用户服务类"""
    
    COLLECTION_NAME = "users"
    
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
        except Exception as e:
            print(f"创建索引时出错: {e}")
    
    def create_user(self, user_data: UserCreate) -> UserInDB:
        """创建新用户"""
        try:
            # 检查用户是否已存在
            existing_user = self.get_user_by_google_id(user_data.google_id)
            if existing_user:
                # 更新最后登录时间
                print(f"用户已存在，更新登录信息: {existing_user.id}")
                updated_user = self.update_user_login(str(existing_user.id))
                if updated_user:
                    return updated_user
                else:
                    print("更新用户登录信息失败，返回原用户信息")
                    return existing_user
            
            # 创建新用户
            user_dict = user_data.dict()
            user_dict.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                "login_count": 1,
                "is_active": True
            })
            
            # 插入数据库
            self.dao.insert(self.COLLECTION_NAME, user_dict)
            print(f"新用户创建成功: {user_data.email}")
            
            # 返回创建的用户
            new_user = self.get_user_by_google_id(user_data.google_id)
            if new_user:
                return new_user
            else:
                print("创建用户后无法获取用户信息")
                return None
                
        except Exception as e:
            print(f"创建用户时出错: {e}")
            return None
    
    def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """根据Google ID获取用户"""
        users = self.dao.search(self.COLLECTION_NAME, "google_id", google_id)
        if users:
            user_data = users[0]
            user_data["id"] = user_data.pop("_id")
            return UserInDB(**user_data)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """根据用户ID获取用户"""
        try:
            # 确保user_id是有效的ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            users = self.dao.search(self.COLLECTION_NAME, "_id", user_id)
            if users:
                user_data = users[0]
                user_data["id"] = user_data.pop("_id")
                return UserInDB(**user_data)
        except Exception as e:
            print(f"获取用户时出错: {e}, user_id: {user_id}")
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """根据邮箱获取用户"""
        users = self.dao.search(self.COLLECTION_NAME, "email", email)
        if users:
            user_data = users[0]
            user_data["id"] = user_data.pop("_id")
            return UserInDB(**user_data)
        return None
    
    def update_user_login(self, user_id: str) -> Optional[UserInDB]:
        """更新用户登录信息"""
        try:
            # 使用MongoDB的$inc操作符增加登录次数
            result = self.dao._MongoDao__db[self.COLLECTION_NAME].update_one(
                {"_id": ObjectId(user_id)}, 
                {
                    "$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}, 
                    "$inc": {"login_count": 1}
                }
            )
            
            if result.modified_count > 0:
                return self.get_user_by_id(user_id)
            else:
                print(f"更新用户登录信息失败，用户ID: {user_id}")
        except Exception as e:
            print(f"更新用户登录信息时出错: {e}")
        return None
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserInDB]:
        """更新用户信息"""
        try:
            update_dict = user_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            result = self.dao.update(
                self.COLLECTION_NAME, 
                "_id", 
                ObjectId(user_id), 
                update_dict
            )
            
            if result:
                return self.get_user_by_id(user_id)
        except Exception as e:
            print(f"更新用户时出错: {e}")
        return None
    
    def deactivate_user(self, user_id: str) -> bool:
        """停用用户"""
        try:
            result = self.dao.update(
                self.COLLECTION_NAME,
                "_id",
                ObjectId(user_id),
                {"is_active": False, "updated_at": datetime.utcnow()}
            )
            return result
        except Exception as e:
            print(f"停用用户时出错: {e}")
            return False
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """获取所有用户（分页）"""
        try:
            users = self.dao._MongoDao__db[self.COLLECTION_NAME].find({}).skip(skip).limit(limit)
            result = []
            for user in users:
                user["id"] = user.pop("_id")
                result.append(UserInDB(**user))
            return result
        except Exception as e:
            print(f"获取用户列表时出错: {e}")
            return []
    
    def search_users(self, query: dict, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """搜索用户"""
        try:
            users = self.dao._MongoDao__db[self.COLLECTION_NAME].find(query).skip(skip).limit(limit)
            result = []
            for user in users:
                user["id"] = user.pop("_id")
                result.append(UserInDB(**user))
            return result
        except Exception as e:
            print(f"搜索用户时出错: {e}")
            return []
    
    def get_user_stats(self) -> dict:
        """获取用户统计信息"""
        try:
            total_users = self.dao._MongoDao__db[self.COLLECTION_NAME].count_documents({})
            active_users = self.dao._MongoDao__db[self.COLLECTION_NAME].count_documents({"is_active": True})
            
            # 获取最近7天注册的用户数
            from datetime import timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_users = self.dao._MongoDao__db[self.COLLECTION_NAME].count_documents({
                "created_at": {"$gte": seven_days_ago}
            })
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "recent_users": recent_users
            }
        except Exception as e:
            print(f"获取用户统计时出错: {e}")
            return {}

# 创建全局用户服务实例
user_service = UserService()
