from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Road, TrafficStatus, TrafficEvent, AuditLog
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
from utils.decorators import admin_required
from utils.backup_service import BackupService
import json
from io import BytesIO
from flask import send_file

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/backup', methods=['GET'])
@admin_required
def create_backup():
    """创建并下载数据库备份"""
    try:
        backup_data = BackupService.create_backup()
        
        # 创建内存文件
        mem = BytesIO()
        mem.write(json.dumps(backup_data, ensure_ascii=False, indent=2).encode('utf-8'))
        mem.seek(0)
        
        filename = f"traffic_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return send_file(
            mem,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/restore', methods=['POST'])
@admin_required
def restore_backup():
    """从备份文件恢复数据库"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
        
    try:
        content = file.read()
        backup_data = json.loads(content)
        
        success, message = BackupService.restore_backup(backup_data)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 500
            
    except json.JSONDecodeError:
        return jsonify({'error': '无效的JSON文件'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """获取管理员仪表板数据"""
    # 统计总数
    total_roads = Road.query.count()
    total_users = User.query.count()
    active_events = TrafficEvent.query.filter_by(status='active').count()
    
    # 最近24小时的交通状态统计
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    recent_statuses = TrafficStatus.query.filter(
        TrafficStatus.timestamp >= time_threshold
    ).count()
    
    # 道路类型分布
    road_type_stats = db.session.query(
        Road.road_type,
        func.count(Road.id).label('count')
    ).group_by(Road.road_type).all()
    
    # 事件类型分布(最近7天)
    event_threshold = datetime.utcnow() - timedelta(days=7)
    event_type_stats = db.session.query(
        TrafficEvent.event_type,
        func.count(TrafficEvent.id).label('count')
    ).filter(
        TrafficEvent.start_time >= event_threshold
    ).group_by(TrafficEvent.event_type).all()
    
    return jsonify({
        'overview': {
            'total_roads': total_roads,
            'total_users': total_users,
            'active_events': active_events,
            'recent_status_records': recent_statuses
        },
        'road_type_distribution': {stat.road_type or '未分类': stat.count for stat in road_type_stats},
        'event_type_distribution': {stat.event_type: stat.count for stat in event_type_stats}
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/users/<int:user_id>/admin', methods=['PUT'])
@admin_required
def toggle_admin(user_id):
    """切换用户管理员权限"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'is_admin' not in data:
        return jsonify({'error': '缺少is_admin字段'}), 400
    
    user.is_admin = data['is_admin']
    db.session.commit()
    
    return jsonify({
        'message': '权限更新成功',
        'user': user.to_dict()
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    current_user_id = get_jwt_identity()
    
    # 不能删除自己
    if current_user_id == user_id:
        return jsonify({'error': '不能删除自己'}), 400
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'}), 200


@admin_bp.route('/init-data', methods=['POST'])
@admin_required
def init_sample_data():
    """初始化示例数据"""
    import random
    from datetime import datetime, timedelta
    
    # 创建示例道路
    sample_roads = [
        {
            'name': '中山大道',
            'road_code': 'ZS001',
            'start_point': '江汉路',
            'end_point': '光谷广场',
            'length': 25.5,
            'lanes': 6,
            'road_type': '主干道',
            'latitude_start': 30.5928,
            'longitude_start': 114.3055,
            'latitude_end': 30.4760,
            'longitude_end': 114.4170,
            'description': '武汉市东西向主干道,连接江汉路商圈和光谷商圈'
        },
        {
            'name': '解放大道',
            'road_code': 'JF001',
            'start_point': '汉口火车站',
            'end_point': '武昌火车站',
            'length': 18.3,
            'lanes': 8,
            'road_type': '主干道',
            'latitude_start': 30.6188,
            'longitude_start': 114.2734,
            'latitude_end': 30.5272,
            'longitude_end': 114.3158,
            'description': '连接武汉三镇的重要交通干道'
        },
        {
            'name': '建设大道',
            'road_code': 'JS001',
            'start_point': '青年路',
            'end_point': '后湖',
            'length': 12.8,
            'lanes': 4,
            'road_type': '次干道',
            'latitude_start': 30.5975,
            'longitude_start': 114.2845,
            'latitude_end': 30.6145,
            'longitude_end': 114.3124,
            'description': '汉口地区重要次干道'
        },
        {
            'name': '珞喻路',
            'road_code': 'LY001',
            'start_point': '街道口',
            'end_point': '光谷广场',
            'length': 15.2,
            'lanes': 6,
            'road_type': '主干道',
            'latitude_start': 30.5188,
            'longitude_start': 114.3589,
            'latitude_end': 30.4760,
            'longitude_end': 114.4170,
            'description': '武昌区主要东西向干道,经过多所高校'
        },
        {
            'name': '武珞路',
            'road_code': 'WL001',
            'start_point': '洪山广场',
            'end_point': '街道口',
            'length': 8.5,
            'lanes': 4,
            'road_type': '次干道',
            'latitude_start': 30.5484,
            'longitude_start': 114.3166,
            'latitude_end': 30.5188,
            'longitude_end': 114.3589,
            'description': '连接武昌商业区和高校区'
        },
        {
            'name': '雄楚大道',
            'road_code': 'XC001',
            'start_point': '杨家湾',
            'end_point': '光谷大道',
            'length': 22.0,
            'lanes': 8,
            'road_type': '主干道',
            'latitude_start': 30.5012,
            'longitude_start': 114.3456,
            'latitude_end': 30.4698,
            'longitude_end': 114.4523,
            'description': '武汉市重要的东西向快速路'
        }
    ]
    
    created_roads = []
    for road_data in sample_roads:
        if not Road.query.filter_by(road_code=road_data['road_code']).first():
            road = Road(**road_data)
            db.session.add(road)
            created_roads.append(road)
    
    db.session.commit()
    
    # 为每条道路创建交通状态记录
    created_statuses = 0
    status_options = ['畅通', '缓行', '拥堵', '严重拥堵']
    
    for road in created_roads:
        # 创建最近24小时的状态记录(每2小时一条)
        for i in range(12):
            hours_ago = i * 2
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
            
            # 模拟早晚高峰
            hour = timestamp.hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                # 高峰期:更容易拥堵
                status = random.choice(['缓行', '拥堵', '严重拥堵'])
                speed = random.uniform(15, 35)
                congestion_index = random.uniform(0.6, 1.0)
            elif 11 <= hour <= 14:
                # 午间:中等拥堵
                status = random.choice(['畅通', '缓行', '缓行'])
                speed = random.uniform(30, 50)
                congestion_index = random.uniform(0.3, 0.6)
            else:
                # 其他时间:较为畅通
                status = random.choice(['畅通', '畅通', '缓行'])
                speed = random.uniform(40, 60)
                congestion_index = random.uniform(0.0, 0.4)
            
            traffic_status = TrafficStatus(
                road_id=road.id,
                status=status,
                speed=speed,
                congestion_index=congestion_index,
                travel_time=int(road.length / speed * 60) if speed > 0 else 999,
                vehicle_count=random.randint(50, 500),
                timestamp=timestamp,
                source='system_init'
            )
            db.session.add(traffic_status)
            created_statuses += 1
    
    db.session.commit()
    
    # 创建一些交通事件
    created_events = 0
    event_types = ['事故', '故障', '施工', '管制', '积水', '障碍物', '拥堵', '恶劣天气']
    severities = ['低', '中', '高']
    
    for road in created_roads[:4]:  # 为前4条道路创建事件
        # 创建1-2个事件
        for _ in range(random.randint(1, 2)):
            event_type = random.choice(event_types)
            severity = random.choice(severities)
            
            # 部分事件是活跃的,部分已解决
            is_active = random.random() > 0.3
            
            start_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            end_time = None if is_active else (start_time + timedelta(hours=random.randint(1, 6)))
            
            descriptions = {
                '事故': f'{road.name}发生交通事故,占用{random.randint(1, 2)}条车道',
                '故障': f'{road.name}有车辆故障抛锚,请注意避让',
                '施工': f'{road.name}路段进行道路维护施工',
                '管制': f'{road.name}实施临时交通管制',
                '积水': f'{road.name}路段积水严重,车辆通行缓慢',
                '障碍物': f'{road.name}路面有障碍物,正在清理',
                '拥堵': f'{road.name}出现严重拥堵,请择路绕行',
                '恶劣天气': f'{road.name}路段因恶劣天气影响通行'
            }
            
            event = TrafficEvent(
                road_id=road.id,
                event_type=event_type,
                severity=severity,
                description=descriptions[event_type],
                latitude=road.latitude_start,
                longitude=road.longitude_start,
                status='active' if is_active else 'resolved',
                start_time=start_time,
                end_time=end_time,
                affected_lanes=random.randint(1, road.lanes),
                source='system_init'
            )
            db.session.add(event)
            created_events += 1
    
    db.session.commit()
    
    return jsonify({
        'message': '示例数据初始化成功',
        'roads_created': len(created_roads),
        'traffic_statuses_created': created_statuses,
        'events_created': created_events,
        'details': {
            'roads': [road.name for road in created_roads],
            'time_range': '最近24小时的交通状态数据',
            'note': '数据包含模拟的早晚高峰拥堵情况'
        }
    }), 201


@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """获取审计日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    table_name = request.args.get('table_name')
    action = request.args.get('action')
    
    query = AuditLog.query
    
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if action:
        query = query.filter(AuditLog.action == action)
        
    pagination = query.order_by(AuditLog.changed_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200
