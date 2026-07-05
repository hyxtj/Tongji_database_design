from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import TrafficStatus, Road, User
from extensions import db, cache, limiter
from datetime import datetime, timedelta
from sqlalchemy import func
from utils.simulation import generate_realtime_traffic

traffic_bp = Blueprint('traffic', __name__)


@traffic_bp.route('/status', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
@limiter.limit("20 per minute")
def get_traffic_status():
    """获取交通状态列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    road_id = request.args.get('road_id', type=int)
    status = request.args.get('status', None)
    hours = request.args.get('hours', 24, type=int)  # 默认查询最近24小时
    
    query = TrafficStatus.query
    
    # 时间过滤
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(TrafficStatus.timestamp >= time_threshold)
    
    if road_id:
        query = query.filter_by(road_id=road_id)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(TrafficStatus.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'statuses': [status.to_dict() for status in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@traffic_bp.route('/status/latest', methods=['GET'])
# @cache.cached(timeout=60)  # 禁用缓存以支持实时更新
@limiter.limit("30 per minute")
def get_latest_traffic_status():
    """获取所有道路的最新交通状态"""
    # 检查数据是否陈旧(超过1分钟未更新)
    # 获取任意一条道路的最新状态时间
    latest_record = TrafficStatus.query.order_by(TrafficStatus.timestamp.desc()).first()
    
    should_update = False
    if not latest_record:
        should_update = True
    else:
        # 使用 datetime.now() 因为 seed_data 使用的是本地时间
        time_diff = datetime.now() - latest_record.timestamp
        if time_diff.total_seconds() > 60:  # 超过60秒未更新
            should_update = True
            
    if should_update:
        print("检测到数据陈旧，正在生成实时交通数据...")
        try:
            generate_realtime_traffic()
        except Exception as e:
            print(f"生成实时数据失败: {e}")
            db.session.rollback()

    # 优化查询：直接通过Road表的current_status_id关联获取
    # 这种方式避免了全表扫描和复杂的聚合查询
    roads = Road.query.filter(Road.current_status_id.isnot(None))\
        .options(db.joinedload(Road.current_status)).all()
    
    latest_statuses = [road.current_status for road in roads if road.current_status]
    
    return jsonify({
        'statuses': [status.to_dict() for status in latest_statuses],
        'count': len(latest_statuses)
    }), 200


@traffic_bp.route('/status', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def create_traffic_status():
    """创建交通状态记录(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    data = request.get_json()
    
    if 'road_id' not in data:
        return jsonify({'error': '缺少道路ID'}), 400
    
    # 验证道路是否存在
    road = Road.query.get(data['road_id'])
    if not road:
        return jsonify({'error': '道路不存在'}), 404
    
    # 根据拥堵指数自动判断状态
    congestion_index = data.get('congestion_index', 0)
    status = data.get('status') or TrafficStatus.get_status_from_index(congestion_index)
    
    traffic_status = TrafficStatus(
        road_id=data['road_id'],
        status=status,
        speed=data.get('speed'),
        congestion_index=congestion_index,
        travel_time=data.get('travel_time'),
        vehicle_count=data.get('vehicle_count'),
        source=data.get('source', 'manual')
    )
    
    db.session.add(traffic_status)
    
    # 关键优化：更新Road表的current_status_id
    # 先flush以获取新生成的ID
    db.session.flush()
    road.current_status_id = traffic_status.id
    
    db.session.commit()
    
    return jsonify({
        'message': '交通状态创建成功',
        'status': traffic_status.to_dict()
    }), 201


@traffic_bp.route('/status/<int:road_id>/history', methods=['GET'])
def get_road_traffic_history(road_id):
    """获取指定道路的交通状态历史"""
    hours = request.args.get('hours', 24, type=int)
    
    road = Road.query.get_or_404(road_id)
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    statuses = TrafficStatus.query.filter(
        TrafficStatus.road_id == road_id,
        TrafficStatus.timestamp >= time_threshold
    ).order_by(TrafficStatus.timestamp.asc()).all()
    
    return jsonify({
        'road': road.to_dict(),
        'history': [status.to_dict() for status in statuses],
        'count': len(statuses)
    }), 200


@traffic_bp.route('/statistics', methods=['GET'])
def get_traffic_statistics():
    """获取交通统计数据"""
    hours = request.args.get('hours', 24, type=int)
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # 按状态统计
    status_stats = db.session.query(
        TrafficStatus.status,
        func.count(TrafficStatus.id).label('count')
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).group_by(TrafficStatus.status).all()
    
    # 平均拥堵指数
    avg_congestion = db.session.query(
        func.avg(TrafficStatus.congestion_index)
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).scalar() or 0
    
    # 平均速度
    avg_speed = db.session.query(
        func.avg(TrafficStatus.speed)
    ).filter(
        TrafficStatus.timestamp >= time_threshold,
        TrafficStatus.speed.isnot(None)
    ).scalar() or 0
    
    return jsonify({
        'status_distribution': {stat.status: stat.count for stat in status_stats},
        'avg_congestion_index': round(avg_congestion, 2),
        'avg_speed': round(avg_speed, 2),
        'period_hours': hours
    }), 200


@traffic_bp.route('/analysis/peak-hours', methods=['GET'])
def analyze_peak_hours():
    """分析高峰时段"""
    days = request.args.get('days', 7, type=int)
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    # 按小时统计平均拥堵指数
    hourly_stats = db.session.query(
        func.strftime('%H', TrafficStatus.timestamp).label('hour'),
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.count(TrafficStatus.id).label('count')
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).group_by('hour').all()
    
    # 格式化结果
    result = []
    for stat in hourly_stats:
        result.append({
            'hour': int(stat.hour),
            'avg_congestion': round(stat.avg_congestion, 2),
            'record_count': stat.count
        })
    
    # 按小时排序
    result.sort(key=lambda x: x['hour'])
    
    return jsonify({
        'peak_hours_analysis': result,
        'days_analyzed': days,
        'note': '数据显示了每小时的平均拥堵指数'
    }), 200


@traffic_bp.route('/analysis/congested-roads', methods=['GET'])
def get_most_congested_roads():
    """获取最拥堵的道路"""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 10, type=int)
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # 使用JOIN优化查询，避免N+1问题
    congested_roads = db.session.query(
        Road,
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.count(TrafficStatus.id).label('record_count')
    ).join(
        TrafficStatus, Road.id == TrafficStatus.road_id
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).group_by(Road.id).order_by(
        func.avg(TrafficStatus.congestion_index).desc()
    ).limit(limit).all()
    
    # 格式化结果
    result = []
    for road, avg_congestion, record_count in congested_roads:
        result.append({
            'road': road.to_dict(),
            'avg_congestion_index': round(avg_congestion, 2),
            'record_count': record_count
        })
    
    return jsonify({
        'most_congested_roads': result,
        'period_hours': hours
    }), 200


@traffic_bp.route('/analysis/smooth-roads', methods=['GET'])
def get_smoothest_roads():
    """获取最畅通的道路"""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 10, type=int)
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # 使用JOIN优化查询，避免N+1问题
    smooth_roads = db.session.query(
        Road,
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed'),
        func.count(TrafficStatus.id).label('record_count')
    ).join(
        TrafficStatus, Road.id == TrafficStatus.road_id
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).group_by(Road.id).order_by(
        func.avg(TrafficStatus.congestion_index).asc()
    ).limit(limit).all()
    
    # 格式化结果
    result = []
    for road, avg_congestion, avg_speed, record_count in smooth_roads:
        result.append({
            'road': road.to_dict(),
            'avg_congestion_index': round(avg_congestion, 2),
            'avg_speed': round(avg_speed, 2) if avg_speed else None,
            'record_count': record_count
        })
    
    return jsonify({
        'smoothest_roads': result,
        'period_hours': hours
    }), 200


