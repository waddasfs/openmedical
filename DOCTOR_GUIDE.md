# 医生端功能指南

## 概述

医生端是医疗咨询平台的医生工作台，为医生提供完整的咨询管理、实时聊天和收入统计功能。

## 主要功能

### 1. 医生认证
- **Google登录**: 使用Google OAuth2进行安全登录
- **身份验证**: 需要预先注册的医生账户才能登录
- **会话管理**: 支持24小时会话保持

### 2. 实时聊天
- **患者沟通**: 与患者进行实时文字聊天
- **消息历史**: 查看完整的聊天记录
- **状态管理**: 支持在线、忙碌、离线状态切换
- **自动刷新**: 每30秒自动刷新消息

### 3. 咨询管理
- **咨询列表**: 查看分配给自己的所有咨询
- **状态筛选**: 按状态筛选咨询（全部、待处理、进行中、已完成）
- **接诊功能**: 主动接诊已支付的咨询
- **完成咨询**: 标记咨询为已完成状态

### 4. 收入统计
- **收入概览**: 显示总收入、本月收入、本周收入、今日收入
- **咨询统计**: 显示总咨询次数、已完成咨询、待处理咨询
- **收入趋势**: 图表显示30天收入趋势
- **收入明细**: 时间线显示详细收入记录
- **只读模式**: 仅可查看，不支持转账结算

## 页面结构

### 1. 医生登录页面 (`/doctor/login`)
- Google OAuth2登录界面
- 医生专用登录入口
- 返回患者端链接

### 2. 医生仪表板 (`/doctor/dashboard`)
- 医生基本信息展示
- 收入统计概览
- 最近咨询列表
- 状态管理

### 3. 咨询列表页面 (`/doctor/consultations`)
- 所有咨询的列表视图
- 状态筛选功能
- 接诊和完成操作
- 实时数据刷新

### 4. 聊天页面 (`/doctor/chat/{consultation_id}`)
- 实时聊天界面
- 消息发送和接收
- 咨询信息展示
- 完成咨询功能

### 5. 收入统计页面 (`/doctor/earnings`)
- 详细收入统计
- 图表可视化
- 收入明细时间线
- 只读模式说明

## API接口

### 认证相关
- `POST /auth/doctor/google` - 医生Google登录
- `GET /api/doctor/profile` - 获取医生详细信息

### 咨询管理
- `GET /api/doctor/consultations` - 获取医生咨询列表
- `POST /api/doctor/assign/{consultation_id}` - 接诊咨询
- `POST /api/doctor/consultation/{consultation_id}/complete` - 完成咨询

### 聊天功能
- `POST /api/doctor/consultation/{consultation_id}/send-message` - 发送消息
- `GET /api/consultation/{consultation_id}/messages` - 获取聊天消息

### 收入统计
- `GET /api/doctor/earnings` - 获取收入统计
- `POST /api/doctor/status` - 更新医生状态

## 数据模型

### 医生模型 (Doctor)
```python
{
    "id": "医生ID",
    "google_id": "Google用户ID",
    "name": "医生姓名",
    "email": "邮箱",
    "picture": "头像URL",
    "license_number": "执业证号",
    "hospital": "所属医院",
    "department": "所属科室",
    "specialties": ["专业领域"],
    "level": "医生等级",
    "experience_years": "从业年限",
    "introduction": "医生简介",
    "consultation_fee": "咨询费用",
    "status": "医生状态",
    "total_consultations": "总咨询次数",
    "total_earnings": "总收入",
    "rating": "评分",
    "rating_count": "评分次数"
}
```

### 收入统计模型 (DoctorEarnings)
```python
{
    "doctor_id": "医生ID",
    "total_earnings": "总收入",
    "monthly_earnings": "本月收入",
    "weekly_earnings": "本周收入",
    "daily_earnings": "今日收入",
    "total_consultations": "总咨询次数",
    "completed_consultations": "已完成咨询",
    "pending_consultations": "待处理咨询"
}
```

## 使用流程

### 1. 医生注册
1. 管理员使用 `create_test_doctor.py` 创建医生账户
2. 医生获得Google ID和登录凭据

### 2. 医生登录
1. 访问 `/doctor/login`
2. 使用Google账户登录
3. 系统验证医生身份
4. 跳转到医生仪表板

### 3. 处理咨询
1. 在咨询列表页面查看待处理咨询
2. 点击"接诊"按钮接受咨询
3. 进入聊天页面与患者沟通
4. 完成咨询后点击"完成咨询"

### 4. 查看收入
1. 访问收入统计页面
2. 查看各种收入指标
3. 查看收入趋势图表
4. 查看详细收入记录

## 技术特性

### 前端技术
- Bootstrap 5 响应式设计
- Chart.js 图表可视化
- Font Awesome 图标库
- 原生JavaScript AJAX

### 后端技术
- FastAPI 异步框架
- MongoDB 数据存储
- Google OAuth2 认证
- Pydantic 数据验证

### 安全特性
- Google OAuth2 安全认证
- 会话管理
- 权限验证
- 数据验证

## 部署说明

### 1. 环境要求
- Python 3.8+
- MongoDB 4.4+
- FastAPI
- 相关依赖包

### 2. 配置要求
- Google OAuth2 客户端ID
- MongoDB 连接字符串
- 环境变量配置

### 3. 启动步骤
1. 安装依赖: `pip install -r requirements.txt`
2. 配置环境变量
3. 创建医生账户: `python create_test_doctor.py`
4. 启动服务: `python main.py`

## 测试说明

### 1. 功能测试
- 运行 `test_doctor_functionality.py` 进行基础功能测试
- 测试各个API端点的响应
- 验证页面路由的正确性

### 2. 集成测试
- 测试完整的医生工作流程
- 验证与患者端的交互
- 测试实时聊天功能

### 3. 性能测试
- 测试并发用户访问
- 验证数据库查询性能
- 测试消息推送性能

## 注意事项

1. **医生账户**: 需要预先注册，不支持自助注册
2. **收入结算**: 仅支持查看，不支持直接转账
3. **实时聊天**: 需要定期刷新，非WebSocket实现
4. **权限控制**: 医生只能访问分配给自己的咨询
5. **数据安全**: 所有敏感数据都经过加密处理

## 故障排除

### 常见问题
1. **登录失败**: 检查Google OAuth2配置
2. **数据加载失败**: 检查MongoDB连接
3. **页面显示异常**: 检查静态资源路径
4. **API调用失败**: 检查网络连接和权限

### 调试方法
1. 查看浏览器控制台错误
2. 检查服务器日志
3. 验证数据库连接
4. 测试API端点响应

## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 实现基础医生功能
- 支持Google登录
- 实现实时聊天
- 添加收入统计
- 完成咨询管理
