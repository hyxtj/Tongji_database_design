"""
向数据库添加模拟数据（不重置）
运行方式: python add_mock_data.py
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import Road, TrafficStatus, TrafficEvent, WeatherCondition, TrafficPrediction, MaintenanceSchedule

def add_mock_data():
    app = create_app()
    with app.app_context():
        print("🚀 开始添加模拟数据...")
        
        roads = Road.query.all()
        if not roads:
            print("❌ 没有找到道路数据，请先运行 seed_data.py")
            return

        # 1. 添加最新的交通状态
        print("🚗 更新交通状态...")
        for road in roads:
            # 模拟随机变化
            prev_status = road.current_status
            
            # 基础拥堵指数
            base_index = prev_status.congestion_index if prev_status else random.uniform(0, 5)
            # 随机波动
            change = random.uniform(-1.5, 1.5)
            new_index = max(0, min(10, base_index + change))
            
            status_str = TrafficStatus.get_status_from_index(new_index)
            
            # 速度与拥堵指数成反比
            max_speed = 100 if road.road_type == '快速路' else 60
            speed = max(5, max_speed * (1 - new_index/12))
            
            new_status = TrafficStatus(
                road_id=road.id,
                status=status_str,
                speed=round(speed, 1),
                congestion_index=round(new_index, 1),
                travel_time=int(road.length / speed * 3600),
                vehicle_count=int(random.uniform(50, 500)),
                source='simulation',
                timestamp=datetime.utcnow()
            )
            db.session.add(new_status)
            db.session.flush() # 获取ID
            
            # 更新道路当前状态引用
            road.current_status_id = new_status.id
            
        print(f"✅ 更新了 {len(roads)} 条道路的实时状态")

        # 2. 添加随机交通事件
        print("⚠️  生成随机交通事件...")
        event_types = ['事故', '施工', '拥堵', '管制', '积水']
        severities = ['轻微', '一般', '严重']
        
        # 随机选择5-10条道路发生事件
        target_roads = random.sample(roads, random.randint(5, 10))
        new_events = []
        
        for road in target_roads:
            event_type = random.choice(event_types)
            severity = random.choice(severities)
            
            event = TrafficEvent(
                road_id=road.id,
                event_type=event_type,
                description=f"{road.name}发生{event_type}，请注意避让",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=random.uniform(1, 4)),
                severity=severity,
                status='Active',
                latitude=road.latitude_start, # 简化处理，使用起点坐标
                longitude=road.longitude_start
            )
            db.session.add(event)
            new_events.append(event)
            
        print(f"✅ 新增了 {len(new_events)} 条交通事件")

        # 3. 更新天气数据
        print("☁️  更新天气数据...")
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Foggy']
        # 为每条路生成天气（或者只生成一部分）
        for road in roads:
            weather = WeatherCondition(
                road_id=road.id,
                condition=random.choice(conditions),
                temperature=random.uniform(15, 30),
                visibility=random.uniform(2000, 20000),
                precipitation=random.uniform(0, 10) if random.random() > 0.7 else 0,
                wind_speed=random.uniform(0, 20),
                timestamp=datetime.utcnow()
            )
            db.session.add(weather)
        print(f"✅ 更新了 {len(roads)} 条天气记录")

        # 4. 更新预测数据
        print("🔮 更新未来24小时预测...")
        # 清理旧的预测数据（可选，为了防止数据爆炸）
        # db.session.query(TrafficPrediction).delete()
        
        # 为前10条重要道路生成预测
        important_roads = roads[:10]
        for road in important_roads:
            base_congestion = road.current_status.congestion_index if road.current_status else 2.0
            
            for i in range(24):
                pred_time = datetime.utcnow() + timedelta(hours=i+1)
                hour = pred_time.hour
                
                # 模拟早晚高峰
                peak_factor = 1.0
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    peak_factor = 1.8
                
                congestion = min(10, max(0, base_congestion * peak_factor + random.uniform(-1, 1)))
                speed = max(10, 60 - congestion * 5)
                
                pred = TrafficPrediction(
                    road_id=road.id,
                    predicted_time=pred_time,
                    predicted_congestion=round(congestion, 1),
                    predicted_speed=round(speed, 1),
                    confidence_score=random.uniform(0.8, 0.99)
                )
                db.session.add(pred)
        print(f"✅ 更新了 {len(important_roads) * 24} 条预测记录")

        db.session.commit()
        print("🎉 所有模拟数据添加完成！")

if __name__ == '__main__':
    add_mock_data()
