#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化consultation集合
"""

from utils.mongo_dao import mongo_dao
from datetime import datetime

def init_consultation_collection():
    """初始化consultation集合"""
    print("=== 初始化consultation集合 ===")
    
    try:
        # 检查集合是否存在
        collections = mongo_dao.__db.list_collection_names()
        if 'consultation' in collections:
            print("✅ consultation集合已存在")
        else:
            print("ℹ️ consultation集合不存在，将自动创建")
        
        # 创建索引
        print("\n创建索引...")
        
        # 用户ID索引
        index1 = mongo_dao.create_index("consultation", "user_id")
        print(f"用户ID索引: {index1}")
        
        # 状态索引
        index2 = mongo_dao.create_index("consultation", "status")
        print(f"状态索引: {index2}")
        
        # 创建时间索引
        index3 = mongo_dao.create_index("consultation", "created_at")
        print(f"创建时间索引: {index3}")
        
        # 医生ID索引
        index4 = mongo_dao.create_index("consultation", "assigned_doctor_id")
        print(f"医生ID索引: {index4}")
        
        # 支付订单ID索引
        index5 = mongo_dao.create_index("consultation", "payment_order_id")
        print(f"支付订单ID索引: {index5}")
        
        print("\n✅ 索引创建完成")
        
        # 插入示例数据（可选）
        print("\n插入示例数据...")
        sample_data = {
            "user_id": "sample_user_001",
            "mode": "onetime",
            "status": "completed",
            "disease_description": "示例咨询：头痛症状",
            "symptoms": "持续性头痛，伴有恶心",
            "medical_history": "无特殊病史",
            "attachments": [],
            "doctor_level": "normal",
            "assigned_doctor_id": "doctor_sample_001",
            "package_id": "package_normal",
            "price_usdt": 10.0,
            "payment_order_id": "order_sample_001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        result = mongo_dao.insert("consultation", sample_data)
        if result and result.inserted_id:
            print(f"✅ 示例数据插入成功，ID: {result.inserted_id}")
        else:
            print("❌ 示例数据插入失败")
        
        # 验证数据
        print("\n验证数据...")
        consultations = mongo_dao.find_all("consultation")
        print(f"✅ 集合中共有 {len(consultations)} 条记录")
        
        if consultations:
            sample = consultations[0]
            print(f"示例记录字段: {list(sample.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_collection_stats():
    """检查集合统计信息"""
    print("\n=== 集合统计信息 ===")
    
    try:
        # 获取集合统计
        stats = mongo_dao.__db.command("collStats", "consultation")
        print(f"集合名称: {stats.get('ns')}")
        print(f"文档数量: {stats.get('count', 0)}")
        print(f"集合大小: {stats.get('size', 0)} 字节")
        print(f"平均文档大小: {stats.get('avgObjSize', 0)} 字节")
        
        # 获取索引信息
        indexes = mongo_dao.__db.consultation.list_indexes()
        print(f"\n索引信息:")
        for index in indexes:
            print(f"  - {index.get('name')}: {index.get('key')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")
        return False

def main():
    """主函数"""
    print("开始初始化consultation集合...")
    print(f"初始化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化集合
    init_ok = init_consultation_collection()
    
    if init_ok:
        # 检查统计信息
        check_collection_stats()
        print("\n✅ 初始化完成！")
    else:
        print("\n❌ 初始化失败！")
    
    return init_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

