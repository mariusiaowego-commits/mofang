# mofang AGENTS

三阶魔方速拧学习系统。profile scout 开发，非用户本人项目。

## 项目路径
`/Users/mt16/dev/mofang`

## 技术栈
- Markdown + Obsidian 风格文档
- Python 辅助脚本 (training/)
- 公式图（PLL/OLL）

## 前端参考
- `mofang-demo.html` — 产品概念 UI demo (40K, 单文件 HTML)
  - 双用户对比 (yoyoba + 女儿) + CFOP 4 段进度 + 5 KPI tile + 4 主题色板
  - 以后做真前端页面 (Web dashboard / iPad) 时参考
  - 打开: `open mofang-demo.html` (浏览器开, Cmd+Shift+4 截屏)
  - 数据基于真实 PRD: dashboard.py / user_manager.py / curses_app.py 字段
  - 提交: `e730719` (2026-06-17)

## 核心内容

### 教程 (docs/)
- 01-入门教程（层先法，2分钟内还原目标）
- 02-CFOP教程（进阶，1分钟内目标）
- 03-进阶技巧（F2L/OLL/PLL）
- 04-肌肉记忆训练
- 05-比赛策略

### 公式库 (formulas/)
- cfop/ — CFOP 全套公式
- oll-cases/ — OLL 57 个情况
- pll-cases/ — PLL 21 个情况
- f2l-cases/ — F2L 各情况

### 训练 (training/)
- daily-log.md — 每日训练记录
- progress-tracker.md — 进度跟踪
- templates/ — 记录模板

### 知识库 (knowledge/)
- 魔方基础概念/术语表/历史与名人

## 学习路线图
1. 入门：层先法（2分钟内）
2. 进阶：CFOP 基础（1分钟内）
3. 熟练：7个十字 OLL + 21 PLL（30秒内）
4. 高手：完整 OLL 57个（15秒内）
5. 顶级：COLL/ZBLL（10秒内）

## 训练指标
- Single：单次还原时间
- AO5：5次平均（去最快最慢）
- AO12：12次平均
- PB：Personal Best

## 注意
- 非用户本人开发，是 profile scout 的项目
- 详细开发记录在 docs/03-开发文档/

## 收尾文档
- STATUS.md — **无**（mofang 不使用 STATUS.md）
- DEV_PLAN.md — **无**
- vibe coding log — `docs/03-开发文档/Coding Log.md`
- wiki — **无**

## Repo owner

GitHub 账号: `mariusiaowego-commits`

⚠️ **拼写陷阱**: owner 中段是 5 字符 `o-w-e-g-o` (含 w), 容易被打成 4 字符 `u-e-g-o` (少 o 多 u, 漏掉 w)。任何 GH URL/repo/操作必须从本文件原样复制, 不可凭记忆打字。
