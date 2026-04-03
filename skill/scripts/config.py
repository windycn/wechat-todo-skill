from datetime import datetime, timedelta
import pytz

class DateRangeConfig:
    def __init__(self):
        self.timezone = pytz.timezone('Asia/Shanghai')
    
    def get_today_range(self):
        """获取今天的时间范围"""
        today = datetime.now(self.timezone).date()
        start_time = self.timezone.localize(datetime.combine(today, datetime.min.time()))
        end_time = self.timezone.localize(datetime.combine(today, datetime.max.time()))
        return int(start_time.timestamp()), int(end_time.timestamp())
    
    def get_yesterday_range(self):
        """获取昨天的时间范围"""
        yesterday = datetime.now(self.timezone).date() - timedelta(days=1)
        start_time = self.timezone.localize(datetime.combine(yesterday, datetime.min.time()))
        end_time = self.timezone.localize(datetime.combine(yesterday, datetime.max.time()))
        return int(start_time.timestamp()), int(end_time.timestamp())
    
    def get_this_week_range(self):
        """获取本周的时间范围"""
        today = datetime.now(self.timezone).date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_time = self.timezone.localize(datetime.combine(start_of_week, datetime.min.time()))
        end_time = self.timezone.localize(datetime.combine(end_of_week, datetime.max.time()))
        return int(start_time.timestamp()), int(end_time.timestamp())
    
    def get_date_range(self, start_date, end_date):
        """获取指定日期范围"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            start_time = self.timezone.localize(datetime.combine(start, datetime.min.time()))
            end_time = self.timezone.localize(datetime.combine(end, datetime.max.time()))
            return int(start_time.timestamp()), int(end_time.timestamp())
        except Exception:
            return None, None
    
    def get_time_range(self, start_time_str, end_time_str):
        """获取指定时间段"""
        try:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            return start_time, end_time
        except Exception:
            return None, None
    
    def filter_messages_by_time(self, messages, start_time, end_time):
        """根据时间段筛选消息"""
        if not start_time or not end_time:
            return messages
        
        filtered_messages = []
        for message in messages:
            msg_time = datetime.strptime(message['timestamp'], "%Y-%m-%d %H:%M:%S").time()
            if start_time <= msg_time <= end_time:
                filtered_messages.append(message)
        return filtered_messages
    
    def get_presets(self):
        """获取预设的时间范围"""
        return {
            "today": {
                "name": "今日",
                "description": "今天的聊天记录"
            },
            "yesterday": {
                "name": "昨日",
                "description": "昨天的聊天记录"
            },
            "this_week": {
                "name": "本周",
                "description": "本周的聊天记录"
            }
        }
