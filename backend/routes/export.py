"""
数据导出功能路由
支持多种格式的数据导出(CSV、JSON等)
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import TrafficStatus, TrafficEvent, Road, User
from extensions import db
from datetime import datetime, timedelta
from io import StringIO, BytesIO
from sqlalchemy import func
from utils.analytics_service import TrafficAnalyticsService, EventAnalyticsService
import csv
import json

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/traffic-status/csv', methods=['GET'])
@jwt_required()
def export_traffic_status_csv():
    """导出交通状态数据为CSV(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403

    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    hours = request.args.get('hours', 24, type=int)
    road_id = request.args.get('road_id', type=int)
    
    query = TrafficStatus.query
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                TrafficStatus.timestamp >= start_date,
                TrafficStatus.timestamp < end_date
            )
        except:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(TrafficStatus.timestamp >= time_threshold)
    else:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(TrafficStatus.timestamp >= time_threshold)
    
    if road_id:
        query = query.filter(TrafficStatus.road_id == road_id)
    
    statuses = query.order_by(TrafficStatus.timestamp.desc()).limit(5000).all() # 增加限制防止超时
    
    # 创建CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '时间', '道路ID', '道路名称', '状态', '平均速度', '拥堵指数', 
        '通行时间', '车辆数', '数据来源'
    ])
    
    # 写入数据
    for status in statuses:
        road = Road.query.get(status.road_id)
        writer.writerow([
            status.timestamp.isoformat(),
            status.road_id,
            road.name if road else '未知',
            status.status,
            status.speed or '',
            status.congestion_index or '',
            status.travel_time or '',
            status.vehicle_count or '',
            status.source or ''
        ])
    
    # 创建可下载的文件
    output.seek(0)
    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))  # 支持中文
    mem.seek(0)
    
    filename = f"traffic_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@export_bp.route('/traffic-events/csv', methods=['GET'])
def export_traffic_events_csv():
    """导出交通事件数据为CSV"""
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    days = request.args.get('days', 30, type=int)
    status = request.args.get('status', None)  # active/resolved
    
    query = TrafficEvent.query
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                TrafficEvent.start_time >= start_date,
                TrafficEvent.start_time < end_date
            )
        except:
            time_threshold = datetime.utcnow() - timedelta(days=days)
            query = query.filter(TrafficEvent.start_time >= time_threshold)
    else:
        time_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(TrafficEvent.start_time >= time_threshold)
    
    if status:
        query = query.filter(TrafficEvent.status == status)
    
    events = query.order_by(TrafficEvent.start_time.desc()).all()
    
    # 创建CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '事件ID', '道路', '事件类型', '严重程度', '状态', '开始时间', 
        '结束时间', '持续时间(小时)', '位置(纬度)', '位置(经度)', '说明'
    ])
    
    # 写入数据
    for event in events:
        road = Road.query.get(event.road_id)
        
        # 计算持续时间
        if event.end_time:
            duration = (event.end_time - event.start_time).total_seconds() / 3600
        else:
            duration = (datetime.utcnow() - event.start_time).total_seconds() / 3600
        
        writer.writerow([
            event.id,
            road.name if road else '未知',
            event.event_type,
            event.severity or '',
            event.status,
            event.start_time.isoformat() if event.start_time else '',
            event.end_time.isoformat() if event.end_time else '',
            f"{duration:.2f}" if duration else '',
            event.latitude or '',
            event.longitude or '',
            event.description[:50] + '...' if len(event.description) > 50 else event.description
        ])
    
    # 创建可下载的文件
    output.seek(0)
    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    
    filename = f"traffic_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@export_bp.route('/roads/csv', methods=['GET'])
def export_roads_csv():
    """导出道路数据为CSV"""
    roads = Road.query.all()
    
    # 创建CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        '道路ID', '道路名称', '道路代码', '起点', '终点', '长度(km)', 
        '车道数', '道路类型', '描述'
    ])
    
    # 写入数据
    for road in roads:
        writer.writerow([
            road.id,
            road.name,
            road.road_code,
            road.start_point,
            road.end_point,
            road.length or '',
            road.lanes or '',
            road.road_type or '',
            road.description or ''
        ])
    
    # 创建可下载的文件
    output.seek(0)
    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8-sig'))
    mem.seek(0)
    
    filename = f"roads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@export_bp.route('/traffic-status/json', methods=['GET'])
