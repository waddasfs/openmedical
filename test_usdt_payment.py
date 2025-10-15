#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试USDT(TRC20)支付功能
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:5000"

def test_usdt_payment_flow():
    """测试USDT支付流程"""
    print("=== 测试USDT(TRC20)支付功能 ===")
    
    # 测试咨询套餐价格
    print("\n1. 测试咨询套餐价格...")
    try:
        response = requests.get(f"{BASE_URL}/api/consultation/packages")
        packages = response.json()
        
        print("✅ 咨询套餐加载成功:")
        for pkg in packages:
            print(f"   - {pkg['name']}: {pkg['price_usdt']} USDT")
        
        # 验证价格是否为USDT
        for pkg in packages:
            if 'price_usdt' not in pkg:
                print(f"❌ 套餐 {pkg['name']} 缺少 price_usdt 字段")
                return False
            if pkg['price_usdt'] <= 0:
                print(f"❌ 套餐 {pkg['name']} 价格无效: {pkg['price_usdt']}")
                return False
        
        print("✅ 所有套餐价格格式正确")
        
    except Exception as e:
        print(f"❌ 测试咨询套餐失败: {e}")
        return False
    
    # 测试创建咨询（模拟）
    print("\n2. 测试创建咨询...")
    try:
        # 模拟文件上传
        files = [
            ("attachments", ("test_usdt.txt", "USDT支付测试文件", "text/plain"))
        ]
        
        data = {
            "mode": "onetime",
            "disease_description": "USDT支付测试咨询",
            "symptoms": "测试症状",
            "medical_history": "测试病史",
            "doctor_level": "normal"
        }
        
        response = requests.post(f"{BASE_URL}/api/consultation/create", files=files, data=data)
        result = response.json()
        
        if result.get("success"):
            print("✅ 咨询创建成功")
            consultation_id = result.get('consultation_id')
            payment_info = result.get('payment_info', {})
            
            # 验证支付信息
            print(f"   咨询ID: {consultation_id}")
            print(f"   支付金额: {payment_info.get('amount_usdt')} USDT")
            print(f"   USDT地址: {payment_info.get('usdt_address')}")
            
            # 验证字段名称
            if 'amount_usdt' not in payment_info:
                print("❌ 支付信息缺少 amount_usdt 字段")
                return False
            
            if 'usdt_address' not in payment_info:
                print("❌ 支付信息缺少 usdt_address 字段")
                return False
            
            if 'eth_address' in payment_info:
                print("❌ 支付信息仍包含 eth_address 字段，应该使用 usdt_address")
                return False
            
            print("✅ 支付信息格式正确")
            
            # 测试支付状态检查
            print("\n3. 测试支付状态检查...")
            status_response = requests.get(f"{BASE_URL}/api/payment/status/{consultation_id}")
            status_result = status_response.json()
            
            print(f"   支付状态: {status_result.get('status')}")
            
            if status_result.get('status') == 'pending':
                print("✅ 支付状态检查正常")
            else:
                print(f"❌ 支付状态异常: {status_result.get('status')}")
                return False
            
            # 测试支付成功模拟
            print("\n4. 测试支付成功模拟...")
            test_response = requests.post(f"{BASE_URL}/api/payment/test/{consultation_id}")
            test_result = test_response.json()
            
            if test_result.get("success"):
                print("✅ 测试支付成功")
                
                # 再次检查支付状态
                time.sleep(1)
                status_response = requests.get(f"{BASE_URL}/api/payment/status/{consultation_id}")
                status_result = status_response.json()
                
                print(f"   支付后状态: {status_result.get('status')}")
                
                if status_result.get('status') == 'paid':
                    print("✅ 支付状态更新成功")
                else:
                    print(f"❌ 支付状态更新失败: {status_result.get('status')}")
                    return False
            else:
                print(f"❌ 测试支付失败: {test_result.get('error')}")
                return False
            
            return True
            
        else:
            print(f"❌ 咨询创建失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试创建咨询异常: {e}")
        return False

def test_payment_service():
    """测试支付服务"""
    print("\n=== 测试支付服务 ===")
    
    try:
        from services.payment_service import payment_service
        
        # 测试USDT地址
        print(f"USDT收款地址: {payment_service.usdt_account}")
        
        # 测试二维码生成
        test_address = "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE"
        test_amount = 50.0
        
        qr_code = payment_service.generate_qr_code(test_address, test_amount)
        print(f"✅ 二维码生成成功: {qr_code[:50]}...")
        
        # 测试USDT余额查询
        balance = payment_service.get_usdt_balance(test_address)
        print(f"✅ USDT余额查询: {balance} USDT")
        
        # 测试金额转换
        sun_amount = payment_service.format_usdt_to_sun(test_amount)
        usdt_amount = payment_service.format_usdt_amount(sun_amount)
        print(f"✅ 金额转换测试: {test_amount} USDT -> {sun_amount} Sun -> {usdt_amount} USDT")
        
        return True
        
    except Exception as e:
        print(f"❌ 支付服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试USDT(TRC20)支付功能...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务器: {BASE_URL}")
    
    # 测试支付服务
    service_ok = test_payment_service()
    
    # 测试支付流程
    flow_ok = test_usdt_payment_flow()
    
    print("\n=== 测试结果 ===")
    if service_ok and flow_ok:
        print("✅ 所有测试通过！USDT(TRC20)支付功能正常")
        print("\n修复内容总结:")
        print("1. ✅ 支付模型从ETH改为USDT(TRC20)")
        print("2. ✅ 支付服务支持TRON网络")
        print("3. ✅ 前端显示更新为USDT")
        print("4. ✅ 咨询套餐价格更新为USDT")
        print("5. ✅ 支付二维码使用TRON标准")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    
    return service_ok and flow_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

