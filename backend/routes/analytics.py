"""
数据分析路由模块
提供交通数据的深度分析和统计功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import TrafficStatus, TrafficEvent, Road, User
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case, text
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


# ============== 时间序列分析 ==============

@analytics_bp.route('/time-series/congestion', methods=['GET'])
def get_congestion_time_series():
    """获取拥堵指数时间序列数据"""
    # 支持两种参数方式：日期范围 或 小时数
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    hours = request.args.get('hours', type=int)
    aggregation = request.args.get('aggregation', 'day')
    road_id = request.args.get('road_id', type=int)
    
    # 确定时间范围
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
            print(f'📅 时间序列查询: {start} 到 {end}')
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    elif hours:
        end = datetime.now()
        start = end - timedelta(hours=hours)
        print(f'⏰ 使用小时参数: {hours} 小时')
    else:
        # 默认72小时
        end = datetime.now()
        start = end - timedelta(hours=72)
        print(f'⏰ 使用默认参数: 72 小时')
    
    query = TrafficStatus.query.filter(
        and_(
            TrafficStatus.timestamp >= start,
            TrafficStatus.timestamp <= end
        )
    )
    
    if road_id:
        query = query.filter(TrafficStatus.road_id == road_id)
        road = Road.query.get(road_id)
        if not road:
            return jsonify({'error': '道路不存在'}), 404
    
    # 按日期聚合（如果是日粒度）或按小时聚合
    if aggregation == 'day':
        data_points = db.session.query(
            func.date(TrafficStatus.timestamp).label('date'),
            func.avg(TrafficStatus.congestion_index).label('avg_congestion')
        ).filter(
            and_(
                TrafficStatus.timestamp >= start,
                TrafficStatus.timestamp <= end
            )
        )
        if road_id:
            data_points = data_points.filter(TrafficStatus.road_id == road_id)
        data_points = data_points.group_by('date').order_by('date').all()
        
        result = []
        for point in data_points:
            result.append({
                'timestamp': str(point.date),
                'avg_congestion': round(point.avg_congestion, 2) if point.avg_congestion else 0
            })
    else:
        # 小时粒度
        # SQLite 不支持 date_format，使用 strftime
        if db.engine.name == 'sqlite':
            time_bucket = func.strftime('%Y-%m-%d %H:00:00', TrafficStatus.timestamp)
        else:
            # MySQL
            time_bucket = func.date_format(TrafficStatus.timestamp, '%Y-%m-%d %H:00:00')

        data_points = db.session.query(
            time_bucket.label('time_bucket'),
            func.avg(TrafficStatus.congestion_index).label('avg_congestion')
        ).filter(
            and_(
                TrafficStatus.timestamp >= start,
                TrafficStatus.timestamp <= end
            )
        )
        if road_id:
            data_points = data_points.filter(TrafficStatus.road_id == road_id)
        data_points = data_points.group_by('time_bucket').order_by('time_bucket').all()
        
        result = []
        for point in data_points:
            result.append({
                'timestamp': point.time_bucket,
                'congestion_index': round(point.avg_congestion, 2) if point.avg_congestion else 0
            })
    
    return jsonify({
        'data': result
    }), 200


@analytics_bp.route('/time-series/events', methods=['GET'])
def get_events_time_series():
    """获取交通事件时间序列"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    aggregation = request.args.get('aggregation', 'day')
    
    if not start_date or not end_date:
        return jsonify({'error': '缺少日期参数'}), 400
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        end = end + timedelta(days=1)
    except ValueError:
        return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    
    # 按日期统计事件
    daily_events = db.session.query(
        func.date(TrafficEvent.start_time).label('event_date'),
        func.count(TrafficEvent.id).label('count')
    ).filter(
        and_(
            TrafficEvent.start_time >= start,
            TrafficEvent.start_time < end
        )
    ).group_by('event_date').order_by('event_date').all()
    
    result = []
    for day in daily_events:
        result.append({
            'timestamp': str(day.event_date),
            'count': day.count
        })
    
    return jsonify({
        'data': result
    }), 200


# ============== 对比分析 ==============

