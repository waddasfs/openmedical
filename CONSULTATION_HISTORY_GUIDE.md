# 患者历史咨询管理功能说明

## 功能概述

为患者提供完整的历史咨询管理功能，包括咨询记录查看、详情查看、医生反馈查看和报告下载等功能。

## 页面结构

### 1. 历史咨询列表页面 (`/consultation/history`)

**功能特性：**
- 显示患者所有咨询记录
- 支持分页浏览
- 按状态筛选显示
- 响应式设计，支持移动端

**显示内容：**
- 咨询类型（实时咨询/一次性咨询）
- 医生等级
- 咨询状态（待支付/已支付/进行中/已完成/已取消）
- 费用信息
- 创建时间和完成时间
- 病情描述摘要

**操作功能：**
- 查看详情
- 下载报告（仅已完成咨询）
- 刷新列表

### 2. 咨询详情页面 (`/consultation/detail/{consultation_id}`)

**功能特性：**
- 完整的咨询信息展示
- 聊天记录查看（实时咨询）
- 医生反馈查看（已完成咨询）
- 附件文件展示

**显示内容：**
- 基本信息（类型、等级、状态、费用、时间）
- 病情描述
- 症状描述
- 病史记录
- 相关附件
- 聊天对话（实时咨询）
- 医生反馈（已完成咨询）

## API端点

### 1. 获取咨询列表
```
GET /api/consultation/user/list?skip=0&limit=10
```

**响应格式：**
```json
[
  {
    "id": "consultation_id",
    "mode": "onetime",
    "doctor_level": "normal",
    "status": "completed",
    "price_usdt": 10.0,
    "disease_description": "病情描述",
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T11:30:00Z"
  }
]
```

### 2. 获取咨询详情
```
GET /api/consultation/{consultation_id}
```

**响应格式：**
```json
{
  "id": "consultation_id",
  "mode": "onetime",
  "doctor_level": "normal",
  "status": "completed",
  "price_usdt": 10.0,
  "disease_description": "病情描述",
  "symptoms": "症状描述",
  "medical_history": "病史记录",
  "attachments": ["file1.jpg", "file2.pdf"],
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T11:30:00Z"
}
```

### 3. 获取医生反馈
```
GET /api/consultation/{consultation_id}/feedback
```

**响应格式：**
```json
{
  "id": "feedback_123",
  "consultation_id": "consultation_id",
  "doctor_id": "doctor_001",
  "doctor_name": "张医生",
  "title": "诊断报告",
  "content": "诊断内容...",
  "recommendations": [
    "建议多休息",
    "按时服药"
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. 下载咨询报告
```
GET /api/consultation/{consultation_id}/report
```

**响应格式：**
```json
{
  "consultation_id": "consultation_id",
  "patient_name": "患者姓名",
  "consultation_date": "2024-01-15T10:30:00Z",
  "doctor_level": "normal",
  "disease_description": "病情描述",
  "symptoms": "症状描述",
  "medical_history": "病史记录",
  "doctor_feedback": "医生反馈内容",
  "recommendations": ["建议1", "建议2"]
}
```

## 用户流程

### 1. 一次性咨询流程
1. 用户提交咨询申请
2. 支付USDT费用
3. 支付成功后自动跳转到历史咨询页面
4. 在历史咨询页面查看咨询状态
5. 咨询完成后查看医生反馈
6. 下载咨询报告

### 2. 实时咨询流程
1. 用户提交咨询申请
2. 支付USDT费用
3. 支付成功后进入聊天界面
4. 在历史咨询页面查看聊天记录
5. 咨询结束后查看医生反馈

## 状态说明

| 状态 | 说明 | 可执行操作 |
|------|------|-----------|
| pending | 待支付 | 查看详情 |
| paid | 已支付 | 查看详情 |
| in_progress | 进行中 | 查看详情、聊天 |
| completed | 已完成 | 查看详情、下载报告 |
| cancelled | 已取消 | 查看详情 |

## 设计特性

### 1. 响应式设计
- 支持桌面端和移动端
- 自适应布局
- 触摸友好的交互

### 2. 用户体验
- 加载状态提示
- 错误信息显示
- 成功操作反馈
- 空状态处理

### 3. 安全性
- 用户权限验证
- 数据访问控制
- 输入验证

## 测试

运行测试脚本验证功能：

```bash
python test_consultation_history.py
```

测试内容包括：
- 页面访问测试
- 咨询创建测试
- 列表获取测试
- 详情查看测试
- 反馈获取测试
- 报告下载测试

## 扩展功能

### 1. 搜索和筛选
- 按时间范围筛选
- 按状态筛选
- 按医生等级筛选
- 关键词搜索

### 2. 导出功能
- 批量导出咨询记录
- PDF报告生成
- Excel格式导出

### 3. 通知功能
- 咨询状态变更通知
- 医生反馈通知
- 邮件提醒

## 注意事项

1. **权限控制**：确保用户只能访问自己的咨询记录
2. **数据安全**：敏感医疗信息需要加密存储
3. **性能优化**：大量数据时需要考虑分页和缓存
4. **移动端适配**：确保在手机上的良好体验
5. **错误处理**：提供友好的错误提示和恢复机制

