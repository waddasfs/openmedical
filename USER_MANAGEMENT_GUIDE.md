# 用户管理功能使用指南

## 功能概述

现在FastAPI应用已经集成了完整的用户管理功能，包括：

- ✅ 用户自动入库（Google登录时）
- ✅ 用户信息管理
- ✅ 登录统计
- ✅ 用户查询和管理API

## 数据库结构

### 用户集合 (users)

```json
{
  "_id": "ObjectId",
  "google_id": "Google用户ID",
  "name": "用户姓名",
  "email": "用户邮箱",
  "picture": "用户头像URL",
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "last_login": "最后登录时间",
  "login_count": "登录次数",
  "is_active": "是否激活"
}
```

## 环境配置

创建 `.env` 文件并配置以下变量：

```env
# Google OAuth2 配置
GOOGLE_CLIENT_ID=your_google_client_id_here
SECRET_KEY=your_secret_key_here

# MongoDB 配置
MONGODB_IP=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=users
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
```

## API端点

### 用户认证
- `POST /auth/google` - Google OAuth2认证（自动入库）

### 用户管理
- `GET /api/user/profile` - 获取当前用户详细信息
- `GET /api/user/stats` - 获取用户统计信息
- `GET /api/users` - 获取用户列表（分页）

### 页面路由
- `GET /` - 首页
- `GET /login` - 登录页面
- `GET /profile` - 用户资料页面
- `GET /logout` - 退出登录

## 使用流程

1. **用户首次登录**：
   - 用户通过Google OAuth2登录
   - 系统自动创建用户记录并保存到MongoDB
   - 记录登录时间和次数

2. **用户再次登录**：
   - 系统查找现有用户记录
   - 更新最后登录时间和登录次数
   - 保持用户信息同步

3. **用户信息管理**：
   - 通过API获取用户详细信息
   - 查看用户统计信息
   - 管理用户列表

## 测试方法

1. **运行测试脚本**：
   ```bash
   python test_user_management.py
   ```

2. **手动测试**：
   - 访问 `http://localhost:5000`
   - 点击登录按钮
   - 使用Google账户登录
   - 检查MongoDB中的用户记录

3. **API测试**：
   - 访问 `http://localhost:5000/docs` 查看API文档
   - 使用Swagger UI测试各个端点

## 数据库索引

系统会自动创建以下索引：
- `google_id` - 唯一索引，用于快速查找用户
- `email` - 普通索引，用于邮箱查询

## 注意事项

1. **生产环境**：
   - 建议使用Redis或数据库存储会话
   - 启用HTTPS并设置Cookie安全选项
   - 配置适当的数据库连接池 

2. **安全性**：
   - 定期清理过期会话
   - 实施适当的访问控制
   - 监控异常登录行为

3. **性能优化**：
   - 考虑添加缓存层
   - 实施分页查询
   - 定期清理历史数据

## 故障排除

1. **数据库连接失败**：
   - 检查MongoDB服务是否运行
   - 验证连接配置是否正确
   - 确认网络连接正常

2. **用户创建失败**：
   - 检查Google OAuth2配置
   - 验证数据库权限
   - 查看应用日志

3. **会话问题**：
   - 检查Cookie设置
   - 验证会话存储
   - 确认时间同步
