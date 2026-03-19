# IP-hiofd 项目更新说明

## v0.1.2（稳定性修复）

### 修复点
- 修复偶发 `query_ip` 与 `result_ip` 不一致的问题（页面旧结果脏读）。
- 查询触发改为单次点击，避免 click + Enter 双触发竞态。
- 等待条件升级为：`#resultIpAddress` 必须与输入 IP 完全一致。
- 内置重试机制（默认 3 次，间隔 1 秒）。

### CLI 新增参数
- `--timeout`（默认 90）
- `--retries`（默认 3）
- `--retry-delay`（默认 1.0）

## 版本升级：纯 Python Playwright 实现

### 更新内容
- 新增 `hiofd_client.py` - 完全替代原有的 Node.js 依赖
- 删除对 `hiofd_browser.js` 的依赖

### 主要改进

#### 1. 环境简化
- **不再需要 Node.js 环境** - 完全使用 Python
- **统一的依赖管理** - 只需要 Python 和 playwright

#### 2. 代码质量提升
- **完整的类型提示** - 使用 Python 3.10+ 的 `from __future__ import annotations`
- **数据结构化** - 使用 `dataclass` 封装查询结果
- **健壮的错误处理** - 包含 IP 验证和结果校验

#### 3. 功能增强
- **智能等待机制** - 使用 `wait_for_function` 等待查询完成
- **完整的事件触发** - 模拟真实的浏览器交互
- **结果验证** - 确保查询结果与输入 IP 一致

### 使用示例

```python
from hiofd_client import lookup_ip

result = lookup_ip("8.8.8.8")
print(f"ISP: {result.isp}")
print(f"位置: {result.location}")
```

### 命令行使用

```bash
# 基本查询
python hiofd_client.py 8.8.8.8

# JSON 格式输出
python hiofd_client.py 8.8.8.8 --json

# 自定义超时
python hiofd_client.py 8.8.8.8 --timeout 30
```

### 向后兼容性

新的 `hiofd_client.py` 提供了与原有 `hiofd_browser.py` 类似的功能，但具有更好的稳定性和更完整的特性。

### 依赖要求
- Python 3.7+
- playwright >= 1.40.0

### 安装 playwright
```bash
pip install playwright
playwright install chromium
```