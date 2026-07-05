import json
from datetime import datetime
from extensions import db
from models import User, Road, TrafficEvent, TrafficStatus, WeatherCondition, TrafficPrediction, MaintenanceSchedule

class BackupService:
    MODELS = {
        'users': User,
        'roads': Road,
        'traffic_events': TrafficEvent,
        'traffic_statuses': TrafficStatus,
        'weather_conditions': WeatherCondition,
        'traffic_predictions': TrafficPrediction,
        'maintenance_schedules': MaintenanceSchedule
    }

    @staticmethod
    def create_backup():
        """创建数据库备份"""
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0',
            'data': {}
        }

        for name, model in BackupService.MODELS.items():
            records = model.query.all()
            backup_data['data'][name] = [record.to_dict() for record in records]
            
        return backup_data

    @staticmethod
    def restore_backup(backup_data):
        """从备份恢复数据库"""
        try:
            # 验证备份格式
            if 'data' not in backup_data:
                raise ValueError("无效的备份文件格式")

            # 按照依赖关系的逆序清空表 (简单起见，这里使用禁用外键检查的方式)
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            
            for name, model in BackupService.MODELS.items():
                # 清空表
                model.query.delete()
                
                # 插入数据
                if name in backup_data['data']:
                    for item_data in backup_data['data'][name]:
                        # 处理日期时间字段
                        for key, value in item_data.items():
                            if isinstance(value, str) and ('time' in key or 'date' in key or 'at' in key):
                                try:
                                    item_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except:
                                    pass
                        
                        # 过滤掉不在模型中的字段 (例如 to_dict 可能返回额外的计算字段)
                        valid_columns = model.__table__.columns.keys()
                        filtered_data = {k: v for k, v in item_data.items() if k in valid_columns}
                        
                        record = model(**filtered_data)
                        db.session.add(record)
            
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
            return True, "恢复成功"
            
        except Exception as e:
            db.session.rollback()
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            return False, str(e)
