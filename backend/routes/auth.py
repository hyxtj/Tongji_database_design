from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import User
from extensions import db
from utils.validators import validate_password_strength, validate_email_format, validate_username_format
from utils.email_service import generate_verification_code, send_verification_email, is_verification_code_valid
from utils.decorators import admin_required
from utils.temp_storage import temp_storage

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册 - 第一步:发送验证码(不创建用户)"""
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 清理输入
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # 验证用户名格式
    is_valid, error = validate_username_format(username)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # 验证邮箱格式
    if not validate_email_format(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证密码强度
    is_valid, error = validate_password_strength(password)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    
    # 生成验证码
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(seconds=600)  # 10分钟
    
    # 创建临时用户对象来生成密码哈希
    temp_user = User()
    temp_user.set_password(password)
    password_hash = temp_user.password_hash
    
    # 将注册信息保存到临时存储(不写入数据库)
    temp_storage.save_registration(
        email=email,
        username=username,
        password_hash=password_hash,
        verification_code=code,
        expires_at=expires_at
    )
    
    # 发送验证码邮件
    success, error = send_verification_email(email, code, username)
    
    if not success and error:
        # 邮件发送失败,但验证码已保存在临时存储
        return jsonify({
            'message': '验证码已生成,但邮件发送失败',
            'email': email,
            'verification_required': True,
            'warning': '开发环境下,验证码会打印在后端控制台'
        }), 201
    
    return jsonify({
        'message': '验证码已发送到您的邮箱',
        'email': email,
        'verification_required': True,
        'expires_in': 600  # 秒
    }), 201


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """验证邮箱 - 验证通过后创建用户"""
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'code']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    email = data['email'].strip().lower()
    code = data['code'].strip()
    
    # 从临时存储获取注册信息
    registration_data = temp_storage.get_registration(email)
    
    if not registration_data:
        return jsonify({'error': '验证码已过期或不存在,请重新注册'}), 404
    
    # 检查验证码是否过期
    if registration_data['expires_at'] < datetime.utcnow():
        temp_storage.remove_registration(email)
        return jsonify({'error': '验证码已过期,请重新注册'}), 400
    
    # 验证验证码是否正确
    if registration_data['verification_code'] != code:
        return jsonify({'error': '验证码不正确'}), 400
    
    # 再次检查用户是否已存在(防止并发注册)
    if User.query.filter_by(username=registration_data['username']).first():
        temp_storage.remove_registration(email)
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=email).first():
        temp_storage.remove_registration(email)
        return jsonify({'error': '邮箱已被注册'}), 400
    
    # 创建真实用户(直接标记为已验证)
    user = User(
        username=registration_data['username'],
        email=email,
        password_hash=registration_data['password_hash'],
        email_verified=True  # 直接设置为已验证
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # 从临时存储中删除注册信息
        temp_storage.remove_registration(email)
        
        # 自动登录:生成token (identity必须是字符串)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': '注册成功',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建用户失败: {str(e)}'}), 500


@auth_bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    """重新发送验证码"""
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': '缺少邮箱地址'}), 400
    
    email = data['email'].strip().lower()
    
    # 从临时存储获取注册信息
    registration_data = temp_storage.get_registration(email)
    
    if not registration_data:
        return jsonify({'error': '注册信息不存在或已过期,请重新注册'}), 404
    
    # 生成新验证码
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(seconds=600)
    
    # 更新临时存储中的验证码
    temp_storage.save_registration(
        email=email,
        username=registration_data['username'],
        password_hash=registration_data['password_hash'],
        verification_code=code,
        expires_at=expires_at
    )
    
    # 发送验证码邮件
    success, error = send_verification_email(email, code, registration_data['username'])
    
    if not success and error:
        return jsonify({
            'message': '验证码已生成,但邮件发送失败',
            'warning': '开发环境下,验证码会打印在后端控制台'
        }), 201
    
    return jsonify({
        'message': '验证码已重新发送',
        'expires_in': 600
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 支持邮箱或用户名登录"""
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': '缺少邮箱或密码'}), 400
    
    email_or_username = data['email'].strip()
    
    # 尝试通过邮箱或用户名查找用户
    user = User.query.filter(
        (User.email == email_or_username) | (User.username == email_or_username)
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '邮箱/用户名或密码错误'}), 401
    
    # 检查邮箱是否已验证
    if not user.email_verified:
        return jsonify({
            'error': '邮箱尚未验证',
            'email': user.email,
            'verification_required': True
        }), 403
    
    # 生成token (identity必须是字符串)
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    # identity必须是字符串
    access_token = create_access_token(identity=str(current_user_id))
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 发送重置验证码"""
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': '请提供邮箱地址'}), 400
    
    email = data['email'].strip().lower()
    
    # 验证邮箱格式
    if not validate_email_format(email):
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 查找用户
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # 为了安全,即使用户不存在也返回成功(防止邮箱枚举攻击)
        return jsonify({'message': '如果该邮箱已注册,验证码将发送到您的邮箱'}), 200
    
    # 生成验证码
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(seconds=600)  # 10分钟
    
    # 更新用户的验证码
    user.verification_code = code
    user.verification_code_expires = expires_at
    db.session.commit()
    
    # 发送验证码邮件
    if not send_verification_email(email, code, is_reset=True):
        return jsonify({'error': '发送验证码失败,请稍后重试'}), 500
    
    return jsonify({'message': '验证码已发送到您的邮箱'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码 - 使用验证码"""
    data = request.get_json()
    
    # 验证必填字段
    if not all(k in data for k in ['email', 'code', 'new_password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    email = data['email'].strip().lower()
    code = data['code'].strip()
    new_password = data['new_password']
    
    # 查找用户
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 验证验证码
    if not is_verification_code_valid(user, code):
        return jsonify({'error': '验证码无效或已过期'}), 400
    
    # 验证新密码强度
    is_valid, error = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # 更新密码
    user.set_password(new_password)
    user.verification_code = None
    user.verification_code_expires = None
    db.session.commit()
    
    return jsonify({'message': '密码重置成功'}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新个人信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    data = request.get_json()
    
    # 更新邮箱
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if new_email != user.email:
            if not validate_email_format(new_email):
                return jsonify({'error': '邮箱格式不正确'}), 400
            
            if User.query.filter_by(email=new_email).first():
                return jsonify({'error': '邮箱已被使用'}), 400
                
            user.email = new_email
            
    db.session.commit()
    
    return jsonify({
        'message': '个人信息更新成功',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
        
    data = request.get_json()
    
    if not all(k in data for k in ['current_password', 'new_password']):
        return jsonify({'error': '缺少必填字段'}), 400
        
    current_password = data['current_password']
    new_password = data['new_password']
    
    # 验证当前密码
    if not user.check_password(current_password):
        return jsonify({'error': '当前密码错误'}), 400
        
    # 验证新密码强度
    is_valid, error = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({'error': error}), 400
        
    # 不能与旧密码相同
    if user.check_password(new_password):
        return jsonify({'error': '新密码不能与当前密码相同'}), 400
        
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200
