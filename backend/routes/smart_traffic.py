from flask import Blueprint, jsonify, request
from extensions import db
from models import Road, WeatherCondition, TrafficPrediction, MaintenanceSchedule
from datetime import datetime, timedelta
from sqlalchemy import func
import random

smart_bp = Blueprint('smart', __name__, url_prefix='/api/smart')

@smart_bp.route('/weather', methods=['GET'])
def get_weather():
    """获取天气状况列表"""
    # 获取所有道路的最新天气
    # 使用子查询优化
    subquery = db.session.query(
        WeatherCondition.road_id,
        func.max(WeatherCondition.timestamp).label('max_timestamp')
    ).group_by(WeatherCondition.road_id).subquery()
    
    latest_weather = db.session.query(WeatherCondition).join(
        subquery,
        db.and_(
            WeatherCondition.road_id == subquery.c.road_id,
            WeatherCondition.timestamp == subquery.c.max_timestamp
        )
    ).all()
    
    # 如果没有数据，生成一些默认数据
    if not latest_weather:
        roads = Road.query.limit(10).all()
        result = []
        for road in roads:
            w = WeatherCondition(
                road_id=road.id,
                condition='Sunny',
                temperature=25.0,
                visibility=10000,
                precipitation=0,
                wind_speed=10,
                timestamp=datetime.utcnow()
            )
            db.session.add(w)
            result.append(w)
        db.session.commit()
        latest_weather = result
    
    # 转换为前端需要的格式
    data = []
    for w in latest_weather:
        d = w.to_dict()
        # 确保包含城市和道路名称
        d['city'] = '本市' 
        d['road_name'] = w.road.name if w.road else '未知道路'
        data.append(d)
        
    return jsonify(data) # 直接返回列表，匹配前端 weatherList.value = res.data

@smart_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """获取交通预测"""
    road_id = request.args.get('road_id', type=int)
    if not road_id:
        return jsonify({'success': False, 'message': 'Road ID is required'}), 400
        
    # 获取未来24小时的预测
    now = datetime.utcnow()
    predictions = TrafficPrediction.query.filter(
        TrafficPrediction.road_id == road_id,
        TrafficPrediction.predicted_time >= now
    ).order_by(TrafficPrediction.predicted_time).limit(24).all()
    
    if not predictions:
        # 模拟生成预测数据
        predictions = []
        base_congestion = random.uniform(1, 5)
        for i in range(24):
            pred_time = now + timedelta(hours=i)
            # 简单的正弦波模拟高峰期
            hour = pred_time.hour
            peak_factor = 1.0
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                peak_factor = 2.0
            
            congestion = min(10, max(0, base_congestion * peak_factor + random.uniform(-1, 1)))
            speed = max(10, 80 - congestion * 8)
            
            pred = TrafficPrediction(
                road_id=road_id,
                predicted_time=pred_time,
                predicted_congestion=congestion,
                predicted_speed=speed,
                confidence_score=random.uniform(0.8, 0.95)
            )
            db.session.add(pred)
            predictions.append(pred)
        db.session.commit()
    
    # 转换数据并适配前端字段
    result = []
    for p in predictions:
        d = p.to_dict()
        # 前端使用 congestion_level，后端模型是 predicted_congestion
        d['congestion_level'] = d['predicted_congestion']
        result.append(d)
            
    return jsonify(result) # 直接返回列表

@smart_bp.route('/maintenance', methods=['GET'])
def get_maintenance():
    """获取维护计划"""
    road_id = request.args.get('road_id', type=int)
    query = MaintenanceSchedule.query
    if road_id:
        query = query.filter_by(road_id=road_id)
        
    schedules = query.order_by(MaintenanceSchedule.start_time).all()
    return jsonify([s.to_dict() for s in schedules]) # 直接返回列表

@smart_bp.route('/maintenance', methods=['POST'])
def create_maintenance():
    """创建维护计划并评估影响"""
    data = request.json
    road_id = data.get('road_id')
    start_time = datetime.fromisoformat(data.get('start_time').replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data.get('end_time').replace('Z', '+00:00'))
    maintenance_type = data.get('maintenance_type')
    
    # 简单的影响评估逻辑
    duration_hours = (end_time - start_time).total_seconds() / 3600
    is_peak_hour = False
    # 检查是否跨越高峰期 (7-9, 17-19)
    current = start_time
    while current < end_time:
        if 7 <= current.hour <= 9 or 17 <= current.hour <= 19:
            is_peak_hour = True
            break
        current += timedelta(hours=1)
        
    impact_level = 'Low'
    if is_peak_hour:
        impact_level = 'High'
    elif duration_hours > 4:
        impact_level = 'Medium'
        
    schedule = MaintenanceSchedule(
        road_id=road_id,
        start_time=start_time,
        end_time=end_time,
        maintenance_type=maintenance_type,
        impact_level=impact_level,
        description=data.get('description'),
        status='Planned'
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    return jsonify({'success': True, 'data': schedule.to_dict(), 'message': f'Maintenance scheduled with {impact_level} impact'})
