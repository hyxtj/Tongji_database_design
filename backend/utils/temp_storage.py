"""临时存储 - 用于存储待验证的注册信息"""
from datetime import datetime
from threading import Lock

class TempStorage:
    """临时存储类 - 使用内存存储待验证的注册信息"""
    
    def __init__(self):
        self.storage = {}  # key: email, value: registration data
        self.lock = Lock()
    
    def save_registration(self, email, username, password_hash, verification_code, expires_at):
        """保存待验证的注册信息"""
        with self.lock:
            self.storage[email] = {
                'username': username,
                'password_hash': password_hash,
                'verification_code': verification_code,
                'expires_at': expires_at,
                'created_at': datetime.utcnow()
            }
    
    def get_registration(self, email):
        """获取待验证的注册信息"""
        with self.lock:
            return self.storage.get(email)
    
    def remove_registration(self, email):
        """删除待验证的注册信息"""
        with self.lock:
            if email in self.storage:
                del self.storage[email]
    
    def cleanup_expired(self):
        """清理过期的注册信息"""
        with self.lock:
            now = datetime.utcnow()
            expired_emails = [
                email for email, data in self.storage.items()
                if data['expires_at'] < now
            ]
            for email in expired_emails:
                del self.storage[email]
            return len(expired_emails)

# 全局单例
temp_storage = TempStorage()
