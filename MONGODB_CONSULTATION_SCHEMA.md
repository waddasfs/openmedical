# MongoDB Consultation 集合结构设计

## 集合名称
`consultation`

## 字段结构

### 基础字段
| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `_id` | ObjectId | 是 | MongoDB自动生成的唯一标识 | `ObjectId("...")` |
| `user_id` | String | 是 | 用户ID | `"user_123456"` |
| `mode` | String | 是 | 咨询模式 | `"realtime"` 或 `"onetime"` |
| `status` | String | 是 | 咨询状态 | `"pending"`, `"paid"`, `"in_progress"`, `"completed"`, `"cancelled"` |

### 咨询内容字段
| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `disease_description` | String | 是 | 疾病描述 | `"头痛、发热3天"` |
| `symptoms` | String | 否 | 症状描述 | `"持续性头痛，体温38.5°C"` |
| `medical_history` | String | 否 | 病史记录 | `"无特殊病史"` |
| `attachments` | Array[String] | 否 | 附件文件路径列表 | `["uploads/file1.jpg", "uploads/file2.pdf"]` |

### 医生相关字段
| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `doctor_level` | String | 否 | 医生等级 | `"normal"`, `"senior"`, `"expert"` |
| `assigned_doctor_id` | String | 否 | 分配的医生ID | `"doctor_001"` |
| `package_id` | String | 否 | 咨询套餐ID | `"package_normal"` |

### 支付相关字段
| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `price_usdt` | Number | 是 | 咨询费用(USDT) | `10.0` |
| `payment_order_id` | String | 否 | 支付订单ID | `"order_123456"` |

### 时间字段
| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `created_at` | Date | 是 | 创建时间 | `ISODate("2024-01-15T10:30:00Z")` |
| `updated_at` | Date | 是 | 更新时间 | `ISODate("2024-01-15T10:30:00Z")` |
| `started_at` | Date | 否 | 开始时间 | `ISODate("2024-01-15T11:00:00Z")` |
| `completed_at` | Date | 否 | 完成时间 | `ISODate("2024-01-15T12:00:00Z")` |

## 示例文档

### 实时咨询示例
```json
{
  "_id": ObjectId("65a1b2c3d4e5f6789012345"),
  "user_id": "user_123456",
  "mode": "realtime",
  "status": "paid",
  "disease_description": "头痛、发热3天",
  "symptoms": "持续性头痛，体温38.5°C，伴有恶心",
  "medical_history": "无特殊病史，无药物过敏",
  "attachments": [
    "uploads/20240115_103000_abc123.jpg",
    "uploads/20240115_103001_def456.pdf"
  ],
  "doctor_level": null,
  "assigned_doctor_id": "doctor_001",
  "package_id": null,
  "price_usdt": 20.0,
  "payment_order_id": "order_789012",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z"),
  "started_at": ISODate("2024-01-15T11:00:00Z"),
  "completed_at": null
}
```

### 一次性咨询示例
```json
{
  "_id": ObjectId("65a1b2c3d4e5f6789012346"),
  "user_id": "user_123456",
  "mode": "onetime",
  "status": "completed",
  "disease_description": "皮肤过敏症状",
  "symptoms": "手臂出现红色皮疹，伴有瘙痒",
  "medical_history": "有花粉过敏史",
  "attachments": [
    "uploads/20240115_140000_ghi789.jpg"
  ],
  "doctor_level": "normal",
  "assigned_doctor_id": "doctor_002",
  "package_id": "package_normal",
  "price_usdt": 10.0,
  "payment_order_id": "order_789013",
  "created_at": ISODate("2024-01-15T14:00:00Z"),
  "updated_at": ISODate("2024-01-15T16:00:00Z"),
  "started_at": ISODate("2024-01-15T15:00:00Z"),
  "completed_at": ISODate("2024-01-15T16:00:00Z")
}
```

## 索引设计

### 主要索引
```javascript
// 用户ID索引（用于查询用户的所有咨询）
db.consultation.createIndex({"user_id": 1})

// 状态索引（用于按状态查询）
db.consultation.createIndex({"status": 1})

// 创建时间索引（用于时间排序）
db.consultation.createIndex({"created_at": -1})

// 复合索引：用户ID + 创建时间（用于用户咨询历史排序）
db.consultation.createIndex({"user_id": 1, "created_at": -1})

// 医生ID索引（用于医生查询分配的咨询）
db.consultation.createIndex({"assigned_doctor_id": 1})

// 支付订单ID索引（用于支付相关查询）
db.consultation.createIndex({"payment_order_id": 1})
```

## 查询示例

### 1. 查询用户的所有咨询
```javascript
db.consultation.find({"user_id": "user_123456"}).sort({"created_at": -1})
```

### 2. 查询特定状态的咨询
```javascript
db.consultation.find({"status": "completed"})
```

### 3. 查询医生分配的咨询
```javascript
db.consultation.find({"assigned_doctor_id": "doctor_001"})
```

### 4. 查询时间范围内的咨询
```javascript
db.consultation.find({
  "created_at": {
    "$gte": ISODate("2024-01-01T00:00:00Z"),
    "$lt": ISODate("2024-02-01T00:00:00Z")
  }
})
```

### 5. 分页查询
```javascript
db.consultation.find({"user_id": "user_123456"})
  .sort({"created_at": -1})
  .skip(0)
  .limit(10)
```

## 数据验证规则

### 1. 必填字段验证
- `user_id`: 不能为空
- `mode`: 必须是 "realtime" 或 "onetime"
- `status`: 必须是预定义的状态值
- `disease_description`: 不能为空
- `price_usdt`: 必须大于0
- `created_at`: 不能为空
- `updated_at`: 不能为空

### 2. 业务逻辑验证
- 一次性咨询必须指定 `doctor_level`
- 实时咨询的 `doctor_level` 可以为空
- `completed_at` 不能早于 `started_at`
- `started_at` 不能早于 `created_at`

### 3. 数据类型验证
- `price_usdt`: 必须是数字类型
- `attachments`: 必须是字符串数组
- 时间字段: 必须是Date类型

## 性能优化建议

1. **合理使用索引**: 根据查询模式创建合适的索引
2. **分页查询**: 使用skip和limit进行分页
3. **字段选择**: 只查询需要的字段
4. **数据归档**: 定期归档历史数据
5. **监控性能**: 定期检查查询性能

## 数据迁移

如果需要修改集合结构，建议：
1. 创建新的集合结构
2. 编写数据迁移脚本
3. 验证数据完整性
4. 切换应用指向新集合
5. 删除旧集合（可选）

