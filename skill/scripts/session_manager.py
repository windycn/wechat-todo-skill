class SessionManager:
    def __init__(self, db_parser):
        self.db_parser = db_parser
    
    def get_all_sessions(self):
        success, message, sessions = self.db_parser.get_sessions()
        if not success:
            return success, message, []
        
        # 为每个会话添加名称
        for session in sessions:
            session['name'] = self.db_parser.get_session_name(session['chat_id'])
        
        return success, message, sessions
    
    def search_sessions_by_name(self, name):
        success, message, sessions = self.db_parser.search_sessions(name)
        if not success:
            return success, message, []
        
        # 按匹配程度排序
        sessions.sort(key=lambda x: self._calculate_match_score(x['name'], name), reverse=True)
        
        return success, message, sessions
    
    def get_session_by_id(self, chat_id):
        success, message, sessions = self.get_all_sessions()
        if not success:
            return None
        
        for session in sessions:
            if session['chat_id'] == chat_id:
                return session
        return None
    
    def get_sessions_by_ids(self, chat_ids):
        success, message, all_sessions = self.get_all_sessions()
        if not success:
            return []
        
        return [session for session in all_sessions if session['chat_id'] in chat_ids]
    
    def _calculate_match_score(self, session_name, query):
        score = 0
        query_lower = query.lower()
        session_name_lower = session_name.lower()
        
        # 完全匹配
        if session_name_lower == query_lower:
            score += 100
        # 前缀匹配
        elif session_name_lower.startswith(query_lower):
            score += 80
        # 包含匹配
        elif query_lower in session_name_lower:
            score += 60
        # 部分匹配
        else:
            # 计算共同字符数
            common_chars = set(query_lower) & set(session_name_lower)
            score += len(common_chars) * 10
        
        return score
    
    def filter_sessions(self, sessions, filter_type=None):
        """
        过滤会话类型
        filter_type: 'group' - 群聊, 'private' - 私聊
        """
        if not filter_type:
            return sessions
        
        filtered_sessions = []
        for session in sessions:
            chat_id = session['chat_id']
            if filter_type == 'group' and chat_id.startswith('chatroom'):
                filtered_sessions.append(session)
            elif filter_type == 'private' and not chat_id.startswith('chatroom'):
                filtered_sessions.append(session)
        
        return filtered_sessions
