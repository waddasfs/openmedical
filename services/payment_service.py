#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USDT(TRC20)支付服务
"""

import os
import qrcode
import io
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from services.consultation_service import consultation_service
from models.consultation import PaymentOrder, PaymentStatus

load_dotenv(".env")

class PaymentService:
    """USDT(TRC20)支付服务类"""
    
    def __init__(self):
        # 从环境变量获取USDT(TRC20)收款地址
        self.usdt_account = os.getenv('USDT_ACCOUNT', 'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE')
        self.usdt_private_key = os.getenv('USDT_PRIVATE_KEY', '')  # 私钥（生产环境需要安全存储）
        
    def generate_qr_code(self, usdt_address: str, amount_usdt: float) -> str:
        """生成USDT(TRC20)支付二维码"""
        # 创建支付URL（使用TRON标准）
        payment_url = f"tronlink://send?address={usdt_address}&amount={amount_usdt}&token=USDT"
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64字符串
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def create_payment_order(self, consultation_id: str, user_id: str) -> Dict[str, Any]:
        """创建支付订单"""
        # 获取咨询记录
        consultation = consultation_service.get_consultation_by_id(consultation_id)
        if not consultation:
            raise ValueError("咨询记录不存在")
        
        if consultation.user_id != user_id:
            raise ValueError("无权限访问此咨询记录")
        
        # 生成二维码
        qr_code_data = self.generate_qr_code(self.usdt_account, consultation.price_usdt)
        
        # 创建支付订单
        payment_order = consultation_service.create_payment_order(
            consultation_id=consultation_id,
            user_id=user_id,
            usdt_address=self.usdt_account
        )
        
        return {
            "order_id": str(payment_order.id),
            "consultation_id": consultation_id,
            "amount_usdt": consultation.price_usdt,
            "usdt_address": self.usdt_account,
            "qr_code": qr_code_data,
            "payment_url": f"tronlink://send?address={self.usdt_account}&amount={consultation.price_usdt}&token=USDT",
            "expires_at": payment_order.expires_at.isoformat(),
            "status": payment_order.status.value
        }
    
    def check_payment_status(self, consultation_id: str) -> Dict[str, Any]:
        """检查支付状态"""
        # 这里应该连接TRON网络检查交易状态
        # 为了演示，我们使用模拟的检查逻辑
        status = consultation_service.check_payment_status(consultation_id)
        
        return {
            "status": status.value,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def verify_tron_transaction(self, transaction_hash: str, expected_amount_usdt: float) -> bool:
        """验证TRON交易（模拟实现）"""
        # 实际实现需要：
        # 1. 连接到TRON网络（如TronGrid、TronScan等）
        # 2. 获取交易详情
        # 3. 验证交易金额和收款地址
        # 4. 确认交易状态
        
        # 这里为了演示，返回模拟结果
        import random
        return random.random() > 0.3  # 70%的概率验证成功
    
    def get_usdt_balance(self, address: str) -> float:
        """获取USDT地址余额（模拟实现）"""
        # 实际实现需要连接TRON网络查询USDT余额
        # 这里返回模拟数据
        import random
        return round(random.uniform(10, 1000), 2)
    
    def format_usdt_amount(self, amount_sun: int) -> float:
        """将Sun转换为USDT"""
        return amount_sun / (10 ** 6)  # USDT精度为6位小数
    
    def format_usdt_to_sun(self, amount_usdt: float) -> int:
        """将USDT转换为Sun"""
        return int(amount_usdt * (10 ** 6))

# 创建全局支付服务实例
payment_service = PaymentService()
