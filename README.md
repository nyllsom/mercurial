# Mercurial · 每日 arXiv 简报

**如液态金属般流动的前沿科学洞察**

---

## ✨ 核心特性

- **智能筛选** - 基于关键词与分类的多维度论文排序
- **优雅摘要** - 大型语言模型生成的流畅研究简报
- **灵活投递** - 支持邮件发送或本地存档
- **持久化存储** - SQLite 数据库记录所有历史记录
- **配置驱动** - 环境变量配置，无需修改代码

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，至少配置：
```env
# LLM 配置（支持 OpenAI 兼容 API）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# arXiv 订阅
ARXIV_CATEGORIES=cs.CL,cs.AI,cs.LG
KEYWORDS=llm,transformer,attention,language model
LOOKBACK_HOURS=24
TOP_PICKS=5
```

### 运行首次简报

```bash
# 生成今日简报（本地模式）
python -m mercurial.cli run-daily
```

简报将保存至 `data/digests/YYYY-MM-DD.md`

## ⚙️ 进阶配置

### 邮件投递

如需邮件发送，在 `.env` 中添加：

```env
# 邮件设置
SEND_EMAIL=1
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

### 自定义提示词

编辑 `mercurial/digest/prompts.py` 可调整简报风格与结构。

## 📁 项目结构

```
mercurial/
├── config.py              # 配置中心
├── cli.py                # 命令行入口
├── types.py              # 数据结构定义
├── sources/              # 数据源层
│   └── arxiv_client.py   # arXiv API 客户端
├── ranker/               # 排序层
│   └── simple_ranker.py  # 论文评分算法
├── digest/               # 摘要生成层
│   ├── prompts.py        # LLM 提示词模板
│   ├── generator.py      # 简报生成器
│   └── renderer.py       # Markdown → HTML 渲染
├── delivery/             # 投递层
│   └── emailer.py        # 邮件发送器
├── jobs/                 # 任务编排
│   └── daily_digest.py   # 每日简报流水线
└── db.py                 # 数据库层
```

## 🔧 开发模式

### 分层验证测试

项目设计支持逐步验证各组件：

```bash
# 仅测试 arXiv 数据拉取
python -m mercurial.cli fetch-only

# 测试排序算法
python -m mercurial.cli rank-only

# 测试 LLM 生成（不发送）
python -m mercurial.cli digest-only

# 完整流程（不发送邮件）
SEND_EMAIL=0 python -m mercurial.cli run-daily
```

### 调试数据库

```bash
# 查看已存储的论文
sqlite3 data/mercurial.db "SELECT * FROM papers LIMIT 5;"

# 查看历史简报
sqlite3 data/mercurial.db "SELECT date, status FROM digests ORDER BY date DESC;"
```

## 🧩 模块职责

| 模块 | 职责 | 输入 → 输出 |
|------|------|------------|
| `arxiv_client` | arXiv API 交互 | API 参数 → `List[Paper]` |
| `simple_ranker` | 论文评分排序 | `List[Paper]` → `List[RankedPaper]` |
| `generator` | LLM 简报生成 | `List[RankedPaper]` → Markdown |
| `emailer` | 邮件投递 | HTML + 元数据 → SMTP 发送 |
| `db` | 数据持久化 | 业务对象 ↔ SQLite |

## 🐛 故障排查

### 常见问题

1. **LLM API 连接失败**
   - 检查 `LLM_API_KEY` 和 `LLM_BASE_URL`
   - 验证网络连接

2. **arXiv 无返回结果**
   - 检查 `ARXIV_CATEGORIES` 格式
   - 调整 `LOOKBACK_HOURS` 值

3. **邮件发送超时**
   - 设置 `SEND_EMAIL=0` 跳过邮件测试
   - 检查防火墙/代理设置
   - 确认 SMTP 端口可访问

4. **重复发送**
   - 数据库确保幂等性
   - 使用 `--force` 强制重新生成

### 调试命令

```bash
# 强制重新生成今日简报
python -m mercurial.cli run-daily --force

# 指定日期生成
python -m mercurial.cli run-daily --date 2024-01-15
```

## 🧪 技术栈

- **Python 3.11+** - 核心运行时
- **SQLite** - 数据持久化
- **OpenAI API** - 大型语言模型
- **arXiv API** - 论文数据源
- **Jinja2** - 模板渲染
- **python-dotenv** - 配置管理

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 以改进 Mercurial。

---

> **设计哲学**：如液态金属般流动、自适应、表面张力形成完整边界，但保持内在流动性。代码应如汞珠般优雅聚合，各模块界限清晰而连接流畅。