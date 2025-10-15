# USDT(TRC20)支付配置说明

## 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# USDT(TRC20)支付配置
USDT_ACCOUNT=TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE
USDT_PRIVATE_KEY=your-usdt-private-key-here
```

## 配置说明

### USDT_ACCOUNT
- 用于接收USDT支付的TRON地址
- 格式：以T开头的TRON地址
- 示例：`TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE`

### USDT_PRIVATE_KEY
- 对应USDT_ACCOUNT的私钥
- 用于签名交易（生产环境需要安全存储）
- 格式：64位十六进制字符串

## 支付流程

1. 用户选择咨询套餐
2. 系统生成USDT支付二维码
3. 用户使用支持TRC20的钱包扫码支付
4. 系统检查TRON网络确认支付
5. 支付成功后开始咨询

## 支持的钱包

- TronLink
- Trust Wallet
- MetaMask (需要配置TRON网络)
- 其他支持TRC20的钱包

## 注意事项

1. **网络选择**：确保使用TRC20网络，其他网络可能导致资金丢失
2. **私钥安全**：生产环境中私钥应存储在安全的地方
3. **交易确认**：TRON网络通常需要3-6个区块确认
4. **手续费**：TRON网络手续费较低，通常为1-2 TRX

## 测试

运行测试脚本验证功能：

```bash
python test_usdt_payment.py
```

## 价格设置

当前咨询套餐价格（USDT）：

- 实时咨询：20 USDT（基础费用）
- 普通医生：10 USDT
- 高级医生：50 USDT  
- 专家医生：100 USDT

