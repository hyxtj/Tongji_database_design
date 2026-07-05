"""
权限装饰器
用于保护需要特定权限的路由
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
from models import User
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def admin_required(fn):
    """
    管理员权限装饰器
    用于保护只有管理员才能访问的路由
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # 手动验证JWT，以便捕获具体错误
            verify_jwt_in_request()
            
            # 获取当前用户ID
            current_user_id = get_jwt_identity()
            logger.info(f"Admin check for user_id: {current_user_id}")
            
            if current_user_id is None:
                logger.error("No identity found in JWT")
                return jsonify({'error': '无效的认证信息'}), 422
            
            # 查询用户
            user = User.query.get(current_user_id)
            
            if not user:
                logger.error(f"User not found for id: {current_user_id}")
                return jsonify({'error': '用户不存在'}), 404
            
            if not user.is_admin:
                logger.warning(f"User {user.username} (id: {user.id}) is not admin")
                return jsonify({'error': '需要管理员权限'}), 403
            
            # 执行原函数
            return fn(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"JWT Verification failed in admin_required: {str(e)}")
            # 如果是JWT相关错误，通常是401或422
            return jsonify({'error': f'认证失败: {str(e)}'}), 422
    
    return wrapper


def email_verified_required(fn):
    """
    邮箱验证装饰器
    用于保护需要验证邮箱才能访问的路由
    
    使用示例:
        @email_verified_required
        def some_verified_function():
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 验证JWT token
        verify_jwt_in_request()
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        # 查询用户
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        if not user.email_verified:
            return jsonify({'error': '请先验证邮箱'}), 403
        
        # 执行原函数
        return fn(*args, **kwargs)
    
    return wrapper


def get_current_user():
    """
    获取当前登录的用户对象
    
    Returns:
        User: 用户对象,如果未登录或用户不存在则返回 None
    """
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None
