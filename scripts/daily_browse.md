# 小红书养号任务

## ⚠️ 严重警告：禁止使用 browser_use！

### 🚨 绝对禁止

```
❌ browser_use action=start        ← 这是无头浏览器！禁止！
❌ browser_use action=open         ← 无头浏览器！禁止！
❌ browser_use action=snapshot     ← 无头浏览器！禁止！

为什么禁止？
- browser_use 使用 Playwright 无头浏览器
- 默认分辨率 1280x720（容易被识别）
- 没有用户 Cookie（无法保持登录）
- 极易被小红书反爬虫系统识别并封号
```

### ✅ 必须使用 Chrome DevTools MCP

```
✅ mcporter call chrome-devtools.* ← 连接本地 Chrome！必须！
✅ 本地 Chrome 有用户 Cookie
✅ 本地 Chrome 有登录状态
✅ 截图分辨率 2400x1384（真实浏览器）
```

---

## 任务目标

使用 **Chrome DevTools MCP** 连接本地 Chrome 浏览器，模拟正常用户浏览小红书。

---

## 执行步骤（必须严格按顺序）

### ⭐ 第零步：使用 Chrome DevTools MCP 打开小红书

**⚠️ 必须首先执行此步骤，使用 mcporter 调用！**

```bash
# 1. 列出可用工具（可选）
mcporter list chrome-devtools

# 2. 导航到小红书（必须使用这个命令）
mcporter call chrome-devtools.navigate_page --args '{"type": "url", "url": "https://www.xiaohongshu.com"}'

# 3. 获取页面快照
mcporter call chrome-devtools.take_snapshot

# 4. 截图保存
mcporter call chrome-devtools.take_screenshot --args '{"filename": "/Users/qf/.copaw/workspaces/qwq-automation/hongshutiao/logs/screenshot.png"}'

# 注意：截图会保存到临时目录，需要手动复制：
cp /var/folders/*/chrome-devtools-mcp-*/screenshot.png /Users/qf/.copaw/workspaces/qwq-automation/hongshutiao/logs/screenshot.png
```

### 第一步：检查登录状态

查看快照内容，判断是否已登录：

```
已登录标志：
- 页面有"我"链接（个人主页）
- 页面右上角有头像
- URL 包含 /user/profile/

未登录标志：
- 页面显示"登录"按钮
- 页面显示二维码
- 没有"我"链接
```

**如果未登录：**
1. 截图发送给用户
2. 发送钉钉通知：⚠️ 小红书需要登录，请扫码
3. 等待用户回复「已登录」
4. 重新获取快照确认

### 第二步：搜索关键词

```bash
# 1. 获取快照，找到搜索框 uid
mcporter call chrome-devtools.take_snapshot | grep "搜索小红书"

# 2. 在搜索框输入关键词
mcporter call chrome-devtools.fill --args '{"uid": "搜索框的uid", "value": "红利指数"}'

# 3. 按回车搜索
mcporter call chrome-devtools.press_key --args '{"key": "Enter"}'

# 4. 等待结果加载
sleep 2

# 5. 获取搜索结果快照
mcporter call chrome-devtools.take_snapshot
```

### 第三步：浏览帖子

```bash
# 1. 滚动页面
mcporter call chrome-devtools.evaluate_script --args '{"function": "function() { window.scrollBy(0, 500); return true; }"}'

# 2. 找到帖子链接
mcporter call chrome-devtools.take_snapshot | grep "link.*note"

# 3. 点击帖子
mcporter call chrome-devtools.click --args '{"uid": "帖子链接的uid"}'

# 4. 等待帖子加载
sleep 3

# 5. 在帖子内滚动浏览
mcporter call chrome-devtools.evaluate_script --args '{"function": "function() { window.scrollBy(0, 300); return true; }"}'
```

### 第四步：点赞/收藏（可选）

```bash
# 1. 找到点赞按钮 uid
mcporter call chrome-devtools.take_snapshot | grep "点赞|like"

# 2. 点击点赞
mcporter call chrome-devtools.click --args '{"uid": "点赞按钮uid"}'
```

### 第五步：记录日志

```python
# 保存浏览日志到 hongshutiao/logs/browse_*.jsonl
# 格式：
{
    "timestamp": "2026-03-28T12:00:00",
    "browser_type": "local_chrome",  # 必须是 local_chrome
    "login_status": "logged_in",
    "keywords_searched": ["红利指数"],
    "posts_viewed": 5,
    "duration_seconds": 120
}
```

---

## 关键命令速查表

| 操作 | 命令 |
|-----|------|
| 打开页面 | `mcporter call chrome-devtools.navigate_page --args '{"type": "url", "url": "https://..."}'` |
| 获取快照 | `mcporter call chrome-devtools.take_snapshot` |
| 截图 | `mcporter call chrome-devtools.take_screenshot --args '{"filename": "...png"}'` |
| 点击元素 | `mcporter call chrome-devtools.click --args '{"uid": "..."}'` |
| 输入文字 | `mcporter call chrome-devtools.fill --args '{"uid": "...", "value": "..."}'` |
| 按键 | `mcporter call chrome-devtools.press_key --args '{"key": "Enter"}'` |
| 滚动页面 | `mcporter call chrome-devtools.evaluate_script --args '{"function": "function() { window.scrollBy(0, 500); return true; }"}'` |
| 列出页面 | `mcporter call chrome-devtools.list_pages` |

---

## 安全检查清单

每次汇报时必须包含：

- [ ] 是否使用 `mcporter call chrome-devtools.*`？
- [ ] 截图分辨率是否 > 2000px？（确认是本地 Chrome）
- [ ] 是否先检查登录状态？
- [ ] 登录状态是否保持？

---

## 常见错误

| 错误 | 原因 | 解决 |
|-----|------|------|
| `Tool navigate not found` | 用了错误的工具名 | 使用 `navigate_page` |
| 截图分辨率 1280x720 | 使用了 browser_use | 改用 Chrome DevTools MCP |
| 未登录状态 | 无头浏览器无 Cookie | 使用本地 Chrome |
| `fn is not a function` | evaluate_script 格式错误 | 使用 `function() {...}` 格式 |

---

**创建时间**: 2026-03-27
**更新时间**: 2026-03-28（添加明确调用示例和禁止 browser_use）
**负责人**: 靑枫QwQ_cool
**指导人**: 靑枫claw