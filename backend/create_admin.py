"""
创建初始管理员账户
运行方式: uv run python create_admin.py
"""
from app import create_app
from models import User
from extensions import db


def create_admin():
    """创建管理员账户"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("🔐 创建管理员账户")
        print("="*50 + "\n")
        
        # 检查是否已存在管理员
        admin_email = 'admin@traffic.com'
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f'⚠️  管理员账户已存在: {admin.email}')
            
            # 确保是管理员且邮箱已验证
            if not admin.is_admin or not admin.email_verified:
                admin.is_admin = True
                admin.email_verified = True
                db.session.commit()
                print('✅ 已更新管理员权限和邮箱验证状态')
            
            print(f'\n管理员信息:')
            print(f'  用户名: {admin.username}')
            print(f'  邮箱: {admin.email}')
            print(f'  管理员: {"是" if admin.is_admin else "否"}')
            print(f'  邮箱已验证: {"是" if admin.email_verified else "否"}')
            
        else:
            # 创建新管理员
            print('正在创建新管理员账户...\n')
            
            admin = User(
                username='admin',
                email=admin_email,
                is_admin=True,
                email_verified=True  # 管理员账户默认已验证
            )
            # 密码:Admin@123 (包含字母、数字、符号)
            admin.set_password('Admin@123')
            
            try:
                db.session.add(admin)
                db.session.commit()
                
                print('✅ 管理员账户创建成功!\n')
                print(f'登录信息:')
                print(f'  邮箱: {admin.email}')
                print(f'  用户名: {admin.username}')
                print(f'  密码: Admin@123')
                print(f'\n⚠️  请登录后立即修改密码!')
                
            except Exception as e:
                db.session.rollback()
                print(f'❌ 创建失败: {str(e)}')
                return
        
        print("\n" + "="*50 + "\n")


if __name__ == '__main__':
    create_admin()