@analytics_bp.route('/comparison/road-performance', methods=['GET'])
def compare_road_performance():
    """对比多条道路的性能"""
    hours = request.args.get('hours', 24, type=int)
    road_ids = request.args.getlist('road_ids', type=int)
    
    if not road_ids:
        return jsonify({'error': '请提供要对比的道路ID列表'}), 400
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    result = []
    for road_id in road_ids:
        road = Road.query.get(road_id)
        if not road:
            continue
        
        stats = db.session.query(
            func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
            func.avg(TrafficStatus.speed).label('avg_speed'),
            func.max(TrafficStatus.congestion_index).label('peak_congestion'),
            func.min(TrafficStatus.congestion_index).label('min_congestion'),
            func.count(TrafficStatus.id).label('record_count')
        ).filter(
            and_(
                TrafficStatus.road_id == road_id,
                TrafficStatus.timestamp >= time_threshold
            )
        ).first()
        
        if stats:
            result.append({
                'road': road.to_dict(),
                'avg_congestion': round(stats.avg_congestion, 2),
                'avg_speed': round(stats.avg_speed, 2) if stats.avg_speed else None,
                'peak_congestion': round(stats.peak_congestion, 2),
                'min_congestion': round(stats.min_congestion, 2),
                'record_count': stats.record_count
            })
    
    return jsonify({
        'comparison': result,
        'period_hours': hours,
        'roads_compared': len(result)
    }), 200


@analytics_bp.route('/comparison/by-road-type', methods=['GET'])
def compare_by_road_type():
    """按道路类型对比性能"""
    hours = request.args.get('hours', 24, type=int)
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # 获取所有道路类型
    road_types = db.session.query(Road.road_type.distinct()).all()
    
    result = []
    for (road_type,) in road_types:
        if not road_type:
            continue
        
        # 获取该类型的所有道路
        roads = Road.query.filter_by(road_type=road_type).all()
        road_ids = [r.id for r in roads]
        
        if not road_ids:
            continue
        
        stats = db.session.query(
            func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
            func.avg(TrafficStatus.speed).label('avg_speed'),
            func.count(TrafficStatus.id).label('record_count')
        ).filter(
            and_(
                TrafficStatus.road_id.in_(road_ids),
                TrafficStatus.timestamp >= time_threshold
            )
        ).first()
        
        if stats and stats.record_count > 0:
            result.append({
                'road_type': road_type,
                'roads_count': len(roads),
                'avg_congestion': round(stats.avg_congestion, 2),
                'avg_speed': round(stats.avg_speed, 2) if stats.avg_speed else None,
                'record_count': stats.record_count
            })
    
    return jsonify({
        'by_road_type': result,
        'period_hours': hours
    }), 200


# ============== 事件分析 ==============

