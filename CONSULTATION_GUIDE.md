# 医疗咨询系统使用指南

## 功能概述

本系统为患者提供了完整的在线医疗咨询服务，支持两种咨询模式：

### 1. 实时聊天模式 💬
- **特点**: 与医生进行实时在线聊天
- **收费**: 基础费用 0.02 ETH + 按分钟计费
- **适用场景**: 需要即时医疗建议和指导
- **功能**: 
  - 实时消息交流
  - 文件上传（图片、文档等）
  - 即时回复

### 2. 一次性付费咨询模式 📋
- **特点**: 提交详细病情描述，选择医生等级
- **收费**: 根据医生等级定价
- **适用场景**: 需要专业诊断和详细治疗方案
- **功能**:
  - 详细病情描述
  - 医生等级选择（普通/高级/专家）
  - 文件材料上传
  - 专业诊断报告

## 医生等级和定价

| 等级 | 名称 | 价格 | 响应时间 | 咨询时长 | 特性 |
|------|------|------|----------|----------|------|
| 普通医生 | 普通医生咨询 | 0.01 ETH | 24小时内 | 30分钟 | 基础诊断、用药建议、生活指导 |
| 高级医生 | 高级医生咨询 | 0.05 ETH | 12小时内 | 60分钟 | 专业诊断、详细治疗方案、复查建议、紧急情况处理 |
| 专家医生 | 专家医生咨询 | 0.1 ETH | 6小时内 | 90分钟 | 专家诊断、个性化治疗方案、长期跟踪、多学科会诊 |

## 支付方式

### 以太坊支付
- **支持币种**: ETH (以太坊)
- **支付方式**: 
  - 扫描二维码支付
  - 复制地址手动转账
  - 支持EIP-681标准支付链接
- **支付检测**: 自动检测支付状态
- **订单过期**: 24小时内未支付自动过期

## 使用流程

### 实时聊天咨询流程
1. 登录系统
2. 选择"实时聊天咨询"模式
3. 填写疾病描述和相关信息
4. 上传相关文件（可选）
5. 支付基础费用
6. 等待医生分配
7. 开始实时聊天
8. 结束咨询

### 一次性咨询流程
1. 登录系统
2. 选择"一次性付费咨询"模式
3. 选择医生等级
4. 填写详细病情描述
5. 上传相关文件材料
6. 支付咨询费用
7. 等待医生回复
8. 查看诊断报告

## 技术特性

### 前端特性
- 响应式设计，支持移动端
- 现代化UI界面
- 实时消息更新
- 文件拖拽上传
- 支付状态实时检测

### 后端特性
- FastAPI高性能框架
- MongoDB数据存储
- 以太坊支付集成
- 二维码自动生成
- 实时聊天支持

### 安全特性
- Google OAuth2认证
- 用户权限验证
- 数据加密存储
- 支付安全验证

## 环境配置

### 必需的环境变量
```env
# 数据库配置
MONGODB_IP=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=medical
MONGODB_USERNAME=
MONGODB_PASSWORD=

# Google OAuth2配置
GOOGLE_CLIENT_ID=your_google_client_id_here
SECRET_KEY=your_secret_key_here

# 以太坊配置
ETH_ACCOUNT=0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
ETH_PRIVATE_KEY=your_ethereum_private_key_here
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python main.py
```

## API接口

### 咨询相关接口
- `GET /consultation` - 咨询页面
- `GET /api/consultation/packages` - 获取咨询套餐
- `POST /api/consultation/create` - 创建咨询
- `GET /api/consultation/{consultation_id}` - 获取咨询详情
- `GET /api/consultation/user/list` - 获取用户咨询列表

### 支付相关接口
- `GET /api/payment/status/{consultation_id}` - 检查支付状态

### 聊天相关接口
- `GET /api/consultation/{consultation_id}/messages` - 获取聊天消息
- `POST /api/consultation/{consultation_id}/send-message` - 发送消息
- `POST /api/consultation/{consultation_id}/end` - 结束咨询

## 注意事项

1. **支付安全**: 请确保在HTTPS环境下使用
2. **文件上传**: 支持图片、PDF、Word文档等格式
3. **网络要求**: 需要稳定的网络连接
4. **浏览器兼容**: 建议使用现代浏览器（Chrome、Firefox、Safari等）
5. **以太坊钱包**: 需要安装以太坊钱包进行支付

## 故障排除

### 常见问题
1. **登录失败**: 检查Google OAuth2配置
2. **支付失败**: 检查以太坊网络连接和钱包余额
3. **文件上传失败**: 检查文件大小和格式
4. **聊天连接失败**: 检查网络连接和服务器状态

### 联系支持
如遇到技术问题，请联系系统管理员或查看系统日志。

