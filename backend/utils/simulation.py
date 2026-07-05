import random
from datetime import datetime
from extensions import db
from models import TrafficStatus, Road

def generate_realtime_traffic():
    """生成实时交通数据"""
    roads = Road.query.all()
    statuses = ['畅通', '缓行', '拥堵', '严重拥堵']
    status_weights = [0.5, 0.3, 0.15, 0.05]
    
    new_statuses = []
    
    for road in roads:
        # 根据道路类型调整拥堵概率
        if road.road_type == '快速路':
            weights = [0.7, 0.2, 0.08, 0.02]
        elif road.road_type == '支路':
            weights = [0.4, 0.35, 0.2, 0.05]
        else:
            weights = status_weights
        
        status = random.choices(statuses, weights=weights)[0]
        
        # 根据状态生成合理的速度和拥堵指数
        if status == '畅通':
            speed = random.uniform(40, 60)
            congestion_index = random.uniform(0, 3)
        elif status == '缓行':
            speed = random.uniform(20, 40)
            congestion_index = random.uniform(3, 6)
        elif status == '拥堵':
            speed = random.uniform(10, 20)
            congestion_index = random.uniform(6, 8)
        else:  # 严重拥堵
            speed = random.uniform(0, 10)
            congestion_index = random.uniform(8, 10)
            
        traffic_status = TrafficStatus(
            road_id=road.id,
            status=status,
            speed=round(speed, 1),
            congestion_index=round(congestion_index, 1),
            vehicle_count=random.randint(50, 500),
            timestamp=datetime.now(),
            source='simulation'
        )
        db.session.add(traffic_status)
        new_statuses.append(traffic_status)
        
        # 必须先flush生成ID
        db.session.flush()
        road.current_status_id = traffic_status.id
        
    db.session.commit()
    return new_statuses