@analytics_bp.route('/events/statistics', methods=['GET'])
def get_events_statistics():
    """获取事件统计信息"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    days = request.args.get('days', type=int)
    
    # 确定时间范围
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    elif days:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=30)
    
    # 按事件类型统计
    event_types = db.session.query(
        TrafficEvent.event_type,
        func.count(TrafficEvent.id).label('count'),
        func.sum(
            case(
                (TrafficEvent.severity == '严重', 1),
                else_=0
            )
        ).label('severe_count')
    ).filter(
        and_(
            TrafficEvent.start_time >= start,
            TrafficEvent.start_time < end
        )
    ).group_by(TrafficEvent.event_type).all()
    
    # 按严重程度统计
    severity_stats = db.session.query(
        TrafficEvent.severity,
        func.count(TrafficEvent.id).label('count')
    ).filter(
        and_(
            TrafficEvent.start_time >= start,
            TrafficEvent.start_time < end
        )
    ).group_by(TrafficEvent.severity).all()
    
    # 平均事件处理时间
    resolved_events = db.session.query(
        func.avg(
            func.unix_timestamp(TrafficEvent.end_time) - func.unix_timestamp(TrafficEvent.start_time)
        ).label('avg_duration_seconds')
    ).filter(
        and_(
            TrafficEvent.status == 'resolved',
            TrafficEvent.start_time >= start,
            TrafficEvent.start_time < end,
            TrafficEvent.end_time.isnot(None)
        )
    ).first()
    
    # 当前活跃事件数
    active_events_count = TrafficEvent.query.filter(
        and_(
            TrafficEvent.status == 'active',
            TrafficEvent.start_time >= start,
            TrafficEvent.start_time < end
        )
    ).count()
    
    return jsonify({
        'statistics': {
            'by_type': {
                et.event_type: et.count for et in event_types
            },
            'by_severity': {
                s.severity: s.count for s in severity_stats
            },
            'avg_resolution_time_hours': round(
                (float(resolved_events.avg_duration_seconds) / 3600) 
                if resolved_events and resolved_events.avg_duration_seconds else 0, 
                2
            ),
            'active_events': active_events_count
        }
    }), 200


@analytics_bp.route('/events/impact-analysis', methods=['GET'])
def analyze_event_impact():
    """分析事件对交通的影响"""
    hours = request.args.get('hours', 24, type=int)
    event_id = request.args.get('event_id', type=int)
    
    if not event_id:
        return jsonify({'error': '请提供事件ID'}), 400
    
    event = TrafficEvent.query.get_or_404(event_id)
    
    # 获取事件时间范围内该道路的交通数据
    time_range_before = 2  # 事件前2小时
    time_range_after = 2   # 事件后2小时
    
    before_threshold = event.start_time - timedelta(hours=time_range_before)
    after_threshold = event.end_time + timedelta(hours=time_range_after) if event.end_time else datetime.utcnow() + timedelta(hours=time_range_after)
    
    # 事件前的数据
    before_data = db.session.query(
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed')
    ).filter(
        and_(
            TrafficStatus.road_id == event.road_id,
            TrafficStatus.timestamp >= before_threshold,
            TrafficStatus.timestamp < event.start_time
        )
    ).first()
    
    # 事件期间的数据
    during_data = db.session.query(
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed')
    ).filter(
        and_(
            TrafficStatus.road_id == event.road_id,
            TrafficStatus.timestamp >= event.start_time,
            TrafficStatus.timestamp <= (event.end_time if event.end_time else datetime.utcnow())
        )
    ).first()
    
    # 事件后的数据
    during_end = event.end_time if event.end_time else datetime.utcnow()
    after_data = db.session.query(
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed')
    ).filter(
        and_(
            TrafficStatus.road_id == event.road_id,
            TrafficStatus.timestamp > during_end,
            TrafficStatus.timestamp <= after_threshold
        )
    ).first()
    
    return jsonify({
        'event': event.to_dict(),
        'before_event': {
            'avg_congestion': round(before_data.avg_congestion, 2) if before_data.avg_congestion else None,
            'avg_speed': round(before_data.avg_speed, 2) if before_data.avg_speed else None
        } if before_data else None,
        'during_event': {
            'avg_congestion': round(during_data.avg_congestion, 2) if during_data.avg_congestion else None,
            'avg_speed': round(during_data.avg_speed, 2) if during_data.avg_speed else None
        } if during_data else None,
        'after_event': {
            'avg_congestion': round(after_data.avg_congestion, 2) if after_data.avg_congestion else None,
            'avg_speed': round(after_data.avg_speed, 2) if after_data.avg_speed else None
        } if after_data else None
    }), 200


# ============== 趋势分析 ==============

@analytics_bp.route('/trends/weekly', methods=['GET'])
def analyze_weekly_trends():
    """分析周内的交通趋势"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    weeks = request.args.get('weeks', type=int)
    
    # 确定时间范围
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
            print(f'📅 周趋势查询: {start_date} 到 {end_date}')
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    elif weeks:
        end = datetime.now()
        start = end - timedelta(weeks=weeks)
        print(f'⏰ 周趋势查询: {weeks} 周')
    else:
        end = datetime.now()
        start = end - timedelta(weeks=4)
        print(f'⏰ 周趋势查询: 默认4周')
    
    # 按周几统计 (MySQL 使用 DAYOFWEEK)
    weekly_stats = db.session.query(
        (func.dayofweek(TrafficStatus.timestamp) - 1).label('weekday'),
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed'),
        func.count(TrafficStatus.id).label('record_count')
    ).filter(
        and_(
            TrafficStatus.timestamp >= start,
            TrafficStatus.timestamp <= end
        )
    ).group_by('weekday').all()
    
    print(f'📊 周趋势查询结果: {len(weekly_stats)} 条记录')
    
    weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    
    result = []
    for stat in weekly_stats:
        weekday_idx = int(stat.weekday)
        result.append({
            'weekday': weekday_names[weekday_idx],
            'avg_congestion': round(stat.avg_congestion, 2) if stat.avg_congestion else 0
        })
    
    # 按顺序排列
    result.sort(key=lambda x: weekday_names.index(x['weekday']))
    
    # 记录返回数据
    print(f'✅ 周趋势返回数据: {result}')
    
    return jsonify({
        'data': {
            'data': result,
            'count': len(result)
        }
    }), 200