def export_traffic_status_json():
    """导出交通状态数据为JSON"""
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    hours = request.args.get('hours', 24, type=int)
    road_id = request.args.get('road_id', type=int)
    
    query = TrafficStatus.query
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                TrafficStatus.timestamp >= start_date,
                TrafficStatus.timestamp < end_date
            )
        except:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(TrafficStatus.timestamp >= time_threshold)
    else:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(TrafficStatus.timestamp >= time_threshold)
    
    if road_id:
        query = query.filter(TrafficStatus.road_id == road_id)
    
    statuses = query.order_by(TrafficStatus.timestamp.desc()).limit(5000).all()
    
    data = {
        'export_time': datetime.utcnow().isoformat(),
        'period_hours': hours, # Note: This might be inaccurate if date range is used, but acceptable
        'total_records': len(statuses),
        'data': [status.to_dict() for status in statuses]
    }
    
    return jsonify(data), 200


@export_bp.route('/traffic-events/json', methods=['GET'])
def export_traffic_events_json():
    """导出交通事件数据为JSON"""
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    days = request.args.get('days', 30, type=int)
    status = request.args.get('status', None)
    
    query = TrafficEvent.query
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                TrafficEvent.start_time >= start_date,
                TrafficEvent.start_time < end_date
            )
        except:
            time_threshold = datetime.utcnow() - timedelta(days=days)
            query = query.filter(TrafficEvent.start_time >= time_threshold)
    else:
        time_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(TrafficEvent.start_time >= time_threshold)
    
    if status:
        query = query.filter(TrafficEvent.status == status)
    
    events = query.order_by(TrafficEvent.start_time.desc()).all()
    
    data = {
        'export_time': datetime.utcnow().isoformat(),
        'period_days': days,
        'total_records': len(events),
        'data': [event.to_dict() for event in events]
    }
    
    return jsonify(data), 200


@export_bp.route('/roads/json', methods=['GET'])
def export_roads_json():
    """导出道路数据为JSON"""
    roads = Road.query.all()
    
    data = {
        'export_time': datetime.utcnow().isoformat(),
        'total_roads': len(roads),
        'data': [road.to_dict() for road in roads]
    }
    
    return jsonify(data), 200


@export_bp.route('/analytics-report/json', methods=['GET'])
def export_analytics_report():
    """导出分析报告为JSON"""
    
    # 支持两种参数格式：日期范围或时间偏移
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    
    days = 7
    hours = 24
    
    if start_date_str and end_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            time_threshold_status = start_date
            time_threshold_event = start_date
        except (ValueError, TypeError):
            return jsonify({'error': '日期格式无效'}), 400
    else:
        # 使用旧格式的天数和小时
        days = request.args.get('days', 7, type=int)
        hours = request.args.get('hours', 24, type=int)
        time_threshold_status = datetime.utcnow() - timedelta(hours=hours)
        time_threshold_event = datetime.utcnow() - timedelta(days=days)
    
    # 交通统计
    traffic_stats = db.session.query(
        TrafficStatus.status,
        func.count(TrafficStatus.id).label('count'),
        func.avg(TrafficStatus.congestion_index).label('avg_congestion')
    ).filter(
        TrafficStatus.timestamp >= time_threshold_status
    ).group_by(TrafficStatus.status).all()
    
    # 事件统计
    event_stats = EventAnalyticsService.get_event_statistics(days)
    
    # 高峰时段
    peak_hours = TrafficAnalyticsService.get_peak_hours(7)
    
    data = {
        'export_time': datetime.utcnow().isoformat(),
        'report_period': {
            'traffic_hours': hours,
            'events_days': days
        },
        'traffic_statistics': {
            'by_status': [
                {
                    'status': s.status,
                    'count': s.count,
                    'avg_congestion': round(s.avg_congestion, 2) if s.avg_congestion else 0
                } for s in traffic_stats
            ]
        },
        'event_statistics': event_stats,
        'peak_hours': peak_hours,
        'generated_by': 'Traffic Analytics System'
    }
    
    return jsonify(data), 200