@traffic_bp.route('/realtime/summary', methods=['GET'])
def get_realtime_summary():
    """获取实时交通概览"""
    # 获取最新的交通状态
    subquery = db.session.query(
        TrafficStatus.road_id,
        func.max(TrafficStatus.timestamp).label('max_timestamp')
    ).group_by(TrafficStatus.road_id).subquery()
    
    latest_statuses = db.session.query(TrafficStatus).join(
        subquery,
        db.and_(
            TrafficStatus.road_id == subquery.c.road_id,
            TrafficStatus.timestamp == subquery.c.max_timestamp
        )
    ).all()
    
    # 统计各状态的道路数量
    status_counts = {
        '畅通': 0,
        '缓行': 0,
        '拥堵': 0,
        '严重拥堵': 0
    }
    
    total_congestion = 0
    total_speed = 0
    speed_count = 0
    
    for status in latest_statuses:
        if status.status in status_counts:
            status_counts[status.status] += 1
        total_congestion += status.congestion_index or 0
        if status.speed:
            total_speed += status.speed
            speed_count += 1
    
    total_roads = len(latest_statuses)
    
    return jsonify({
        'total_roads': total_roads,
        'status_breakdown': status_counts,
        'avg_congestion_index': round(total_congestion / total_roads, 2) if total_roads > 0 else 0,
        'avg_speed': round(total_speed / speed_count, 2) if speed_count > 0 else 0,
        'update_time': datetime.utcnow().isoformat()
    }), 200


