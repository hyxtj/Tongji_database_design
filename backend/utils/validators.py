"""
数据验证工具
"""
import re


def validate_password_strength(password):
    """
    验证密码强度:至少包含字母、数字、符号中的两种
    
    Args:
        password: 待验证的密码
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "密码长度不能少于6位"
    
    if len(password) > 20:
        return False, "密码长度不能超过20位"
    
    # 检查是否包含字母、数字、符号
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_symbol = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))
    
    # 计算包含的类型数量
    type_count = sum([has_letter, has_digit, has_symbol])
    
    if type_count < 2:
        return False, "密码必须至少包含字母、数字、符号中的两种"
    
    return True, ""


def validate_email_format(email):
    """
    验证邮箱格式
    
    Args:
        email: 待验证的邮箱
        
    Returns:
        bool: 是否有效
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_username_format(username):
    """
    验证用户名格式
    
    Args:
        username: 待验证的用户名
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "用户名长度不能少于3个字符"
    
    if len(username) > 20:
        return False, "用户名长度不能超过20个字符"
    
    # 只允许字母、数字、下划线、中文
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        return False, "用户名只能包含字母、数字、下划线和中文"
    
    return True, ""
