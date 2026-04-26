# 持久化改造实施计划

## 概述

将子网规划、子网切分、高级工具模块中的历史数据、列表数据持久化到已有的 `SubnetPlanner_data.db` 数据库中，数据库初始化时插入程序中现有的样例数据。

---

## 需要持久化的数据清单

### 1. 子网规划模块
| 数据 | 当前变量 | 当前类型 | 默认样例数据 |
|------|----------|----------|-------------|
| 下拉表历史(IPv4) | `planning_parent_networks_v4` | deque(maxlen=100) | `["10.21.48.0/20", "192.168.0.0/16"]` |
| 下拉表历史(IPv6) | `planning_parent_networks_v6` | deque(maxlen=100) | `["2001:0db8::/32", "fe80::/10"]` |
| 子网需求表 | `requirements_tree` (Treeview) | ttk.Treeview | 10条: office(20), hr_department(10), finance_department(10), planning_department(30), legal(10), procurement(10), security(10), party(20), discipline(10), it_department(20) |
| 需求池表 | `pool_tree` (Treeview) | ttk.Treeview | 5条: engineering(20), sales(20), rd(15), production(100), transportation(20) |

### 2. 子网切分模块
| 数据 | 当前变量 | 当前类型 | 默认样例数据 |
|------|----------|----------|-------------|
| 父网段历史(IPv4) | `split_parent_networks_v4` | deque(maxlen=100) | `["10.0.0.0/8", "172.16.0.0/12"]` |
| 父网段历史(IPv6) | `split_parent_networks_v6` | deque(maxlen=100) | `["2001:0db8::/32", "fe80::/10"]` |
| 切分段历史(IPv4) | `split_networks_v4` | deque(maxlen=100) | `["10.21.50.0/23", "172.20.180.0/24"]` |
| 切分段历史(IPv6) | `split_networks_v6` | deque(maxlen=100) | `["2001:0db8::/64", "fe80::1/128"]` |
| 切分历史记录 | `history_records` | list[dict] | `[]` (空列表，运行时产生) |

### 3. 高级工具模块
| 数据 | 当前变量 | 当前类型 | 默认样例数据 |
|------|----------|----------|-------------|
| IPv4查询下拉表历史 | `ipv4_history` | list | `["192.168.1.1", "10.0.0.1"]` |
| IPv6查询下拉表历史 | `ipv6_history` | list | `["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "fe80::1"]` |
| 子网合并列表 | `subnet_merge_text` (tk.Text) | tk.Text | 15行CIDR子网 |
| 范围起始下拉表历史 | `range_start_history` | list | `["192.168.0.1", "10.0.0.1", "2001:db8::1", "fe80::1"]` |
| 范围结束下拉表历史 | `range_end_history` | list | `["192.168.30.254", "10.0.0.254", "2001:db8::100", "fe80::100"]` |
| 重叠检测列表 | `overlap_text` (tk.Text) | tk.Text | 12行CIDR子网 |

---

## 数据库表设计

### 表1: `combo_history` — 下拉表历史
存储所有下拉框的历史记录，通过 `category` 字段区分不同用途。

```sql
CREATE TABLE IF NOT EXISTS combo_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    value TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    UNIQUE(category, value)
)
```

`category` 取值：
- `planning_parent_v4` — 子网规划IPv4父网段历史
- `planning_parent_v6` — 子网规划IPv6父网段历史
- `split_parent_v4` — 子网切分IPv4父网段历史
- `split_parent_v6` — 子网切分IPv6父网段历史
- `split_network_v4` — 子网切分IPv4切分段历史
- `split_network_v6` — 子网切分IPv6切分段历史
- `ipv4_query` — IPv4查询历史
- `ipv6_query` — IPv6查询历史
- `range_start` — IP范围起始历史
- `range_end` — IP范围结束历史

### 表2: `requirements_data` — 子网需求/需求池数据
存储子网需求表和需求池的行数据。

```sql
CREATE TABLE IF NOT EXISTS requirements_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_type TEXT NOT NULL,
    name TEXT NOT NULL,
    hosts INTEGER NOT NULL,
    sort_order INTEGER NOT NULL
)
```

