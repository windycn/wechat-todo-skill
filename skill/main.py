import os
import sys
import argparse
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.db_parser import WeChatDBParser
from scripts.session_manager import SessionManager
from scripts.config import DateRangeConfig
from scripts.analyzer import ChatAnalyzer
from scripts.decryptor import WeChatDecryptor

class WeChatTodoSkill:
    def __init__(self):
        self.db_parser = WeChatDBParser()
        self.session_manager = SessionManager(self.db_parser)
        self.date_config = DateRangeConfig()
        self.analyzer = ChatAnalyzer()
        self.decryptor = WeChatDecryptor()
        self._last_analysis_time = {}  # 存储每个会话的最后分析时间
    
    def run(self):
        """运行主流程"""
        # 解析命令行参数
        args = self._parse_args()
        
        # 连接数据库
        success, message = self._connect_db(args.db_dir)
        if not success:
            print(f"❌ {message}")
            return
        
        try:
            # 选择会话
            selected_sessions = self._select_sessions(args.session)
            if not selected_sessions:
                print("❌ 未选择会话，退出")
                return
            
            # 选择日期范围
            start_time, end_time = self._select_date_range(args.date_range)
            if start_time is None:
                print("❌ 日期范围选择失败，退出")
                return
            
            # 选择时间段
            start_hour, end_hour = self._select_time_range(args.time_range)
            
            # 分析聊天记录
            self._analyze_chats(selected_sessions, start_time, end_time, start_hour, end_hour)
        finally:
            # 关闭数据库连接
            self.db_parser.close()
    
    def _parse_args(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser(
            description="微信聊天记录分析器 - OpenClaw Skill",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  python main.py --session "项目组"
  python main.py --session "张三" --date-range today
  python main.py --session "李四" --date-range "2026-01-01,2026-01-31" --time-range "09:00,18:00"
            """
        )
        
        parser.add_argument("--db-dir", help="微信数据库目录")
        parser.add_argument("--session", help="会话名称或关键词")
        parser.add_argument("--date-range", default="today", help="日期范围: today/yesterday/this_week 或 2026-01-01,2026-01-31")
        parser.add_argument("--time-range", help="时间段: 09:00,18:00")
        
        return parser.parse_args()
    
    def _connect_db(self, db_dir):
        """连接数据库"""
        # 自动查找数据库目录
        if not db_dir:
            print("🔍 自动查找微信数据库...")
            db_dir = self._find_db_dir()
        
        # 尝试自动解密
        if not db_dir or not self._is_valid_db_dir(db_dir):
            print("🔑 尝试自动解密微信数据库...")
            decrypted_dir = os.path.join(os.getcwd(), "decrypted")
            success, message = self.decryptor.auto_decrypt(decrypted_dir)
            if success:
                print(f"✅ {message}")
                db_dir = decrypted_dir
            else:
                print(f"⚠️ {message}")
                print("\n📋 数据库准备步骤:")
                print("\n**权限要求**：")
                print("- **Windows 用户**：请确保以管理员权限启动支持 skills 的 agent 程序，否则可能无法从微信内存中提取密钥。")
                print("- **macOS 用户**：由于系统安全限制（SIP），无法像 Windows 那样直接从内存提取密钥。需要手动准备解密数据，具体步骤如下：")
                print("  * **步骤1**: 定位微信数据目录")
                print("    - 打开 Finder，按 `Cmd+Shift+G` 输入路径：`~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/`")
                print("    - 进入 `4.0b*/` 目录（`*` 代表一串随机字符），找到 `db_storage` 文件夹")
                print("  * **步骤2**: 使用第三方工具提取并解密数据库")
                print("    - 推荐使用开源工具 `https://github.com/ylytdeng/wechat-decrypt`  或其他类似的微信数据库解密工具")
                print("    - 按照工具说明提取并解密微信数据库文件")
                print("  * **步骤3**: 将解密后的数据复制到用户对话路径下")
                print("    - 将解密工具生成的 `decrypted` 目录完整复制到当前用户对话路径下")
                print("    - 确保目录结构为：`{用户对话路径}/decrypted/message_*.db`")
                print("\n💡 提示：如果电脑端微信缺少数据，请使用微信的手机聊天记录导出功能导出到电脑微信。")
                return False, "未找到微信数据库目录"
        
        # 连接数据库
        self.db_parser.set_db_dir(db_dir)
        success, message = self.db_parser.connect()
        
        # 如果连接失败，再次尝试自动解密
        if not success:
            print(f"⚠️ {message}")
            print("🔑 再次尝试自动解密微信数据库...")
            decrypted_dir = os.path.join(os.getcwd(), "decrypted")
            decrypt_success, decrypt_message = self.decryptor.auto_decrypt(decrypted_dir)
            if decrypt_success:
                print(f"✅ {decrypt_message}")
                self.db_parser.set_db_dir(decrypted_dir)
                success, message = self.db_parser.connect()
            else:
                print("\n📋 数据库准备步骤:")
                print("\n**权限要求**：")
                print("- **Windows 用户**：请确保以管理员权限启动支持 skills 的 agent 程序，否则可能无法从微信内存中提取密钥。")
                print("- **macOS 用户**：由于系统安全限制（SIP），无法像 Windows 那样直接从内存提取密钥。需要手动准备解密数据，具体步骤如下：")
                print("  * **步骤1**: 定位微信数据目录")
                print("    - 打开 Finder，按 `Cmd+Shift+G` 输入路径：`~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/`")
                print("    - 进入 `4.0b*/` 目录（`*` 代表一串随机字符），找到 `db_storage` 文件夹")
                print("  * **步骤2**: 使用第三方工具提取并解密数据库")
                print("    - 推荐使用开源工具 `https://github.com/ylytdeng/wechat-decrypt`  或其他类似的微信数据库解密工具")
                print("    - 按照工具说明提取并解密微信数据库文件")
                print("  * **步骤3**: 将解密后的数据复制到用户对话路径下")
                print("    - 将解密工具生成的 `decrypted` 目录完整复制到当前用户对话路径下")
                print("    - 确保目录结构为：`{用户对话路径}/decrypted/message_*.db`")
                print("\n💡 提示：如果电脑端微信缺少数据，请使用微信的手机聊天记录导出功能导出到电脑微信。")
        
        return success, message
    
    def _is_valid_db_dir(self, db_dir):
        """检查数据库目录是否有效"""
        if not db_dir or not os.path.exists(db_dir):
            return False
        
        # 检查是否包含必要的数据库文件
        message_db = os.path.join(db_dir, "message", "Msg.db")
        contact_db = os.path.join(db_dir, "contact", "Contact.db")
        
        return os.path.exists(message_db) and os.path.exists(contact_db)
    
    def _find_db_dir(self):
        """自动查找数据库目录"""
        # 尝试多个可能的位置
        possible_paths = [
            # 当前目录下的 decrypted 文件夹
            os.path.join(os.getcwd(), "decrypted"),
            # 用户主目录下的 WeChat 相关目录
            os.path.join(os.path.expanduser("~"), "WeChat", "decrypted"),
            # Windows 微信默认路径
            os.path.join(os.environ.get("APPDATA", ""), "Tencent", "WeChat", "WeChat Files"),
            # macOS 微信默认路径
            os.path.join(os.path.expanduser("~"), "Library", "Containers", "com.tencent.xinWeChat", "Data", "Library", "Application Support", "WeChat")
        ]
        
        for path in possible_paths:
            if self._is_valid_db_dir(path):
                print(f"✅ 找到有效数据库目录: {path}")
                return path
        
        return None
    
    def _select_sessions(self, session_keyword):
        """选择会话"""
        if not session_keyword:
            # 显示所有会话供用户选择
            success, message, sessions = self.session_manager.get_all_sessions()
            if not success:
                print(f"❌ {message}")
                return []
            
            print("📋 可用会话列表:")
            for i, session in enumerate(sessions[:50]):  # 最多显示50个会话
                print(f"{i+1}. {session['name']} ({session['message_count']}条消息)")
            
            choice = input("请输入要分析的会话序号（多个序号用逗号分隔）: ")
            choices = [int(c.strip())-1 for c in choice.split(",") if c.strip().isdigit()]
            return [sessions[i] for i in choices if 0 <= i < len(sessions)]
        else:
            # 搜索会话
            success, message, sessions = self.session_manager.search_sessions_by_name(session_keyword)
            if not success:
                print(f"❌ {message}")
                return []
            
            if not sessions:
                print(f"❌ 未找到匹配的会话: {session_keyword}")
                return []
            
            # 显示匹配结果
            print("📋 匹配的会话:")
            for i, session in enumerate(sessions[:10]):  # 最多显示10个匹配结果
                print(f"{i+1}. {session['name']}")
            
            if len(sessions) == 1:
                # 只有一个匹配结果，直接使用
                return [sessions[0]]
            else:
                # 多个匹配结果，让用户选择
                choice = input("请输入要分析的会话序号（多个序号用逗号分隔）: ")
                choices = [int(c.strip())-1 for c in choice.split(",") if c.strip().isdigit()]
                return [sessions[i] for i in choices if 0 <= i < len(sessions)]
    
    def _select_date_range(self, date_range):
        """选择日期范围"""
        if date_range == "today":
            return self.date_config.get_today_range()
        elif date_range == "yesterday":
            return self.date_config.get_yesterday_range()
        elif date_range == "this_week":
            return self.date_config.get_this_week_range()
        else:
            # 自定义日期范围
            try:
                start_date, end_date = date_range.split(",")
                return self.date_config.get_date_range(start_date, end_date)
            except Exception:
                print(f"❌ 日期范围格式错误: {date_range}")
                return None, None
    
    def _select_time_range(self, time_range):
        """选择时间段"""
        if not time_range:
            return None, None
        
        try:
            start_time, end_time = time_range.split(",")
            return self.date_config.get_time_range(start_time, end_time)
        except Exception:
            print(f"❌ 时间段格式错误: {time_range}")
            return None, None
    
    def _analyze_chats(self, sessions, start_time, end_time, start_hour, end_hour):
        """分析聊天记录"""
        for session in sessions:
            print(f"\n{'='*60}")
            print(f"分析会话: {session['name']}")
            print(f"日期范围: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')} 至 {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')}")
            if start_hour and end_hour:
                print(f"时间段: {start_hour.strftime('%H:%M')} 至 {end_hour.strftime('%H:%M')}")
            print(f"{'='*60}")
            
            # 增量分析：获取最后分析时间
            chat_id = session['chat_id']
            last_time = self._last_analysis_time.get(chat_id, start_time)
            
            # 获取消息（只获取新消息）
            success, message, messages = self.db_parser.get_messages(
                chat_id, 
                last_time, 
                end_time,
                limit=5000
            )
            
            if not success:
                print(f"❌ {message}")
                continue
            
            if not messages:
                print("❌ 未找到消息记录")
                continue
            
            # 按时间段筛选
            if start_hour and end_hour:
                messages = self.date_config.filter_messages_by_time(messages, start_hour, end_hour)
            
            # 分析消息
            analysis_result = self.analyzer.analyze_chat(messages)
            
            # 输出结果
            self._print_analysis_result(analysis_result)
            
            # 更新最后分析时间
            self._last_analysis_time[chat_id] = end_time
    
    def _print_analysis_result(self, result):
        """打印分析结果"""
        print(f"\n📊 聊天摘要:")
        print(result['summary'])
        
        if result['key_events']:
            print(f"\n🔍 关键事件:")
            for i, event in enumerate(result['key_events']):
                print(f"{i+1}. [{event['timestamp']}] {event['content']}")
        
        if result['todos']:
            print(f"\n✅ 待办事项:")
            for i, todo in enumerate(result['todos']):
                print(f"{i+1}. [{todo['timestamp']}] {todo['content']}")
        
        if result['ddls']:
            print(f"\n⏰ 截止日期:")
            for i, ddl in enumerate(result['ddls']):
                print(f"{i+1}. [{ddl['timestamp']}] {ddl['content']} (截止: {ddl['deadline']})")
        
        # 输出JSON格式结果，供OpenClaw使用
        print(f"\n{'='*60}")
        print("JSON结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    skill = WeChatTodoSkill()
    skill.run()
