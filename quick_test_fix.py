#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试修复效果
"""

def test_consultation_service_directly():
    """直接测试咨询服务"""
    print("=== 直接测试咨询服务 ===")
    
    try:
        from services.consultation_service import consultation_service
        
        # 测试获取用户咨询列表
        print("测试获取用户咨询列表...")
        consultations = consultation_service.get_user_consultations("test_user_fix")
        print(f"✅ 成功获取 {len(consultations)} 条咨询记录")
        
        for i, cons in enumerate(consultations):
            print(f"  {i+1}. ID: {cons.id}")
            print(f"     用户ID: {cons.user_id}")
            print(f"     模式: {cons.mode}")
            print(f"     状态: {cons.status}")
            print(f"     价格: {cons.price_usdt} USDT")
            print(f"     描述: {cons.disease_description[:50]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    try:
        import requests
        
        # 测试获取咨询列表API
        response = requests.get("http://localhost:5000/api/consultation/user/list")
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            consultations = response.json()
            print(f"✅ API查询成功，获取 {len(consultations)} 条记录")
            
            for i, cons in enumerate(consultations):
                print(f"  {i+1}. ID: {cons.get('id')}")
                print(f"     用户ID: {cons.get('user_id')}")
                print(f"     模式: {cons.get('mode')}")
                print(f"     状态: {cons.get('status')}")
                print(f"     价格: {cons.get('price_usdt')} USDT")
                print(f"     描述: {cons.get('disease_description', '')[:50]}...")
                print()
            
            return True
        else:
            print(f"❌ API查询失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始快速测试修复效果...")
    
    # 直接测试服务
    service_ok = test_consultation_service_directly()
    
    if service_ok:
        # 测试API
        api_ok = test_api_endpoint()
        
        print("\n=== 测试结果 ===")
        if api_ok:
            print("✅ 修复成功！咨询查询功能正常")
            print("\n现在可以:")
            print("1. 正常查看咨询历史记录")
            print("2. 查看咨询详情")
            print("3. 创建新的咨询")
        else:
            print("❌ API测试失败，请检查服务器是否运行")
    else:
        print("❌ 服务测试失败")
    
    return service_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