`table_type` 取值：
- `requirements` — 子网需求表
- `pool` — 需求池

### 表3: `split_history` — 切分历史记录
存储子网切分操作的完整历史记录。

```sql
CREATE TABLE IF NOT EXISTS split_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent TEXT NOT NULL,
    split TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(parent, split)
)
```

### 表4: `text_data` — 文本数据
存储子网合并和重叠检测的多行文本内容。

```sql
CREATE TABLE IF NOT EXISTS text_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TEXT,
    UNIQUE(category)
)
```

`category` 取值：
- `subnet_merge` — 子网合并列表
- `overlap_detection` — 重叠检测列表

---

## 实施步骤

### 步骤1: 创建 `HistorySQLite` 数据库访问类

**文件**: `services/history_sqlite.py` (新建)

创建 `HistorySQLite` 类，负责所有历史数据的数据库操作：

1. **`__init__`**: 连接到 `SubnetPlanner_data.db`，调用 `init_db()`
2. **`init_db()`**: 创建4张新表（combo_history, requirements_data, split_history, text_data），如果表为空则插入样例数据
3. **下拉表历史 CRUD**:
   - `load_combo_history(category)` → 返回 `list[str]`
   - `save_combo_history(category, values)` → 保存整个列表（先删后插）
   - `add_combo_history_item(category, value)` → 添加单条记录
4. **子网需求/需求池 CRUD**:
   - `load_requirements_data(table_type)` → 返回 `list[tuple(name, hosts)]`
   - `save_requirements_data(table_type, data_list)` → 保存整个列表
5. **切分历史记录 CRUD**:
   - `load_split_history()` → 返回 `list[dict]`
   - `add_split_record(parent, split)` → 添加单条记录
   - `delete_split_record(parent, split)` → 删除单条记录
   - `clear_split_history()` → 清空所有记录
6. **文本数据 CRUD**:
   - `load_text_data(category)` → 返回 `str`
   - `save_text_data(category, content)` → 保存文本内容（UPSERT）

### 步骤2: 修改 `HistoryRepository` 集成持久化

**文件**: `services/history_repository.py` (修改)

1. 在 `__init__` 中创建 `HistorySQLite` 实例
2. 修改初始化逻辑：从数据库加载数据而非硬编码默认值
3. 修改 `update_history()` 方法：更新内存后同步写入数据库
4. 修改 `update_history_entry()` 方法：更新内存后同步写入数据库
5. 修改 `add_split_record()` 方法：写入内存后同步写入数据库
6. 新增方法：
   - `save_combo_history_to_db(category)` — 将内存中的下拉表历史持久化到数据库
   - `save_requirements_to_db(table_type, data)` — 将需求/需求数据持久化到数据库
   - `save_text_data_to_db(category, content)` — 将文本数据持久化到数据库
   - `load_text_data_from_db(category)` — 从数据库加载文本数据

### 步骤3: 修改 `windows_app.py` 适配持久化

**文件**: `windows_app.py` (修改)

1. **移除硬编码的默认样例数据**：
   - `planning_parent_networks_v4/v6` 不再硬编码初始值，从数据库加载
   - `split_parent_networks_v4/v6` 不再硬编码初始值，从数据库加载
   - `split_networks_v4/v6` 不再硬编码初始值，从数据库加载
   - `ipv4_history`、`ipv6_history`、`range_start_history`、`range_end_history` 不再硬编码初始值

2. **子网需求/需求池加载**：
   - 修改需求表和需求池的初始化逻辑，从数据库加载数据而非硬编码
   - 如果数据库中有数据则使用数据库数据，否则使用样例数据（首次运行时数据库初始化已插入样例）

3. **子网合并/重叠检测文本加载**：
   - 修改 `subnet_merge_text` 的初始化，从数据库加载内容
   - 修改 `overlap_text` 的初始化，从数据库加载内容

4. **数据变更时保存到数据库**：
   - 子网需求/需求池变更（添加、删除、交换、导入、撤销/重做）后调用保存方法
   - 子网合并文本变更后保存到数据库
   - 重叠检测文本变更后保存到数据库
   - 切分历史记录变更后保存到数据库

