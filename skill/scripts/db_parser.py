import os
import platform
import sqlite3
import json
from datetime import datetime

class WeChatDBParser:
    def __init__(self, db_dir=None):
        self.db_dir = db_dir
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.message_db = None
        self.contact_db = None
        self._session_cache = {}
        self._message_cache = {}
        self._contact_cache = {}
    
    def set_db_dir(self, db_dir):
        self.db_dir = db_dir
    
    def connect(self):
        if not self.db_dir:
            return False, "数据库目录未设置"
        
        # 尝试不同的数据库路径结构
        possible_message_paths = [
            os.path.join(self.db_dir, "message", "Msg.db"),
            os.path.join(self.db_dir, "Msg.db"),
            os.path.join(self.db_dir, "message_*.db")
        ]
        
        possible_contact_paths = [
            os.path.join(self.db_dir, "contact", "Contact.db"),
            os.path.join(self.db_dir, "Contact.db")
        ]
        
        # 查找消息数据库
        message_db_path = None
        import glob
        for path_pattern in possible_message_paths:
            if "*" in path_pattern:
                # 使用glob匹配
                matches = glob.glob(path_pattern)
                if matches:
                    message_db_path = matches[0]
                    break
            else:
                if os.path.exists(path_pattern):
                    message_db_path = path_pattern
                    break
        
        if not message_db_path:
            return False, f"消息数据库不存在，尝试了以下路径: {', '.join(possible_message_paths)}"
        
        # 查找联系人数据库
        contact_db_path = None
        for path in possible_contact_paths:
            if os.path.exists(path):
                contact_db_path = path
                break
        
        if not contact_db_path:
            return False, f"联系人数据库不存在，尝试了以下路径: {', '.join(possible_contact_paths)}"
        
        try:
            self.message_db = sqlite3.connect(message_db_path)
            self.contact_db = sqlite3.connect(contact_db_path)
            return True, f"数据库连接成功，消息数据库: {message_db_path}, 联系人数据库: {contact_db_path}"
        except Exception as e:
            return False, f"数据库连接失败: {str(e)}"
    
    def close(self):
        if self.message_db:
            self.message_db.close()
        if self.contact_db:
            self.contact_db.close()
    
    def get_sessions(self):
        if not self.message_db:
            return False, "数据库未连接", []
        
        # 检查缓存
        if "all" in self._session_cache:
            return True, "获取会话列表成功", self._session_cache["all"]
        
        try:
            cursor = self.message_db.cursor()
            # 优化SQL查询，只选择需要的列
            cursor.execute("""
                SELECT 
                    ChatId, 
                    COUNT(*) as message_count,
                    MAX(CreateTime) as last_message_time
                FROM Message
                GROUP BY ChatId
                ORDER BY last_message_time DESC
                LIMIT 1000
            """)
            sessions = []
            for row in cursor.fetchall():
                chat_id, message_count, last_message_time = row
                sessions.append({
                    "chat_id": chat_id,
                    "message_count": message_count,
                    "last_message_time": self._format_timestamp(last_message_time)
                })
            
            # 缓存结果
            self._session_cache["all"] = sessions
            return True, "获取会话列表成功", sessions
        except Exception as e:
            return False, f"获取会话列表失败: {str(e)}", []
    
    def get_session_name(self, chat_id):
        if not self.contact_db:
            return chat_id
        
        # 检查缓存
        if chat_id in self._contact_cache:
            return self._contact_cache[chat_id]
        
        try:
            cursor = self.contact_db.cursor()
            cursor.execute("SELECT NickName FROM Contact WHERE UserName=?", (chat_id,))
            result = cursor.fetchone()
            name = result[0] if result else chat_id
            
            # 缓存结果
            self._contact_cache[chat_id] = name
            return name
        except Exception:
            return chat_id
    
    def get_messages(self, chat_id, start_time=None, end_time=None, limit=1000):
        if not self.message_db:
            return False, "数据库未连接", []
        
        # 生成缓存键
        cache_key = f"{chat_id}_{start_time}_{end_time}_{limit}"
        # 检查缓存
        if cache_key in self._message_cache:
            return True, "获取消息成功", self._message_cache[cache_key]
        
        try:
            cursor = self.message_db.cursor()
            # 优化SQL查询，确保使用索引
            query = "SELECT CreateTime, IsSender, Content FROM Message WHERE ChatId=?"
            params = [chat_id]
            
            if start_time:
                query += " AND CreateTime >= ?"
                params.append(start_time)
            if end_time:
                query += " AND CreateTime <= ?"
                params.append(end_time)
            
            # 限制返回的消息数量，避免一次性加载太多数据
            safe_limit = min(limit, 5000)  # 最多返回5000条消息
            query += " ORDER BY CreateTime DESC LIMIT ?"
            params.append(safe_limit)
            
            # 执行查询
            cursor.execute(query, params)
            
            # 批量处理结果
            messages = []
            for row in cursor.fetchall():
                create_time, is_sender, content = row
                messages.append({
                    "timestamp": self._format_timestamp(create_time),
                    "is_sender": bool(is_sender),
                    "content": content
                })
            
            # 缓存结果
            self._message_cache[cache_key] = messages
            return True, "获取消息成功", messages
        except Exception as e:
            return False, f"获取消息失败: {str(e)}", []
    
    def _format_timestamp(self, timestamp):
        try:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "未知时间"
    
    def search_sessions(self, keyword):
        if not self.contact_db:
            return False, "数据库未连接", []
        
        # 检查缓存
        if keyword in self._session_cache:
            return True, "搜索会话成功", self._session_cache[keyword]
        
        try:
            cursor = self.contact_db.cursor()
            # 优化SQL查询，限制返回数量
            cursor.execute("""
                SELECT UserName, NickName 
                FROM Contact 
                WHERE NickName LIKE ? OR UserName LIKE ?
                LIMIT 50
            """, (f"%{keyword}%", f"%{keyword}%"))
            
            sessions = []
            for row in cursor.fetchall():
                user_name, nick_name = row
                sessions.append({
                    "chat_id": user_name,
                    "name": nick_name or user_name
                })
            
            # 缓存结果
            self._session_cache[keyword] = sessions
            return True, "搜索会话成功", sessions
        except Exception as e:
            return False, f"搜索会话失败: {str(e)}", []