@analytics_bp.route('/trends/monthly', methods=['GET'])
def analyze_monthly_trends():
    """分析月内的交通趋势"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    months = request.args.get('months', type=int)
    
    # 确定时间范围
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
            print(f'📅 月趋势查询: {start_date} 到 {end_date}')
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    elif months:
        end = datetime.now()
        start = end - timedelta(days=30 * months)
        print(f'⏰ 月趋势查询: {months} 个月')
    else:
        end = datetime.now()
        start = end - timedelta(days=90)
        print(f'⏰ 月趋势查询: 默认90天')
    
    # 按日期统计 (对于日粒度的趋势)
    daily_stats = db.session.query(
        func.date(TrafficStatus.timestamp).label('day'),
        func.avg(TrafficStatus.congestion_index).label('avg_congestion')
    ).filter(
        and_(
            TrafficStatus.timestamp >= start,
            TrafficStatus.timestamp <= end
        )
    ).group_by('day').order_by('day').all()
    
    print(f'📊 月趋势查询结果: {len(daily_stats)} 条记录')
    
    result = []
    for stat in daily_stats:
        result.append({
            'day': str(stat.day),
            'timestamp': str(stat.day),
            'avg_congestion': round(stat.avg_congestion, 2) if stat.avg_congestion else 0
        })
    
    # 记录返回数据
    print(f'✅ 月趋势返回数据: {len(result)} 条记录')
    
    return jsonify({
        'data': {
            'data': result,
            'count': len(result)
        }
    }), 200


# ============== 预测和异常检测 ==============

@analytics_bp.route('/anomalies/detect', methods=['GET'])
def detect_anomalies():
    """检测异常交通数据"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    # 前端传的是 threshold，后端之前用的是 std_threshold，这里做兼容
    std_threshold = request.args.get('threshold', type=float) or request.args.get('std_threshold', 2, type=float)
    
    # 确定时间范围
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end + timedelta(days=1)
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    else:
        hours = request.args.get('hours', 24, type=int)
        end = datetime.now()
        start = end - timedelta(hours=hours)
    
    # 获取平均值和标准差
    
    stats = db.session.query(
        TrafficStatus.road_id,
        func.avg(TrafficStatus.congestion_index).label('mean'),
        func.stddev_pop(TrafficStatus.congestion_index).label('stddev')
    ).filter(
        and_(
            TrafficStatus.timestamp >= start,
            TrafficStatus.timestamp < end
        )
    ).group_by(TrafficStatus.road_id).all()
    
    anomalies = []
    
    for stat in stats:
        if not stat.stddev or stat.stddev == 0:
            continue
        
        # 查找超过阈值的数据点
        outliers = db.session.query(TrafficStatus).filter(
            and_(
                TrafficStatus.road_id == stat.road_id,
                TrafficStatus.timestamp >= start,
                TrafficStatus.timestamp < end,
                or_(
                    TrafficStatus.congestion_index > stat.mean + (std_threshold * stat.stddev),
                    TrafficStatus.congestion_index < stat.mean - (std_threshold * stat.stddev)
                )
            )
        ).order_by(TrafficStatus.timestamp.desc()).limit(20).all()
        
        if outliers:
            road = Road.query.get(stat.road_id)
            road_name = road.name if road else f"Road {stat.road_id}"
            
            for o in outliers:
                anomalies.append({
                    'road_name': road_name,
                    'timestamp': o.timestamp.isoformat(),
                    'status': o.status,
                    'congestion_index': round(o.congestion_index, 2),
                    'speed': round(o.speed, 1) if o.speed else 0,
                    'deviation': round(abs(o.congestion_index - stat.mean), 2)
                })
    
    # 按时间倒序排列
    anomalies.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'anomalies_detected': len(anomalies),
        'std_threshold': std_threshold,
        'anomalies': anomalies
    }), 200


# ============== 综合报告 ==============

