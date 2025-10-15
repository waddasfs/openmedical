# 医生档案修复总结

## 问题描述

医生端点开实时聊天时显示"加载消息失败，请重试"，后端报错：

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for DoctorResponse
current_consultation_count
  Field required [type=missing, input_value={'id': '68eef8f322f67f339...': 3, 'is_active': True}, input_type=dict]
```

## 问题原因

1. **模型字段缺失**: `DoctorResponse` 模型需要 `current_consultation_count` 字段，但在创建响应对象时没有提供
2. **数据库字段缺失**: 现有医生记录中可能没有 `current_consultation_count` 字段
3. **服务方法不完整**: 获取医生的方法没有确保返回完整的字段

## 修复方案

### 1. 修复API响应 (`main.py`)

在 `get_doctor_profile` 端点中添加 `current_consultation_count` 字段：

```python
return DoctorResponse(
    # ... 其他字段 ...
    total_consultations=db_doctor.total_consultations,
    current_consultation_count=db_doctor.current_consultation_count,  # 新增
    total_earnings=db_doctor.total_earnings,
    # ... 其他字段 ...
)
```

### 2. 修复医生服务 (`services/doctor_service.py`)

在所有获取医生的方法中确保包含 `current_consultation_count` 字段：

```python
# 确保包含current_consultation_count字段
if "current_consultation_count" not in doctor_data:
    doctor_data["current_consultation_count"] = 0
```

修复的方法包括：
- `get_doctor_by_id()`
- `get_doctor_by_google_id()`
- `get_doctor_by_email()`

### 3. 数据库更新脚本 (`update_doctor_records.py`)

创建脚本更新现有医生记录，添加 `current_consultation_count` 字段：

```python
# 计算当前咨询数量
current_count = mongo_dao._MongoDao__db["consultations"].count_documents({
    "assigned_doctor_id": doctor_id,
    "status": {"$in": ["in_progress", "paid"]}
})

# 更新医生记录
mongo_dao._MongoDao__db["doctors"].update_one(
    {"_id": ObjectId(doctor_id)},
    {"$set": {"current_consultation_count": current_count}}
)
```

## 修复的文件

1. **main.py** - 修复API响应
2. **services/doctor_service.py** - 修复服务方法
3. **update_doctor_records.py** - 数据库更新脚本
4. **test_doctor_profile_fix.py** - 测试脚本

## 验证方法

### 1. 运行数据库更新脚本
```bash
python update_doctor_records.py
```

### 2. 运行测试脚本
```bash
python test_doctor_profile_fix.py
```

### 3. 启动服务测试
```bash
python main.py
```

然后访问医生端页面测试实时聊天功能。

## 预期结果

修复后，医生端实时聊天应该能够正常加载，不再出现 `current_consultation_count` 字段缺失的错误。

## 注意事项

1. **向后兼容**: 修复确保现有医生记录能够正常工作
2. **数据一致性**: 当前咨询数量需要实时计算和更新
3. **错误处理**: 添加了字段缺失的默认值处理

## 相关字段说明

- `current_consultation_count`: 医生当前进行中的咨询数量
- `total_consultations`: 医生总咨询次数
- 状态为 `in_progress` 或 `paid` 的咨询计入当前咨询数量