@traffic_bp.route('/route-estimate', methods=['POST'])
def estimate_route_time():
    """
    估算路线通行时间
    接收道路ID列表，返回总距离、预计时间和平均速度
    """
    data = request.get_json()
    road_ids = data.get('road_ids', [])
    
    if not road_ids:
        return jsonify({'error': '请提供道路ID列表'}), 400
        
    # 获取这些道路的最新状态
    # 使用子查询获取每条路最新的状态ID
    subquery = db.session.query(
        func.max(TrafficStatus.id).label('max_id')
    ).filter(TrafficStatus.road_id.in_(road_ids)).group_by(TrafficStatus.road_id).subquery()
    
    # 查询具体状态信息
    latest_statuses = db.session.query(TrafficStatus).join(
        subquery, TrafficStatus.id == subquery.c.max_id
    ).all()
    
    # 创建查找字典
    status_map = {s.road_id: s for s in latest_statuses}
    
    # 获取道路基础信息
    roads = Road.query.filter(Road.id.in_(road_ids)).all()
    road_map = {r.id: r for r in roads}
    
    total_distance = 0 # km
    total_time_seconds = 0
    segments = []
    
    # 按请求顺序处理
    for rid in road_ids:
        road = road_map.get(rid)
        if not road:
            continue
            
        status = status_map.get(rid)
        
        # 如果没有实时状态，使用默认速度
        if status and status.speed and status.speed > 0:
            speed = status.speed
            congestion = status.congestion_index
            status_text = status.status
        else:
            # 默认速度
            speed = 60 if road.road_type != '快速路' else 80
            congestion = 0
            status_text = '未知'
            
        distance = road.length # km
        time_needed = (distance / speed) * 3600 # seconds
        
        total_distance += distance
        total_time_seconds += time_needed
        
        segments.append({
            'road_name': road.name,
            'length': distance,
            'speed': speed,
            'time_seconds': round(time_needed),
            'status': status_text
        })
        
    avg_speed = (total_distance / (total_time_seconds / 3600)) if total_time_seconds > 0 else 0
    
    return jsonify({
        'total_distance_km': round(total_distance, 2),
        'total_time_minutes': round(total_time_seconds / 60, 1),
        'avg_speed_kmh': round(avg_speed, 1),
        'segments': segments
    })
