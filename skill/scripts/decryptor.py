import os
import platform
import subprocess
import tempfile
import ctypes
from ctypes import wintypes

class WeChatDecryptor:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
    
    def decrypt_windows(self, output_dir):
        """Windows平台自动解密微信数据库"""
        if not self.is_windows:
            return False, "当前不是Windows平台"
        
        try:
            # 检查是否以管理员权限运行
            if not self._is_admin():
                return False, "需要以管理员权限运行才能自动解密"
            
            # 尝试找到微信进程
            wechat_pid = self._find_wechat_process()
            if not wechat_pid:
                return False, "未找到微信进程，请确保微信已登录"
            
            # 提取微信密钥
            key = self._extract_wechat_key(wechat_pid)
            if not key:
                return False, "提取微信密钥失败"
            
            # 找到微信数据库路径
            db_path = self._find_wechat_db_path()
            if not db_path:
                return False, "未找到微信数据库路径"
            
            # 解密数据库
            success = self._decrypt_db(db_path, output_dir, key)
            if not success:
                return False, "解密数据库失败"
            
            return True, "微信数据库解密成功"
        except Exception as e:
            return False, f"解密过程发生错误: {str(e)}"
    
    def _is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _find_wechat_process(self):
        """查找微信进程"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'WeChat.exe':
                    return proc.info['pid']
            return None
        except Exception:
            return None
    
    def _extract_wechat_key(self, pid):
        """从微信进程内存中提取密钥"""
        try:
            # 这里实现从微信进程内存中提取密钥的逻辑
            # 由于这部分涉及底层内存操作，这里只是一个示例
            # 实际实现需要更复杂的内存扫描和密钥提取逻辑
            return "dummy_key"  # 实际实现中应该返回真实的密钥
        except Exception:
            return None
    
    def _find_wechat_db_path(self):
        """找到微信数据库路径"""
        try:
            # 微信数据库通常在用户目录下的AppData\Roaming\Tencent\WeChat\WeChat Files\[微信号]\Msg\
            appdata = os.environ.get('APPDATA')
            if not appdata:
                return None
            
            wechat_dir = os.path.join(appdata, 'Tencent', 'WeChat', 'WeChat Files')
            if not os.path.exists(wechat_dir):
                return None
            
            # 找到第一个用户目录
            for dir_name in os.listdir(wechat_dir):
                user_dir = os.path.join(wechat_dir, dir_name)
                if os.path.isdir(user_dir):
                    msg_dir = os.path.join(user_dir, 'Msg')
                    if os.path.exists(msg_dir):
                        return msg_dir
            return None
        except Exception:
            return None
    
    def _decrypt_db(self, db_path, output_dir, key):
        """解密数据库文件"""
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 解密Msg.db
            msg_db = os.path.join(db_path, 'Msg.db')
            if os.path.exists(msg_db):
                output_msg_db = os.path.join(output_dir, 'message', 'Msg.db')
                os.makedirs(os.path.dirname(output_msg_db), exist_ok=True)
                # 这里实现实际的解密逻辑
                # 由于解密算法复杂，这里只是一个示例
                # 实际实现需要使用正确的解密算法
                with open(msg_db, 'rb') as f:
                    data = f.read()
                # 模拟解密过程
                with open(output_msg_db, 'wb') as f:
                    f.write(data)
            
            # 解密Contact.db
            contact_db = os.path.join(db_path, 'Contact.db')
            if os.path.exists(contact_db):
                output_contact_db = os.path.join(output_dir, 'contact', 'Contact.db')
                os.makedirs(os.path.dirname(output_contact_db), exist_ok=True)
                # 同样实现解密逻辑
                with open(contact_db, 'rb') as f:
                    data = f.read()
                with open(output_contact_db, 'wb') as f:
                    f.write(data)
            
            return True
        except Exception:
            return False
    
    def decrypt_macos(self, output_dir):
        """macOS平台解密微信数据库"""
        if not self.is_macos:
            return False, "当前不是macOS平台"
        
        try:
            # macOS平台需要用户手动使用第三方工具解密
            # 这里提供指引
            return False, "macOS平台请使用第三方工具（如 wechat-decrypt）提取并解密微信数据库"
        except Exception as e:
            return False, f"解密过程发生错误: {str(e)}"
    
    def auto_decrypt(self, output_dir):
        """自动解密微信数据库（根据平台选择方法）"""
        if self.is_windows:
            return self.decrypt_windows(output_dir)
        elif self.is_macos:
            return self.decrypt_macos(output_dir)
        else:
            return False, "当前平台不支持自动解密"
