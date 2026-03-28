# Errors Log

记录执行过程中的错误和违规行为，以便持续改进。

---

## 2026-03-28: 智能体违规使用无头浏览器

### 错误描述

智能体 **qwq-automation** 在执行小红书养号任务时，**违规使用了 browser_use 无头浏览器**，而不是按要求使用 Chrome DevTools MCP 连接本地 Chrome 浏览器。

### 证据

| 对比项 | 智能体执行（错误） | 正确执行 |
|-------|-------------------|---------|
| 截图分辨率 | 1280x720 | 2400x1384 |
| 文件大小 | 377KB | 2.1MB |
| 浏览器类型 | browser_use (Playwright 无头) | Chrome DevTools MCP (本地 Chrome) |
| 登录状态 | 未登录（无头浏览器无 Cookie） | 已登录（本地 Chrome 有 Cookie） |

### 问题根源

1. 智能体没有区分 `browser_use` 和 `Chrome DevTools MCP`
2. 智能体习惯性地使用了 `browser_use`（它常用的浏览器工具）
3. 指令不够明确，没有提供具体的调用示例

### 影响

- 无头浏览器没有登录状态 → 小红书识别为新设备
- 无头浏览器容易被反爬虫系统识别 → 可能导致封号
- 用户扫码登录的是无头浏览器，不是本地 Chrome → 登录状态无法保留

### 正确做法

**必须使用 Chrome DevTools MCP 连接本地 Chrome：**

```bash
# ❌ 错误：不要使用 browser_use
browser_use action=start  # 这是无头浏览器！

# ✅ 正确：使用 Chrome DevTools MCP
mcporter call chrome-devtools.navigate_page --args '{"type": "url", "url": "https://www.xiaohongshu.com"}'
mcporter call chrome-devtools.take_snapshot
mcporter call chrome-devtools.take_screenshot --args '{"filename": "/path/to/screenshot.png"}'
mcporter call chrome-devtools.click --args '{"uid": "element_uid"}'
mcporter call chrome-devtools.fill --args '{"uid": "input_uid", "value": "搜索内容"}'
mcporter call chrome-devtools.evaluate_script --args '{"function": "function() { window.scrollBy(0, 500); return true; }"}'
```

### 纠正措施

1. **更新指令**：明确禁止 browser_use，提供 Chrome DevTools MCP 调用示例
2. **增加检查**：汇报时必须检查截图分辨率，确认是本地 Chrome
3. **教育智能体**：让 qwq-automation 明确区分两种工具

### 教训总结

| 教训 | 说明 |
|-----|------|
| 工具区分至关重要 | browser_use ≠ Chrome DevTools MCP |
| 提供具体示例 | 指令不能只说"使用 Chrome MCP"，要提供具体命令 |
| 检查机制必要 | 通过截图分辨率可以识别浏览器类型 |
| 本地浏览器优势 | 有用户 Cookie，避免反爬虫检测 |

---

**严重程度：高** ⚠️

**分类：安全违规**

**责任人：qwq-automation**

---