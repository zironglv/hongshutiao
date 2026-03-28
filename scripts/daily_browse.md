# 小红书养号任务

## ⚠️ 严格安全要求（必读）

### 🚨 绝对禁止事项

1. **禁止使用无头浏览器** - 极易被小红书识别并封禁
2. **禁止使用自动化浏览器** - 如 Puppeteer 无头模式
3. **禁止自动登录** - 必须由用户扫码完成登录
4. **禁止跳过登录检查** - 每次执行前必须检查

### ✅ 必须执行事项

1. **使用本地 Chrome 浏览器** - 通过 Chrome DevTools MCP
2. **保留登录 Cookie** - 使用用户数据目录
3. **检查登录状态** - 每次执行前必须检查
4. **未登录时通知用户** - 发送二维码让用户扫码

---

## 任务目标

使用 **Chrome DevTools MCP** 连接本地 Chrome 浏览器，模拟正常用户浏览小红书，实现养号目的。

---

## 执行频率

- 每天 1-2 次
- 时间：上午 10:30 或 晚上 20:00
- 每次浏览 5-15 分钟

---

## 执行步骤

### ⭐ 第零步：登录状态检查（必须先执行）

```
⚠️ 此步骤必须首先执行，不可跳过！

检查流程：
1. 使用 mcporter 调用 Chrome DevTools MCP
2. 获取当前页面列表
3. 打开小红书网站 https://www.xiaohongshu.com
4. 截图检查页面状态
5. 判断是否已登录：
   - 已登录：继续执行浏览任务
   - 未登录：停止任务，截图发送给用户，等待用户扫码

登录状态判断方法：
- 页面右上角有头像 = 已登录
- 页面显示登录按钮/二维码 = 未登录

未登录时处理：
1. 截图当前页面（包含二维码）
2. 发送钉钉通知给用户：
   "⚠️ 小红书需要登录！请查看截图，扫码登录后回复「已登录」继续。"
3. 等待用户确认后再继续
4. 严禁自动填写账号密码或跳过此步骤
```

### 第一步：打开小红书（使用本地 Chrome）

```
使用 Chrome DevTools MCP：
1. 调用 mcporter 连接本地 Chrome
2. 使用 navigate 打开 https://www.xiaohongshu.com
3. 等待页面加载完成
4. 截图确认页面状态

命令示例：
mcporter call chrome-devtools navigate --args '{"url": "https://www.xiaohongshu.com"}'
mcporter call chrome-devtools snapshot
```

### 第二步：随机浏览首页

```
1. 在首页随机滚动 2-3 次
2. 停留在任意帖子 3-5 秒
3. 模拟正常用户的随机行为
4. 不要快速操作，要有时间间隔
```

### 第三步：搜索关键词

从以下关键词中随机选择 2-4 个：

**核心关键词**：
- 红利指数
- 红利低波
- 股息率
- 红利ETF

**扩展关键词**：
- 定投红利
- 红利基金
- 高股息
- 稳健投资
- 被动收入

**长尾关键词**：
- 红利指数定投
- 中证红利
- 红利投资策略

### 第四步：浏览搜索结果

```
每个关键词：
1. 搜索后随机滚动 2-3 次
2. 点击进入 2-5 个帖子
3. 在每个帖子内：
   - 停留 10-30 秒
   - 随机滚动浏览
   - 以 30% 概率点赞
   - 以 20% 概率收藏
```

### 第五步：记录学习内容

```
浏览过程中，注意记录：
1. 热门标题格式
2. 高赞帖子特点
3. 用户讨论热点
4. 常见问题

保存到: hongshutiao/logs/browse_*.jsonl
```

### 第六步：关闭

```
1. 随机等待 1-3 分钟
2. 关闭标签页（不要关闭浏览器，保留 Cookie）
```

---

## 行为规范

### 要做的 ✅

- 使用本地 Chrome 浏览器（Chrome DevTools MCP）
- 先检查登录状态
- 随机时间间隔（模拟人类节奏）
- 鼠标滚动自然
- 停留时间合理
- 保持登录 Cookie

### 不要做的 ❌

- **禁止使用无头浏览器**
- **禁止使用自动化浏览器**
- **禁止自动登录**
- **禁止跳过登录检查**
- 不要快速连续点击
- 不要浏览太多帖子（单次不超过 20 个）
- 不要关闭整个浏览器（会丢失 Cookie）

---

## 登录异常处理流程

```
场景：检查登录状态时发现未登录

步骤：
1. 立即停止所有浏览操作
2. 截图当前页面（包含二维码）
3. 发送钉钉通知：
   ⚠️ 小红书需要登录
   
   请查看附件中的截图，使用手机小红书 APP 扫码登录。
   登录成功后，回复「已登录」，我将继续执行浏览任务。
   
   注意：请不要关闭浏览器窗口，否则登录状态会丢失。

4. 等待用户回复「已登录」
5. 重新检查登录状态
6. 确认登录后再继续浏览任务
```

---

## 日志记录

每次执行后记录：

```json
{
  "date": "2026-03-27",
  "time": "10:32:15",
  "login_status": "logged_in",
  "duration_seconds": 420,
  "keywords_searched": ["红利指数", "股息率"],
  "posts_viewed": 12,
  "actions": {
    "likes": 3,
    "collects": 2
  }
}
```

---

## 技术说明

### Chrome DevTools MCP

- 连接本地 Chrome 浏览器
- 使用 Chrome DevTools Protocol (CDP)
- 保留用户数据和 Cookie
- 不是无头模式

### 关键命令

```bash
# 列出可用工具
mcporter list chrome-devtools

# 打开页面
mcporter call chrome-devtools navigate --args '{"url": "https://www.xiaohongshu.com"}'

# 获取页面快照
mcporter call chrome-devtools snapshot

# 截图
mcporter call chrome-devtools screenshot --args '{"filename": "login_qrcode.png"}'

# 点击元素
mcporter call chrome-devtools click --args '{"uid": "element_uid"}'

# 输入文字
mcporter call chrome-devtools type --args '{"uid": "input_uid", "text": "红利指数"}'
```

---

**创建时间**: 2026-03-27
**负责人**: 靑枫QwQ_cool
**指导人**: 靑枫claw
**更新时间**: 2026-03-27（添加登录检查要求）