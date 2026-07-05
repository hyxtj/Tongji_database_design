from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import TrafficEvent, Road, User
from extensions import db
from datetime import datetime, timedelta

events_bp = Blueprint('events', __name__)


@events_bp.route('', methods=['GET'], strict_slashes=False)
def get_events():
    """获取交通事件列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    road_id = request.args.get('road_id', type=int)
    event_type = request.args.get('type', None)
    status = request.args.get('status', 'active')
    days = request.args.get('days', 7, type=int)
    severity = request.args.get('severity', None)
    
    query = TrafficEvent.query
    
    # 时间过滤
    time_threshold = datetime.utcnow() - timedelta(days=days)
    query = query.filter(TrafficEvent.start_time >= time_threshold)
    
    if road_id:
        query = query.filter_by(road_id=road_id)
    
    if event_type:
        query = query.filter_by(event_type=event_type)

    if severity:
        query = query.filter_by(severity=severity)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(TrafficEvent.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'events': [event.to_dict() for event in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """获取单个事件详情"""
    event = TrafficEvent.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200


@events_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_event():
    """创建交通事件(管理员直接发布，普通用户需审核)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['road_id', 'event_type', 'description']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 验证道路是否存在
    road = Road.query.get(data['road_id'])
    if not road:
        return jsonify({'error': '道路不存在'}), 404
    
    # 根据用户权限设置初始状态
    initial_status = 'active' if user.is_admin else 'pending'
    source = 'admin' if user.is_admin else 'user_report'
    
    event = TrafficEvent(
        road_id=data['road_id'],
        event_type=data['event_type'],
        severity=data.get('severity', '一般'),
        description=data['description'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        affected_lanes=data.get('affected_lanes'),
        source=source,
        status=initial_status
    )
    
    db.session.add(event)
    db.session.commit()
    
    message = '交通事件创建成功' if user.is_admin else '事件上报成功，等待管理员审核'
    
    return jsonify({
        'message': message,
        'event': event.to_dict()
    }), 201


@events_bp.route('/<int:event_id>/approve', methods=['PUT'])
@jwt_required()
def approve_event(event_id):
    """审核通过事件(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
        
    event = TrafficEvent.query.get_or_404(event_id)
    
    if event.status != 'pending':
        return jsonify({'error': '该事件不需要审核'}), 400
        
    event.status = 'active'
    db.session.commit()
    
    return jsonify({
        'message': '事件审核通过',
        'event': event.to_dict()
    }), 200


@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """更新交通事件(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    event = TrafficEvent.query.get_or_404(event_id)
    data = request.get_json()
    
    # 更新字段
    for key in ['event_type', 'severity', 'description', 'latitude', 
                'longitude', 'status', 'affected_lanes']:
        if key in data:
            setattr(event, key, data[key])
    
    # 如果状态变为resolved,设置结束时间
    if data.get('status') == 'resolved' and not event.end_time:
        event.end_time = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': '交通事件更新成功',
        'event': event.to_dict()
    }), 200


@events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """删除交通事件(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    event = TrafficEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': '交通事件删除成功'}), 200


@events_bp.route('/active', methods=['GET'])
def get_active_events():
    """获取所有活跃的交通事件"""
    events = TrafficEvent.query.filter_by(status='active').order_by(
        TrafficEvent.start_time.desc()
    ).all()
    
    return jsonify({
        'events': [event.to_dict() for event in events],
        'count': len(events)
    }), 200


@events_bp.route('/statistics', methods=['GET'])
def get_event_statistics():
    """获取交通事件统计"""
    days = request.args.get('days', 30, type=int)
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    # 按类型统计
    from sqlalchemy import func
    type_stats = db.session.query(
        TrafficEvent.event_type,
        func.count(TrafficEvent.id).label('count')
    ).filter(
        TrafficEvent.start_time >= time_threshold
    ).group_by(TrafficEvent.event_type).all()
    
    # 按严重程度统计
    severity_stats = db.session.query(
        TrafficEvent.severity,
        func.count(TrafficEvent.id).label('count')
    ).filter(
        TrafficEvent.start_time >= time_threshold
    ).group_by(TrafficEvent.severity).all()
    
    # 按状态统计
    status_stats = db.session.query(
        TrafficEvent.status,
        func.count(TrafficEvent.id).label('count')
    ).filter(
        TrafficEvent.start_time >= time_threshold
    ).group_by(TrafficEvent.status).all()
    
    # 平均持续时间(已解决的事件)
    resolved_events = TrafficEvent.query.filter(
        TrafficEvent.status == 'resolved',
        TrafficEvent.start_time >= time_threshold,
        TrafficEvent.end_time.isnot(None)
    ).all()
    
    avg_duration = 0
    if resolved_events:
        total_duration = sum([
            (event.end_time - event.start_time).total_seconds() / 3600
            for event in resolved_events
        ])
        avg_duration = total_duration / len(resolved_events)
    
    return jsonify({
        'type_distribution': {stat.event_type: stat.count for stat in type_stats},
        'severity_distribution': {stat.severity: stat.count for stat in severity_stats},
        'status_distribution': {stat.status: stat.count for stat in status_stats},
        'avg_duration_hours': round(avg_duration, 2),
        'period_days': days,
        'total_events': sum(stat.count for stat in type_stats)
    }), 200


@events_bp.route('/by-severity/<severity>', methods=['GET'])
def get_events_by_severity(severity):
    """根据严重程度获取事件"""
    events = TrafficEvent.query.filter_by(
        severity=severity,
        status='active'
    ).order_by(TrafficEvent.start_time.desc()).all()
    
    return jsonify({
        'severity': severity,
        'events': [event.to_dict() for event in events],
        'count': len(events)
    }), 200


@events_bp.route('/recent', methods=['GET'])
def get_recent_events():
    """获取最近的事件(包括已解决的)"""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    events = TrafficEvent.query.filter(
        TrafficEvent.start_time >= time_threshold
    ).order_by(TrafficEvent.start_time.desc()).limit(limit).all()
    
    return jsonify({
        'events': [event.to_dict() for event in events],
        'count': len(events),
        'period_hours': hours
    }), 200
