# WeChat Todo Skill for OpenClaw

## 项目简介

WeChat Todo Skill 是一个为 OpenClaw 平台开发的技能，用于解析微信数据库并分析聊天记录中的待办事项、关键事件和截止日期。该技能支持 macOS 和 Windows 平台，能够帮助用户快速获取聊天摘要和待办事项，提高工作效率。

## 功能特性

- **多平台支持**：兼容 macOS 和 Windows 操作系统
- **会话筛选**：通过群名、微信用户昵称（或备注名、微信号）获取对应会话
- **时间范围选择**：支持今日、昨日、本周或指定日期范围和时间段的分析
- **智能分析**：自动提取聊天摘要、关键事件、Todo待办事项以及DDL等信息
- **模糊匹配**：当会话名称存在多个匹配结果时，提供选择界面
- **JSON输出**：支持输出标准化的JSON结果，方便OpenClaw平台集成

## 技术栈

- Python 3.8+
- SQLite3
- 正则表达式
- 日期时间处理

## 安装方法

### 手动安装

1. 克隆项目到本地

```bash
git clone https://github.com/windycn/wechat-todo-skill.git
cd wechat-todo-skill
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 准备微信数据库

   - **Windows**：运行技能时会尝试自动提取微信密钥并解密数据库
   - **macOS**：技能会自动完成以下步骤：
     1. **检查微信版本**：确保微信版本为 4.x
     2. **退出微信**：执行 `killall WeChat`
     3. **Ad-hoc 签名**：执行 `sudo codesign --force --deep --sign - /Applications/WeChat.app`（需要输入密码）
     4. **重新打开微信**：重新启动并登录微信
     5. **安装 wechat-decrypt 工具**：自动克隆并安装 `https://github.com/ylytdeng/wechat-decrypt` 工具
     6. **提取密钥**：执行 `cd ~/.qclaw/workspace/wechat-decrypt && sudo ./find_all_keys_macos`
     7. **查找数据库**：自动查找微信数据目录，支持新旧路径
     8. **解密数据库**：自动运行 wechat-decrypt 工具解密数据库

   **注意**：如果自动流程失败，你可以手动执行上述步骤，然后将解密后的 `decrypted` 目录复制到项目根目录

### OpenClaw 自主安装

#### 方法一：本地会话安装

你可以通过自然语言对话让 OpenClaw 自主安装此技能：

1. 在 OpenClaw 聊天界面中，发送消息：
   - 例如：`请帮我安装XXX目录下微信待办分析技能`
   - 或：`我需要安装 XX/wechat-todo-skill 技能`

2. OpenClaw 会理解你的请求并自动安装技能

3. 安装完成后，你可以直接使用技能：
   - 例如：`请分析项目组的今日聊天记录`
   - 或：`帮我提取昨天的待办事项`

#### 方法二：在线命令安装

1. 在 OpenClaw 中，使用命令 `@install skill https://github.com/windycn/wechat-todo-skill`

2. OpenClaw 会自动克隆项目、安装依赖并注册技能

3. 安装完成后，你可以直接使用技能：
   - 例如：`@wechat-todo analyze "项目组" today`
   - 或：`@wechat-todo help` 获取帮助信息

#### 方法三：本地手动安装

如果你已经下载或克隆了项目到本地，可以通过以下步骤安装到 OpenClaw：

1. 克隆或下载项目到本地：

```bash
git clone https://github.com/windycn/wechat-todo-skill.git
cd wechat-todo-skill
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 在 OpenClaw 中，使用命令安装本地技能：

```
@install skill /path/to/wechat-todo-skill
```

4. 安装完成后，你可以直接使用技能：
   - 例如：`@wechat-todo analyze "项目组" today`
   - 或：`@wechat-todo help` 获取帮助信息

## 使用方式

### 命令行方式

```bash
# 基本使用（分析今日聊天记录）
python skill/main.py --session "会话名称"

# 分析指定日期范围的聊天记录
python skill/main.py --session "会话名称" --date-range "2026-01-01,2026-01-31"

# 分析指定日期范围和时间段的聊天记录
python skill/main.py --session "会话名称" --date-range "2026-01-01,2026-01-31" --time-range "09:00,18:00"

