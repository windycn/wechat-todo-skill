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
            
            # 检查微信版本
            version_check = self._check_windows_wechat_version()
            if not version_check['success']:
                return False, version_check['message']
            
            # 尝试自动安装和使用 wechat-decrypt 工具
            success, message = self._auto_install_wechat_decrypt()
            if not success:
                return False, message
            
            # 查找微信数据目录
            db_dir = self._find_windows_db_storage()
            if not db_dir:
                return False, "未找到微信数据目录，请手动提供路径"
            
            # 使用 wechat-decrypt 工具解密
            success, message = self._run_wechat_decrypt(db_dir, output_dir)
            if success:
                return True, f"微信数据库解密成功，解密后文件位于: {output_dir}"
            else:
                return False, message
        except Exception as e:
            return False, f"解密过程发生错误: {str(e)}"
    
    def _is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _check_windows_wechat_version(self):
        """检查Windows微信版本"""
        try:
            import os
            import subprocess
            
            # 检查微信是否安装
            wechat_exe = os.path.join(os.environ.get('PROGRAMFILES'), 'Tencent', 'WeChat', 'WeChat.exe')
            if not os.path.exists(wechat_exe):
                # 尝试64位路径
                wechat_exe = os.path.join(os.environ.get('PROGRAMFILES(X86)'), 'Tencent', 'WeChat', 'WeChat.exe')
                if not os.path.exists(wechat_exe):
                    return {
                        'success': False,
                        'message': "未找到微信应用，请先安装微信"
                    }
            
            # 尝试获取微信版本
            result = subprocess.run(
                ["wmic", "datafile", "where", f"name='{wechat_exe}'", "get", "Version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[-1].strip()
                if version:
                    print(f"检测到微信版本: {version}")
                    
                    # 检查是否为 4.x 版本
                    major_version = int(version.split('.')[0])
                    if major_version < 4:
                        return {
                            'success': False,
                            'message': f"微信版本 {version} 过低，需要 4.x 版本以上才能使用此功能"
                        }
            
            return {'success': True, 'message': "微信版本检查通过"}
        except Exception as e:
            return {
                'success': False,
                'message': f"检查微信版本时发生错误: {str(e)}"
            }
    
    def _find_windows_db_storage(self):
        """查找 Windows 微信数据目录"""
        try:
            import os
            import glob
            
            # 微信 4.x 版本数据目录
            appdata = os.environ.get('APPDATA')
            if not appdata:
                return None
            
            # 新路径：C:\Users\用户名\AppData\Roaming\Tencent\xwechat\radium\users\*\
            search_path = os.path.join(appdata, 'Tencent', 'xwechat', 'radium', 'users')
            
            if os.path.exists(search_path):
                # 查找所有用户目录
                user_dirs = glob.glob(os.path.join(search_path, '*'))
                if user_dirs:
                    # 返回第一个找到的用户目录
                    return user_dirs[0]
            
            # 旧路径：C:\Users\用户名\AppData\Roaming\Tencent\WeChat\WeChat Files\*\Msg\
            old_search_path = os.path.join(appdata, 'Tencent', 'WeChat', 'WeChat Files')
            if os.path.exists(old_search_path):
                for dir_name in os.listdir(old_search_path):
                    user_dir = os.path.join(old_search_path, dir_name)
                    if os.path.isdir(user_dir):
                        msg_dir = os.path.join(user_dir, 'Msg')
                        if os.path.exists(msg_dir):
                            return msg_dir
            
            return None
        except Exception:
            return None
    
    def decrypt_macos(self, output_dir):
        """macOS平台解密微信数据库"""
        if not self.is_macos:
            return False, "当前不是macOS平台"
        
        try:
            # 检查微信版本
            version_check = self._check_wechat_version()
            if not version_check['success']:
                return False, version_check['message']
            
            # 尝试自动安装和使用 wechat-decrypt 工具
            success, message = self._auto_install_wechat_decrypt()
            if not success:
                return False, message
            
            # 查找 db_storage 目录
            db_dir = self._find_macos_db_storage()
            if not db_dir:
                return False, "未找到微信 db_storage 目录，请手动提供路径"
            
            # 检查是否需要 Ad-hoc 签名
            sign_check = self._check_wechat_signature()
            if not sign_check['success']:
                return False, sign_check['message']
            
            # 使用 wechat-decrypt 工具解密
            success, message = self._run_wechat_decrypt(db_dir, output_dir)
            if success:
                return True, f"微信数据库解密成功，解密后文件位于: {output_dir}"
            else:
                return False, message
        except Exception as e:
            return False, f"解密过程发生错误: {str(e)}"
    
    def _check_wechat_version(self):
        """检查微信版本"""
        try:
            import os
            import subprocess
            
            # 检查微信是否安装
            wechat_app = "/Applications/WeChat.app"
            if not os.path.exists(wechat_app):
                return {
                    'success': False,
                    'message': "未找到微信应用，请先安装微信"
                }
            
            # 尝试获取微信版本
            result = subprocess.run(
                ["defaults", "read", wechat_app + "/Contents/Info.plist", "CFBundleShortVersionString"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"检测到微信版本: {version}")
                
                # 检查是否为 4.x 版本
                major_version = int(version.split('.')[0])
                if major_version < 4:
                    return {
                        'success': False,
                        'message': f"微信版本 {version} 过低，需要 4.x 版本以上才能使用此功能"
                    }
            
            return {'success': True, 'message': "微信版本检查通过"}
        except Exception as e:
            return {
                'success': False,
                'message': f"检查微信版本时发生错误: {str(e)}"
            }
    
    def _check_wechat_signature(self):
        """检查微信签名状态"""
        try:
            import subprocess
            
            # 检查微信签名状态
            result = subprocess.run(
                ["codesign", "-dv", "/Applications/WeChat.app"],
                capture_output=True,
                text=True
            )
            
            # 检查输出中是否包含 ad-hoc 签名
            if "Signature=adhoc" in result.stdout:
                return {'success': True, 'message': "微信已使用 ad-hoc 签名"}
            else:
                return {
                    'success': False,
                    'message': "微信需要 ad-hoc 签名才能解密数据库，请执行以下操作：\n" +
                              "# 1. 退出微信\nkillall WeChat\n" +
                              "# 2. Ad-hoc 签名（需要输入密码）\nsudo codesign --force --deep --sign - /Applications/WeChat.app\n" +
                              "# 3. 重新打开微信并登录\n" +
                              "# 4. 提取密钥\ncd ~/.qclaw/workspace/wechat-decrypt && sudo ./find_all_keys_macos"
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"检查微信签名状态时发生错误: {str(e)}"
            }
    
    def _auto_install_wechat_decrypt(self):
        """自动安装 wechat-decrypt 工具"""
        try:
            import subprocess
            import os
            
            # 检查是否已安装
            if os.path.exists("wechat-decrypt"):
                return True, "wechat-decrypt 工具已存在"
            
            # 克隆仓库
            print("正在安装 wechat-decrypt 工具...")
            subprocess.run(["git", "clone", "https://github.com/ylytdeng/wechat-decrypt.git"], check=True)
            
            # 安装依赖
            print("正在安装依赖...")
            subprocess.run(["pip", "install", "-r", "wechat-decrypt/requirements.txt"], check=True)
            
            return True, "wechat-decrypt 工具安装成功"
        except Exception as e:
            return False, f"安装 wechat-decrypt 工具失败: {str(e)}"
    
    def _find_macos_db_storage(self):
        """查找 macOS 微信 db_storage 目录"""
        try:
            import os
            import glob
            
            # 自动获取当前用户的主目录
            home_dir = os.path.expanduser("~")
            
            # 新路径：/Users/用户名/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/*/db_storage
            search_path = os.path.join(home_dir, "Library", "Containers", "com.tencent.xinWeChat", "Data", "Documents", "xwechat_files")
            
            if os.path.exists(search_path):
                # 查找所有 db_storage 目录
                db_storage_dirs = glob.glob(os.path.join(search_path, "*", "db_storage"))
                if db_storage_dirs:
                    # 返回第一个找到的 db_storage 目录
                    return db_storage_dirs[0]
            
            # 旧路径：~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/4.0b*/db_storage
            old_search_path = os.path.join(home_dir, "Library", "Containers", "com.tencent.xinWeChat", "Data", "Library", "Application Support", "com.tencent.xinWeChat")
            if os.path.exists(old_search_path):
                db_storage_dirs = glob.glob(os.path.join(old_search_path, "4.0b*", "db_storage"))
                if db_storage_dirs:
                    return db_storage_dirs[0]
            
            return None
        except Exception:
            return None
    
    def _run_wechat_decrypt(self, db_dir, output_dir):
        """运行 wechat-decrypt 工具解密数据库"""
        try:
            import subprocess
            import os
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 运行解密命令
            print(f"正在解密微信数据库，路径: {db_dir}")
            result = subprocess.run(
                ["python", "wechat-decrypt/main.py", "decrypt", "--db-dir", db_dir, "--decrypted-dir", output_dir],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, "解密成功"
            else:
                return False, f"解密失败: {result.stderr}"
        except Exception as e:
            return False, f"运行解密工具失败: {str(e)}"
    
    def auto_decrypt(self, output_dir):
        """自动解密微信数据库（根据平台选择方法）"""
        if self.is_windows:
            return self.decrypt_windows(output_dir)
        elif self.is_macos:
            return self.decrypt_macos(output_dir)
        else:
            return False, "当前平台不支持自动解密"
