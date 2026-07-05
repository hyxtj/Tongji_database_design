"""
用户认证功能测试脚本
使用此脚本测试注册和登录功能
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """打印响应信息"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_register():
    """测试用户注册"""
    print("\n🧪 测试1: 用户注册")
    
    data = {
        "username": "测试用户001",
        "email": "test001@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response("注册结果", response)
    
    return response.json()

def test_login_with_email(email, password):
    """测试使用邮箱登录"""
    print("\n🧪 测试2: 邮箱登录")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("邮箱登录结果", response)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_login_with_username(username, password):
    """测试使用用户名登录"""
    print("\n🧪 测试3: 用户名登录")
    
    data = {
        "email": username,  # 后端会尝试匹配邮箱或用户名
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("用户名登录结果", response)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_get_current_user(token):
    """测试获取当前用户信息"""
    print("\n🧪 测试4: 获取用户信息")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("用户信息", response)

def test_duplicate_register():
    """测试重复注册"""
    print("\n🧪 测试5: 重复注册(应该失败)")
    
    data = {
        "username": "测试用户001",
        "email": "test001@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response("重复注册结果", response)

def test_invalid_email():
    """测试无效邮箱"""
    print("\n🧪 测试6: 无效邮箱格式")
    
    data = {
        "username": "测试用户002",
        "email": "invalid-email",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response("无效邮箱注册结果", response)

def test_short_password():
    """测试短密码"""
    print("\n🧪 测试7: 密码过短")
    
    data = {
        "username": "测试用户003",
        "email": "test003@example.com",
        "password": "123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response("短密码注册结果", response)

def test_wrong_password(email):
    """测试错误密码"""
    print("\n🧪 测试8: 错误密码登录")
    
    data = {
        "email": email,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("错误密码登录结果", response)

def main():
    """主测试流程"""
    print("\n" + "="*50)
    print("🚀 开始测试用户认证功能")
    print("="*50)
    
    try:
        # 1. 注册新用户
        register_result = test_register()
        
        if register_result:
            email = register_result.get('user', {}).get('email')
            username = register_result.get('user', {}).get('username')
            
            # 2. 使用邮箱登录
            token = test_login_with_email(email, "password123")
            
            # 3. 使用用户名登录
            if username:
                test_login_with_username(username, "password123")
            
            # 4. 获取用户信息
            if token:
                test_get_current_user(token)
            
            # 5. 测试重复注册
            test_duplicate_register()
            
            # 6. 测试无效邮箱
            test_invalid_email()
            
            # 7. 测试短密码
            test_short_password()
            
            # 8. 测试错误密码
            if email:
                test_wrong_password(email)
        
        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("请确保后端服务正在运行: http://localhost:5000")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()

