# 咨询状态修复总结

## 问题描述

1. **ConsultationStatus未定义错误**: `完成咨询失败: name 'ConsultationStatus' is not defined`
2. **401 Unauthorized错误**: 医生端访问咨询相关API时出现认证失败

## 问题原因

### 1. ConsultationStatus未定义错误
在 `services/doctor_service.py` 中的以下方法使用了硬编码的字符串而不是 `ConsultationStatus` 枚举：
- `update_doctor_consultation_count()` 方法
- `get_available_doctors()` 方法

### 2. 401 Unauthorized错误
可能的原因：
- 医生没有正确登录
- 会话过期
- 医生认证信息不完整

## 修复方案

### 1. 修复ConsultationStatus使用

#### 修复 `update_doctor_consultation_count` 方法
```python
# 修复前
current_count = self.dao._MongoDao__db["consultations"].count_documents({
    "assigned_doctor_id": doctor_id,
    "status": {"$in": ["in_progress", "paid"]}
})

# 修复后
current_count = self.dao._MongoDao__db["consultations"].count_documents({
    "assigned_doctor_id": doctor_id,
    "status": {"$in": [ConsultationStatus.IN_PROGRESS.value, ConsultationStatus.PAID.value]}
})
```

#### 修复 `get_available_doctors` 方法
```python
# 修复前
current_count = self.dao._MongoDao__db["consultations"].count_documents({
    "assigned_doctor_id": doctor["id"],
    "status": {"$in": ["in_progress", "paid"]}
})

# 修复后
current_count = self.dao._MongoDao__db["consultations"].count_documents({
    "assigned_doctor_id": doctor["id"],
    "status": {"$in": [ConsultationStatus.IN_PROGRESS.value, ConsultationStatus.PAID.value]}
})
```

### 2. 检查医生认证状态

创建了测试脚本 `test_doctor_auth.py` 来检查：
- 医生数据是否正确
- 医生登录功能是否正常
- 医生咨询获取是否正常

## 修复的文件

1. **services/doctor_service.py** - 修复ConsultationStatus使用
2. **test_doctor_auth.py** - 医生认证测试脚本

## 验证方法

### 1. 运行医生认证测试
```bash
python test_doctor_auth.py
```

### 2. 检查医生登录状态
确保医生已经正确登录，会话中包含医生信息。

### 3. 检查API访问
确保访问医生相关API时使用正确的认证信息。

## 预期结果

修复后：
1. 不再出现 `ConsultationStatus` 未定义错误
2. 医生端API访问正常，不再出现401错误
3. 医生咨询功能正常工作

## 注意事项

1. **枚举使用**: 始终使用枚举值而不是硬编码字符串
2. **认证状态**: 确保医生正确登录并保持会话
3. **错误处理**: 添加适当的错误处理和日志记录

## 相关枚举值

- `ConsultationStatus.IN_PROGRESS.value` = "in_progress"
- `ConsultationStatus.PAID.value` = "paid"
- `ConsultationStatus.COMPLETED.value` = "completed"
- `ConsultationStatus.PENDING.value` = "pending"

## 故障排除

如果仍然出现问题：

1. 检查医生是否正确登录
2. 确认会话中是否包含医生信息
3. 检查数据库中的医生记录是否完整
4. 查看详细的错误日志