### 步骤4: 样例数据插入

在 `HistorySQLite.init_db()` 中，创建表后检查各表是否为空，如果为空则插入样例数据：

- **combo_history 表样例数据**:
  - planning_parent_v4: "10.21.48.0/20", "192.168.0.0/16"
  - planning_parent_v6: "2001:0db8::/32", "fe80::/10"
  - split_parent_v4: "10.0.0.0/8", "172.16.0.0/12"
  - split_parent_v6: "2001:0db8::/32", "fe80::/10"
  - split_network_v4: "10.21.50.0/23", "172.20.180.0/24"
  - split_network_v6: "2001:0db8::/64", "fe80::1/128"
  - ipv4_query: "192.168.1.1", "10.0.0.1"
  - ipv6_query: "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "fe80::1"
  - range_start: "192.168.0.1", "10.0.0.1", "2001:db8::1", "fe80::1"
  - range_end: "192.168.30.254", "10.0.0.254", "2001:db8::100", "fe80::100"

- **requirements_data 表样例数据**:
  - requirements: office(20), hr_department(10), finance_department(10), planning_department(30), legal(10), procurement(10), security(10), party(20), discipline(10), it_department(20)
  - pool: engineering(20), sales(20), rd(15), production(100), transportation(20)

- **text_data 表样例数据**:
  - subnet_merge: 15行CIDR子网文本
  - overlap_detection: 12行CIDR子网文本

---

## 历史记录数量上限配置

所有历史记录在代码中设置统一的数量上限，达到上限后自动删除最早的记录。下拉表历史和切分历史记录分开设定上限。

### 配置常量（定义在 `HistorySQLite` 类中）

```python
class HistorySQLite:
    # 下拉表历史记录数量上限（适用于所有 combo_history 类别）
    MAX_COMBO_HISTORY_ITEMS = 100

    # 切分历史记录数量上限（适用于 split_history 表）
    MAX_SPLIT_HISTORY_ITEMS = 500
```

### 上限执行逻辑

1. **下拉表历史**：
   - 每次添加新记录后，检查该 category 下的记录总数
   - 如果超过 `MAX_COMBO_HISTORY_ITEMS`，按 `sort_order` 升序（即最早的记录）删除多余记录
   - 在 `add_combo_history_item()` 和 `save_combo_history()` 方法中执行

2. **切分历史记录**：
   - 每次添加新记录后，检查 `split_history` 表的记录总数
   - 如果超过 `MAX_SPLIT_HISTORY_ITEMS`，按 `created_at` 升序（即最早的记录）删除多余记录
   - 在 `add_split_record()` 方法中执行

3. **内存与数据库同步**：
   - `HistoryRepository` 中的 `deque(maxlen=100)` 保持不变，与 `MAX_COMBO_HISTORY_ITEMS` 对应
   - 数据库层面额外做一次上限检查，确保数据一致性

---

## 关键设计决策

1. **使用同一数据库文件**: 直接使用 `SubnetPlanner_data.db`，通过 `get_app_directory()` 获取路径
2. **独立的数据库访问类**: 创建 `HistorySQLite` 类，与 `IPAMSQLite` 平级，职责分离
3. **样例数据仅在首次初始化时插入**: 通过检查表是否为空来判断是否需要插入样例数据
4. **下拉表历史采用全量替换策略**: 每次保存时先删除该 category 的所有记录再重新插入，避免排序混乱
5. **需求/需求池采用全量替换策略**: 每次保存时先删除该 table_type 的所有记录再重新插入
6. **文本数据采用 UPSERT 策略**: 使用 INSERT OR REPLACE 保证每个 category 只有一条记录
7. **切分历史记录采用增量插入策略**: 逐条添加，避免重复
8. **历史记录数量上限**: 下拉表历史和切分历史记录分别设定上限，达到上限后自动删除最早记录

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `services/history_sqlite.py` | 新建 | 历史数据数据库访问类 |
| `services/history_repository.py` | 修改 | 集成 HistorySQLite，数据从数据库加载，变更时同步写入 |
| `windows_app.py` | 修改 | 移除硬编码默认值，从数据库加载数据，变更时触发持久化 |