# 使用自定义数据库目录
python skill/main.py --db-dir "/path/to/decrypted" --session "会话名称"
```

### 预设时间范围

- `today`：今日
- `yesterday`：昨日
- `this_week`：本周

## 项目结构

```
wechat-todo-skill/
├── skill/              # OpenClaw skill目录
│   ├── __init__.py
│   ├── main.py          # 主入口
│   ├── SKILL.md         # OpenClaw技能配置
│   ├── scripts/         # 脚本目录
│   │   ├── __init__.py
│   │   ├── db_parser.py     # 数据库解析
│   │   ├── session_manager.py  # 会话管理
│   │   ├── config.py        # 配置管理
│   │   ├── analyzer.py      # 聊天分析
│   │   └── decryptor.py     # 解密模块
├── .gitignore
├── README.md
└── requirements.txt
```

## 工作原理

1. **数据库连接**：连接到解密后的微信数据库
2. **会话选择**：根据用户输入的关键词搜索并选择会话
3. **消息获取**：根据指定的时间范围获取消息
4. **数据分析**：分析消息内容，提取摘要、关键事件、待办事项和截止日期
5. **结果输出**：输出分析结果，包括文本和JSON格式

## 注意事项

1. 该技能需要访问解密后的微信数据库，确保你有权限访问这些数据
2. 首次运行时可能需要较长时间来解析数据库
3. 对于大型聊天记录，分析可能需要一些时间
4. 该技能仅在本地运行，不会上传任何数据到云端
5. 如果遇到任何问题，请查阅 `skill/troubleshooting.md` 文件获取详细的故障排除指南

## 性能优化

该技能采用了多种性能优化策略：

1. **数据库处理**：
   - 使用 wechat-decrypt 工具的批量解密功能
   - 利用工具的缓存机制，避免重复解密
   - 优先处理消息数据库

2. **分析处理**：
   - 使用集合存储关键词，提高查找速度
   - 预编译正则表达式，提高匹配速度
   - 增量分析，避免重复处理数据
   - 三级缓存机制，减少数据库查询
   - 对于大型聊天记录，采用分批处理
   - 优先处理最近的消息，提高响应速度
   - 利用多线程并行处理多个会话

3. **内存优化**：
   - 限制单次处理的消息数量
   - 使用生成器模式处理大型数据集
   - 及时释放不再需要的内存

## 示例输出

```
============================================================
分析会话: 项目组
日期范围: 2026-04-03 至 2026-04-03
时间段: 09:00 至 18:00
============================================================

📊 聊天摘要:
本次聊天共有 120 条消息。 主要讨论了：项目进度、下周计划、技术方案 等内容

🔍 关键事件:
1. [2026-04-03 09:15:32] 讨论了项目的当前进度和遇到的问题
2. [2026-04-03 10:30:15] 确定了下周的工作计划和任务分配
3. [2026-04-03 14:20:45] 讨论了新功能的技术实现方案

✅ 待办事项:
1. [2026-04-03 09:20:15] 完成用户界面设计
2. [2026-04-03 10:35:20] 编写API文档
3. [2026-04-03 14:25:30] 测试新功能

⏰ 截止日期:
1. [2026-04-03 10:40:10] 界面设计需要在周五前完成 (截止: 周五)
2. [2026-04-03 14:30:20] API文档必须在下周一生成 (截止: 下周一)

============================================================
JSON结果:
{
  "summary": "本次聊天共有 120 条消息。 主要讨论了：项目进度、下周计划、技术方案 等内容",
  "key_events": [
    {
      "timestamp": "2026-04-03 09:15:32",
      "content": "讨论了项目的当前进度和遇到的问题",
      "event_type": "讨论"
    },
    ...
  ],
  "todos": [
    {
      "timestamp": "2026-04-03 09:20:15",
      "content": "完成用户界面设计",
      "status": "pending"
    },
    ...
  ],
  "ddls": [
    {
      "timestamp": "2026-04-03 10:40:10",
      "content": "界面设计需要在周五前完成",
      "deadline": "周五"
    },
    ...
  ]
}
```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

MIT License