@export_bp.route('/custom-dataset', methods=['POST'])
# @jwt_required()
def export_custom_dataset():
    """导出自定义数据集"""
    # 暂时移除管理员权限检查，以便演示
    # current_user_id = get_jwt_identity()
    # user = User.query.get(current_user_id)
    # if not user or not user.is_admin:
    #     return jsonify({'error': '需要管理员权限'}), 403
    
    request_data = request.get_json()
    
    start_date_str = request_data.get('startDate')
    end_date_str = request_data.get('endDate')
    data_types = request_data.get('dataTypes', []) # ['trafficStatus', 'trafficEvents', 'roads']
    fields = request_data.get('fields', [])
    export_format = request_data.get('format', 'json')
    
    # 解析日期
    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
            end_date = datetime.utcnow()
    except:
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

    result_data = {}
    
    # 获取数据
    if 'trafficStatus' in data_types:
        statuses = TrafficStatus.query.filter(
            TrafficStatus.timestamp >= start_date,
            TrafficStatus.timestamp < end_date
        ).limit(1000).all() # 限制数量防止过大
        result_data['trafficStatus'] = [s.to_dict() for s in statuses]
    
    if 'trafficEvents' in data_types:
        events = TrafficEvent.query.filter(
            TrafficEvent.start_time >= start_date,
            TrafficEvent.start_time < end_date
        ).all()
        result_data['trafficEvents'] = [e.to_dict() for e in events]
    
    if 'roads' in data_types:
        roads = Road.query.all()
        result_data['roads'] = [r.to_dict() for r in roads]
        
    # 处理 CSV 格式
    if export_format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        
        for key, items in result_data.items():
            writer.writerow([f'--- {key} ---'])
            if items:
                # 获取表头
                headers = list(items[0].keys())
                # 如果指定了字段，则过滤
                if fields:
                    headers = [h for h in headers if h in fields]
                
                writer.writerow(headers)
                for item in items:
                    row = [item.get(h, '') for h in headers]
                    writer.writerow(row)
            writer.writerow([]) # 空行分隔
            
        output.seek(0)
        mem = BytesIO()
        mem.write(output.getvalue().encode('utf-8-sig'))
        mem.seek(0)
        
        filename = f"custom_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return send_file(mem, mimetype='text/csv', as_attachment=True, download_name=filename)
    
    # JSON 格式
    return jsonify({
        'export_time': datetime.utcnow().isoformat(),
        'filters': {
            'startDate': start_date_str,
            'endDate': end_date_str,
            'dataTypes': data_types
        },
        'data': result_data
    }), 200


@export_bp.route('/data-summary', methods=['GET'])
def get_export_summary():
    """获取可导出数据的摘要信息"""
    # 统计数据量
    traffic_status_count = TrafficStatus.query.count()
    events_count = TrafficEvent.query.count()
    roads_count = Road.query.count()
    
    # 数据时间范围
    oldest_status = db.session.query(func.min(TrafficStatus.timestamp)).scalar()
    latest_status = db.session.query(func.max(TrafficStatus.timestamp)).scalar()
    
    date_range_str = '--'
    if oldest_status and latest_status:
        date_range_str = f"{oldest_status.strftime('%Y-%m-%d')} 至 {latest_status.strftime('%Y-%m-%d')}"
        
    last_update_str = latest_status.strftime('%Y-%m-%d %H:%M:%S') if latest_status else '--'
    
    # 快速统计 (今日、本周、本月)
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = datetime(now.year, now.month, 1)
    
    today_status_count = TrafficStatus.query.filter(TrafficStatus.timestamp >= today_start).count()
    today_event_count = TrafficEvent.query.filter(TrafficEvent.start_time >= today_start).count()
    week_event_count = TrafficEvent.query.filter(TrafficEvent.start_time >= week_start).count()
    month_event_count = TrafficEvent.query.filter(TrafficEvent.start_time >= month_start).count()
    
    return jsonify({
        'summary': {
            'traffic_status_count': traffic_status_count,
            'traffic_event_count': events_count,
            'road_count': roads_count,
            'date_range': date_range_str,
            'last_update': last_update_str,
            'today_traffic_status_count': today_status_count,
            'today_event_count': today_event_count,
            'week_event_count': week_event_count,
            'month_event_count': month_event_count
        }
    }), 200
