# WeChat Todo Skill 故障排除指南

## 常见问题及解决方案

### 1. 数据库连接失败

**症状**：系统无法连接到微信数据库

**可能原因**：
- 微信数据库未解密
- 数据库路径不正确
- 微信版本过低
- 权限不足

**解决方案**：
- 确保微信版本为 4.x
- 按照 SKILL.md 中的步骤执行 Ad-hoc 签名（macOS）
- 手动指定数据库路径：`python skill/main.py --db-dir "/path/to/decrypted"`
- 以管理员权限运行 OpenClaw（Windows）

### 2. 解密失败

**症状**：wechat-decrypt 工具无法解密数据库

**可能原因**：
- 微信未运行
- 微信版本过低
- 权限不足
- 微信进程被保护

**解决方案**：
- 确保微信正在运行
- 确保微信版本为 4.x
- 以管理员权限运行 OpenClaw
- 重新执行 Ad-hoc 签名（macOS）
- 尝试手动运行 wechat-decrypt 工具：`python wechat-decrypt/main.py decrypt`

### 3. 会话未找到

**症状**：系统无法找到指定的会话

**可能原因**：
- 会话名称输入错误
- 数据库中不存在该会话
- 数据库未正确解密

**解决方案**：
- 检查会话名称是否正确
- 尝试使用不同的关键词搜索
- 确保数据库已正确解密
- 尝试使用微信号或备注名搜索

### 4. 分析速度慢

**症状**：分析大型聊天记录时速度缓慢

**可能原因**：
- 聊天记录数量过多
- 系统资源不足
- 数据库查询效率低

**解决方案**：
- 限制分析的时间范围
- 只分析最近的消息
- 关闭其他占用系统资源的应用
- 确保使用了最新版本的 wechat-decrypt 工具

### 5. 提取的待办事项不准确

**症状**：系统提取的待办事项与实际不符

**可能原因**：
- 关键词匹配不够准确
- 消息内容复杂
- 语境理解不足

**解决方案**：
- 使用更具体的关键词
- 手动指定需要分析的消息范围
- 提供更多上下文信息

### 6. 权限错误

**症状**：系统提示权限不足

**可能原因**：
- 未以管理员权限运行
- 文件系统权限限制
- 系统安全设置

**解决方案**：
- 以管理员权限运行 OpenClaw
- 确保用户有权访问微信数据目录
- 检查系统安全设置

### 7. wechat-decrypt 工具安装失败

**症状**：无法安装或运行 wechat-decrypt 工具

**可能原因**：
- 网络连接问题
- 依赖包安装失败
- Git 未安装

**解决方案**：
- 检查网络连接
- 手动安装依赖包：`pip install -r wechat-decrypt/requirements.txt`
- 确保 Git 已安装
- 手动克隆 wechat-decrypt 仓库：`git clone https://github.com/ylytdeng/wechat-decrypt.git`

### 8. 微信数据目录未找到

**症状**：系统无法找到微信数据目录

**可能原因**：
- 微信安装在非默认位置
- 微信版本不同
- 系统路径变更

**解决方案**：
- **Windows**：手动指定微信数据目录，微信 4.x 版本路径通常为：`C:\Users\用户名\AppData\Roaming\Tencent\xwechat\radium\users\*\`
- **macOS**：手动指定微信数据目录，路径通常为：`~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/*/db_storage`
- 检查微信设置中的文件管理路径
- 尝试使用文件管理器搜索数据目录

## 高级故障排除

### 手动解密数据库

如果自动解密失败，可以尝试手动解密：

1. 克隆 wechat-decrypt 工具：
   ```bash
   git clone https://github.com/ylytdeng/wechat-decrypt.git
   cd wechat-decrypt
   pip install -r requirements.txt
   ```

2. 提取密钥：
   ```bash
   # Windows
   python find_all_keys.py
   
   # macOS
   sudo ./find_all_keys_macos
   ```

3. 解密数据库：
   ```bash
   python main.py decrypt --db-dir "/path/to/db_storage" --decrypted-dir "decrypted"
   ```

4. 将解密后的 `decrypted` 目录复制到技能目录

### 手动分析聊天记录

如果自动分析失败，可以尝试手动分析：

1. 确保数据库已解密
2. 运行分析脚本：
   ```bash
   python skill/main.py --db-dir "/path/to/decrypted" --session "会话名称" --date-range "2026-01-01,2026-01-31"
   ```

### 日志排查

如果遇到问题，可以查看系统日志：

1. 运行技能时添加 `--verbose` 参数：
   ```bash
   python skill/main.py --verbose --session "会话名称"
   ```

2. 检查 wechat-decrypt 工具的日志：
   ```bash
   cat wechat-decrypt/decrypt.log
   ```

## 联系支持

如果以上解决方案都无法解决问题，可以：

1. 查看 wechat-decrypt 项目的 GitHub  Issues：https://github.com/ylytdeng/wechat-decrypt/issues
2. 查看 OpenClaw 官方文档：https://openclaw.io/docs
3. 联系 OpenClaw 社区寻求帮助