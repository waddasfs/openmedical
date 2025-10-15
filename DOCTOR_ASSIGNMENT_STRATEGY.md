# 医生分配策略说明

## 概述

本系统实现了简单的医生自动分配策略，优先选择在线且符合用户需求（主要看医生等级）的医生。

## 分配策略

### 1. 分配优先级

1. **第一优先级**：医生状态为在线（ACTIVE）
2. **第二优先级**：医生等级匹配患者需求
3. **第三优先级**：当前咨询数量最少

### 2. 分配时机

- **支付成功后立即分配**：患者支付成功后，系统立即尝试分配医生
- **定时检查分配**：每5分钟检查一次未分配的咨询并尝试分配

### 3. 分配流程

```
患者提交咨询 → 创建咨询记录 → 生成支付订单 → 患者支付 → 支付成功 → 触发自动分配 → 获取在线医生 → 按等级筛选 → 选择咨询数量最少的医生 → 分配医生 → 更新咨询状态 → 开始医患沟通
```

## 技术实现

### 1. 数据模型更新

- 在医生模型中添加了 `current_consultation_count` 字段，用于跟踪医生当前进行中的咨询数量

### 2. 核心方法

#### 咨询服务 (`services/consultation_service.py`)

- `auto_assign_doctor(consultation_id)`: 自动分配医生到指定咨询
- `get_available_doctors_by_level(doctor_level, status)`: 根据等级获取可用医生
- `get_unassigned_consultations(limit)`: 获取未分配的咨询列表

#### 医生服务 (`services/doctor_service.py`)

- `update_doctor_consultation_count(doctor_id)`: 更新医生当前咨询数量
- `assign_doctor_to_consultation(doctor_id, consultation_id)`: 分配医生到咨询

### 3. 定时任务

- 使用 APScheduler 实现定时任务
- 每5分钟检查一次未分配的咨询
- 自动尝试分配医生

### 4. API端点

- `POST /api/admin/trigger-assignment`: 手动触发分配检查（管理员功能）

## 使用说明

### 1. 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

### 2. 测试分配策略

```bash
# 运行测试脚本
python test_assignment_strategy.py
```

### 3. 手动触发分配

```bash
# 使用curl手动触发分配检查
curl -X POST http://localhost:5000/api/admin/trigger-assignment \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=your_session_id"
```

## 监控和日志

### 1. 分配日志

系统会在控制台输出详细的分配日志：

```
支付成功，开始自动分配医生到咨询 68eef8f322f67f3395da58e2
成功分配医生 张医生 到咨询 68eef8f322f67f3395da58e2
咨询 68eef8f322f67f3395da58e2 医生分配成功
```

### 2. 定时任务日志

```
开始检查未分配的咨询...
发现 2 个未分配的咨询
尝试分配咨询: 68eef8f322f67f3395da58e2
✅ 成功分配咨询: 68eef8f322f67f3395da58e2
```

## 异常处理

### 1. 无可用医生

- 当没有符合等级要求的在线医生时，咨询保持待分配状态
- 定时任务会持续尝试分配
- 医生上线后自动参与分配

### 2. 分配失败

- 系统会记录分配失败的原因
- 定时任务会重新尝试分配
- 管理员可以手动触发分配检查

## 配置参数

### 1. 定时任务间隔

- 默认：5分钟
- 可在 `main.py` 中修改 `IntervalTrigger(minutes=5)`

### 2. 未分配咨询检查数量

- 默认：每次检查20个
- 可在 `get_unassigned_consultations(limit=20)` 中修改

## 扩展性

### 1. 添加新的分配策略

可以在 `auto_assign_doctor` 方法中添加更多分配逻辑：

```python
# 按医生评分分配
selected_doctor = max(available_doctors, key=lambda d: d.get("rating", 0))

# 按医生专业领域分配
specialty_doctors = [d for d in available_doctors if d.get("specialty") == consultation.specialty]
```

### 2. 添加分配通知

可以在分配成功后添加通知机制：

```python
# 发送邮件通知
send_email_notification(doctor.email, consultation_id)

# 发送短信通知
send_sms_notification(doctor.phone, consultation_id)
```

## 注意事项

1. **医生状态管理**：确保医生状态正确更新，避免分配离线医生
2. **并发处理**：在高并发情况下，可能需要添加分布式锁
3. **性能优化**：大量咨询时，考虑使用缓存优化查询性能
4. **监控告警**：建议添加分配失败率监控和告警机制
