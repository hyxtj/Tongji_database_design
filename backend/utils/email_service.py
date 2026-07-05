"""
邮件发送服务
"""
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app


def generate_verification_code(length=6):
    """
    生成验证码
    
    Args:
        length: 验证码长度,默认6位
        
    Returns:
        str: 验证码
    """
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email, code, username=None, is_reset=False):
    """
    发送验证码邮件
    
    Args:
        email: 收件人邮箱
        code: 验证码
        username: 用户名(可选)
        is_reset: 是否为密码重置(默认为注册)
        
    Returns:
        tuple: (success, error_message)
    """
    try:
        # 获取配置
        mail_server = current_app.config['MAIL_SERVER']
        mail_port = current_app.config['MAIL_PORT']
        mail_username = current_app.config['MAIL_USERNAME']
        mail_password = current_app.config['MAIL_PASSWORD']
        mail_sender = current_app.config['MAIL_DEFAULT_SENDER']
        mail_use_tls = current_app.config['MAIL_USE_TLS']
        
        # 如果没有配置邮件服务,返回模拟成功(用于开发测试)
        if not mail_username or not mail_password:
            action = "密码重置" if is_reset else "注册"
            print(f"[开发模式] {action}验证码邮件: {email} -> {code}")
            return True, None
        
        # 根据类型设置不同的内容
        if is_reset:
            subject = '城市交通查询系统 - 密码重置验证码'
            action_text = '重置密码'
            action_desc = '正在重置您的账户密码'
        else:
            subject = '城市交通查询系统 - 邮箱验证码'
            action_text = '注册'
            action_desc = '正在注册城市交通查询系统'
        
        # 创建邮件
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = mail_sender
        message['To'] = email
        
        # 邮件内容
        text_content = f"""
您好{f' {username}' if username else ''}!

您{action_desc},您的验证码是:

{code}

该验证码10分钟内有效,请及时使用。

如果这不是您本人的操作,请忽略此邮件。

---
城市交通查询系统
        """
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                    }}
                    .code {{
                        font-size: 32px;
                        font-weight: bold;
                        color: {'#e74c3c' if is_reset else '#667eea'};
                        text-align: center;
                        padding: 20px;
                        background-color: #f0f0f0;
                        border-radius: 5px;
                        margin: 20px 0;
                        letter-spacing: 5px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 10px;
                        margin: 20px 0;
                        border-radius: 3px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        color: #999;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚦 城市交通查询系统</h1>
                    </div>
                    <div class="content">
                        <p>您好{f' <strong>{username}</strong>' if username else ''}!</p>
                        <p>您{action_desc},请使用以下验证码完成{action_text}:</p>
                        <div class="code">{code}</div>
                        <p>该验证码 <strong>10分钟</strong> 内有效,请及时使用。</p>
                        {'<div class="warning"><strong>⚠️ 安全提示:</strong> 如果这不是您本人的操作,您的账户可能存在安全风险,请立即修改密码!</div>' if is_reset else ''}
                        <p>如果这不是您本人的操作,请忽略此邮件。</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 城市交通查询系统 - 让出行更智能</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # 添加文本和HTML版本
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
        
        # 发送邮件
        if mail_use_tls:
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(mail_server, mail_port)
        
        server.login(mail_username, mail_password)
        server.sendmail(mail_sender, email, message.as_string())
        server.quit()
        
        return True, None
        
    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}"
        print(error_msg)
        return False, error_msg


def is_verification_code_valid(user, code):
    """
    验证验证码是否有效
    
    Args:
        user: 用户对象
        code: 输入的验证码
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not user.verification_code:
        return False, "验证码不存在"
    
    if user.verification_code != code:
        return False, "验证码错误"
    
    if user.verification_code_expires < datetime.utcnow():
        return False, "验证码已过期"
    
    return True, None
