"""
重置数据库脚本
运行方式: python reset_db.py
"""
from app import create_app
from extensions import db
from models import Road, TrafficStatus, TrafficEvent, WeatherCondition, TrafficPrediction, MaintenanceSchedule
from sqlalchemy import text

def reset_database():
    """清空并重新创建数据库"""
    app = create_app()
    with app.app_context():
        print("📊 正在删除所有表...")
        # 禁用外键检查
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        
        # 获取所有表名并删除
        result = db.session.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        
        if tables:
            for table in tables:
                print(f"  - 删除表: {table}")
                db.session.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
            db.session.commit()
        
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()
        
        print("📋 正在创建所有表...")
        db.create_all()
        
        # 执行触发器SQL
        print("🔧 正在配置数据库触发器...")
        try:
            import os
            
            migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_audit_trigger.sql')
            if os.path.exists(migration_file):
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    # 使用自定义分隔符分割SQL语句
                    statements = sql_content.split('-- STATEMENT_SPLIT')
                    for statement in statements:
                        if statement.strip():
                            db.session.execute(text(statement))
                    db.session.commit()
                print("✅ 触发器配置成功!")
            else:
                print(f"⚠️ 未找到触发器文件: {migration_file}")
        except Exception as e:
            print(f"❌ 触发器配置失败: {str(e)}")
        
        print("✅ 数据库重置完成!")

if __name__ == '__main__':
    reset_database()
