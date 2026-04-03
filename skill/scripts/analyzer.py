import re
from datetime import datetime

class ChatAnalyzer:
    def __init__(self):
        # Todo相关关键词（使用简单字符串而非正则表达式，提高性能）
        self.todo_keywords = [
            '需要', '要做', '必须', '应该',
            '待办', 'todo', 'TODO', '待办事项',
            '任务', '安排', '计划', '准备',
            '记得', '别忘了', '提醒', '务必',
            '应该', '应当', '需要做', '要完成',
            '要处理', '要解决', '要跟进', '要落实',
            '待处理', '待解决', '待跟进', '待落实'
        ]
        
        # DDL相关关键词
        self.ddl_keywords = [
            '截止', 'deadline', 'DEADLINE', '截止日期',
            '截止时间', '最后期限', 'deadline', 'DEADLINE',
            '之前', '以内', '之内', '完成', '到期',
            '今天', '明天', '后天', '本周', '下周',
            '本月', '下月', '今年', '明年',
            '月', '日', '年', '号', '时', '分'
        ]
        
        # 关键事件关键词
        self.event_keywords = [
            '会议', '讨论', '聚会', '活动',
            '项目', '方案', '计划', '安排',
            '问题', '解决', '进展', '结果',
            '决定', '确定', '同意', '反对',
            '通知', '提醒', '更新', '变化',
            '发布', '上线', '启动', '结束',
            '开始', '完成', '成功', '失败',
            '合作', '协作', '沟通', '交流',
            '汇报', '总结', '分析', '评估'
        ]
        
        # 日期正则表达式（只在需要时使用）
        self.date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}/\d{1,2}/\d{1,2}',
            r'\d{1,2}月\d{1,2}日',
            r'\d{1,2}/\d{1,2}'
        ]
    
    def analyze_chat(self, messages):
        """分析聊天记录"""
        if not messages:
            return {
                "summary": "暂无聊天记录",
                "key_events": [],
                "todos": [],
                "ddls": []
            }
        
        # 限制消息数量，避免处理过多数据
        max_messages = 5000
        if len(messages) > max_messages:
            messages = messages[:max_messages]
        
        # 按时间排序（从早到晚）
        sorted_messages = sorted(messages, key=lambda x: x['timestamp'])
        
        # 分析各部分（使用批处理提高性能）
        summary = self._generate_summary(sorted_messages)
        key_events = self._extract_key_events(sorted_messages)
        todos = self._extract_todos(sorted_messages)
        ddls = self._extract_ddls(sorted_messages)
        
        return {
            "summary": summary,
            "key_events": key_events,
            "todos": todos,
            "ddls": ddls
        }
    
    def _generate_summary(self, messages):
        """生成聊天摘要"""
        if not messages:
            return "暂无聊天记录"
        
        # 统计消息数量
        total_messages = len(messages)
        
        # 提取关键内容（使用集合去重，提高效率）
        key_contents = set()
        for message in messages:
            content = message['content']
            if len(content) > 10:
                # 快速检查是否包含关键事件关键词
                if any(keyword in content for keyword in self.event_keywords):
                    # 限制内容长度，避免摘要过长
                    key_contents.add(content[:100])
        
        # 转换为列表并限制数量
        key_contents_list = list(key_contents)[:3]
        
        # 生成摘要
        summary = f"本次聊天共有 {total_messages} 条消息。"
        if key_contents_list:
            summary += " 主要讨论了："
            summary += "、".join(key_contents_list)
            if len(key_contents) > 3:
                summary += " 等内容"
        else:
            summary += " 未发现明显的关键讨论内容"
        
        return summary
    
    def _extract_key_events(self, messages):
        """提取关键事件"""
        events = []
        # 使用集合去重，避免重复事件
        seen_events = set()
        
        for message in messages:
            content = message['content']
            timestamp = message['timestamp']
            
            # 快速检查是否包含关键事件关键词
            for keyword in self.event_keywords:
                if keyword in content:
                    # 生成事件哈希，避免重复
                    event_hash = f"{timestamp}_{keyword}_{content[:50]}"
                    if event_hash not in seen_events:
                        seen_events.add(event_hash)
                        events.append({
                            "timestamp": timestamp,
                            "content": content,
                            "event_type": keyword
                        })
                        # 达到上限，提前返回
                        if len(events) >= 10:
                            return events
                    break
        
        return events[:10]  # 最多返回10个关键事件
    
    def _extract_todos(self, messages):
        """提取Todo待办事项"""
        todos = []
        # 使用集合去重，避免重复待办事项
        seen_todos = set()
        
        for message in messages:
            content = message['content']
            timestamp = message['timestamp']
            
            # 快速检查是否包含待办关键词
            for keyword in self.todo_keywords:
                if keyword in content:
                    # 生成待办哈希，避免重复
                    todo_hash = f"{timestamp}_{content[:100]}"
                    if todo_hash not in seen_todos:
                        seen_todos.add(todo_hash)
                        todos.append({
                            "timestamp": timestamp,
                            "content": content,
                            "status": "pending"
                        })
                        # 达到上限，提前返回
                        if len(todos) >= 15:
                            return todos
                    break
        
        return todos[:15]  # 最多返回15个待办事项
    
    def _extract_ddls(self, messages):
        """提取DDL截止日期"""
        ddls = []
        # 使用集合去重，避免重复DDL
        seen_ddls = set()
        
        for message in messages:
            content = message['content']
            timestamp = message['timestamp']
            
            # 快速检查是否包含DDL关键词
            for keyword in self.ddl_keywords:
                if keyword in content:
                    # 尝试提取日期
                    deadline = self._extract_deadline(content)
                    # 生成DDL哈希，避免重复
                    ddl_hash = f"{timestamp}_{deadline}_{content[:100]}"
                    if ddl_hash not in seen_ddls:
                        seen_ddls.add(ddl_hash)
                        ddls.append({
                            "timestamp": timestamp,
                            "content": content,
                            "deadline": deadline
                        })
                        # 达到上限，提前返回
                        if len(ddls) >= 10:
                            return ddls
                    break
        
        return ddls[:10]  # 最多返回10个DDL
    
    def _extract_deadline(self, content):
        """从内容中提取截止日期"""
        # 首先检查简单的时间关键词
        time_keywords = ['今天', '明天', '后天', '本周', '下周', '本月', '下月']
        for keyword in time_keywords:
            if keyword in content:
                return keyword
        
        # 然后使用正则表达式匹配日期格式
        for pattern in self.date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return "未明确"