@analytics_bp.route('/report/daily-summary', methods=['GET'])
def get_daily_summary():
    """获取每日综合报告"""
    # 支持 date 参数 (YYYY-MM-DD) 或 days_ago 参数
    date_param = request.args.get('date')
    days_ago = request.args.get('days_ago', 0, type=int)  # 0表示今天,1表示昨天
    
    # 计算日期范围
    if date_param:
        try:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            target_date = (datetime.utcnow() - timedelta(days=days_ago)).date()
    else:
        target_date = (datetime.utcnow() - timedelta(days=days_ago)).date()
    
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = start_time + timedelta(days=1)
    
    # 交通状态统计
    status_stats = db.session.query(
        TrafficStatus.status,
        func.count(TrafficStatus.id).label('count')
    ).filter(
        and_(
            TrafficStatus.timestamp >= start_time,
            TrafficStatus.timestamp < end_time
        )
    ).group_by(TrafficStatus.status).all()
    
    # 平均指标
    avg_stats = db.session.query(
        func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
        func.avg(TrafficStatus.speed).label('avg_speed'),
        func.max(TrafficStatus.congestion_index).label('peak_congestion'),
        func.count(TrafficStatus.id).label('total_records')
    ).filter(
        and_(
            TrafficStatus.timestamp >= start_time,
            TrafficStatus.timestamp < end_time
        )
    ).first()
    
    # 事件统计
    events_stats = db.session.query(
        func.count(TrafficEvent.id).label('total_events'),
        func.sum(
            case(
                (TrafficEvent.severity == '严重', 1),
                else_=0
            )
        ).label('severe_events'),
        func.sum(
            case(
                (TrafficEvent.status == 'resolved', 1),
                else_=0
            )
        ).label('resolved_events')
    ).filter(
        and_(
            TrafficEvent.start_time >= start_time,
            TrafficEvent.start_time < end_time
        )
    ).first()
    
    return jsonify({
        'summary': {
            'date': str(target_date),
            'avgCongestion': round(avg_stats.avg_congestion, 2) if avg_stats.avg_congestion else 0,
            'avgSpeed': round(avg_stats.avg_speed, 2) if avg_stats.avg_speed else 0,
            'peakCongestion': round(avg_stats.peak_congestion, 2) if avg_stats.peak_congestion else 0,
            'eventCount': events_stats.total_events or 0,
            'eventResolutionRate': (events_stats.resolved_events / events_stats.total_events) if events_stats.total_events and events_stats.total_events > 0 else 0,
            'statusDistribution': {stat.status: stat.count for stat in status_stats},
            'totalRecords': avg_stats.total_records
        }
    }), 200


@analytics_bp.route('/report/road-performance-card', methods=['GET'])
def get_road_performance_card():
    """获取道路性能卡片(用于仪表盘)"""
    hours = request.args.get('hours', 24, type=int)
    
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # 获取每条道路的最新性能数据
    subquery = db.session.query(
        TrafficStatus.road_id,
        func.max(TrafficStatus.timestamp).label('max_timestamp')
    ).filter(
        TrafficStatus.timestamp >= time_threshold
    ).group_by(TrafficStatus.road_id).subquery()
    
    latest_statuses = db.session.query(TrafficStatus).join(
        subquery,
        db.and_(
            TrafficStatus.road_id == subquery.c.road_id,
            TrafficStatus.timestamp == subquery.c.max_timestamp
        )
    ).all()
    
    result = []
    for status in latest_statuses:
        road = Road.query.get(status.road_id)
        if road:
            # 获取24小时内的历史数据用于趋势
            history = db.session.query(
                func.avg(TrafficStatus.congestion_index).label('avg_congestion')
            ).filter(
                and_(
                    TrafficStatus.road_id == status.road_id,
                    TrafficStatus.timestamp >= time_threshold
                )
            ).first()
            
            result.append({
                'road': road.to_dict(),
                'current_status': status.to_dict(),
                'avg_congestion_24h': round(history.avg_congestion, 2) if history.avg_congestion else 0,
                'trend': 'up' if (history.avg_congestion and history.avg_congestion > status.congestion_index) else 'down'
            })
    
    return jsonify({
        'roads_performance': result,
        'count': len(result),
        'period_hours': hours
    }), 200


# ============== 高影响事件分析 ==============

@analytics_bp.route('/events/high-impact', methods=['GET'])
def get_high_impact_events():
    """获取高影响事件"""
    from utils.analytics_service import EventAnalyticsService
    
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    limit = request.args.get('limit', 10, type=int)
    
    # 计算天数
    days = 30
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 30
        except:
            days = 30
    
    events = EventAnalyticsService.get_high_impact_events(days, limit)
    
    # 扁平化数据结构以适配前端表格
    flat_events = []
    for item in events:
        event_data = item['event']
        event_data['impact_score'] = item['impact_score']
        flat_events.append(event_data)
    
    return jsonify({
        'events': flat_events,
        'period_days': days,
        'total': len(flat_events)
    }), 200
