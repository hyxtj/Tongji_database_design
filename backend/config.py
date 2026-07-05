import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置"""
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///traffic_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL')

    # 缓存配置
    if REDIS_URL:
        CACHE_TYPE = 'RedisCache'
        CACHE_REDIS_URL = REDIS_URL
        RATELIMIT_STORAGE_URI = REDIS_URL
    else:
        CACHE_TYPE = 'SimpleCache'
        RATELIMIT_STORAGE_URI = 'memory://'

    CACHE_DEFAULT_TIMEOUT = 300
    
    # 限流配置
    RATELIMIT_DEFAULT = "20000 per day; 2000 per minute"
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@traffic-system.com')
    
    # 验证码配置
    VERIFICATION_CODE_EXPIRES = int(os.getenv('VERIFICATION_CODE_EXPIRES', 600))  # 10分钟
    
    # API密钥
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', '')
    BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', '')
    
    # 分页配置
    ITEMS_PER_PAGE = 20
