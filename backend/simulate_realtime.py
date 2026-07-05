import time
import random
import sys
import requests
from datetime import datetime, timedelta

# 添加当前目录到 sys.path
sys.path.append('.')

from app import create_app
from extensions import db
from models import Road, TrafficStatus, TrafficEvent, WeatherCondition, TrafficPrediction, MaintenanceSchedule

def simulate_realtime_data():
    """
    模拟实时数据生成
    每隔一段时间生成新的交通状态、事件、天气、预测和维护数据
    """
    app = create_app()
    
    print("🚀 启动全量实时交通模拟器...")
    print("   - 包含: 交通状态, 交通事件, 天气状况, 交通预测, 维护计划")
    print("按 Ctrl+C 停止模拟")
    print("-" * 50)

    # 简单的内存缓存，用于保持天气连续性
    weather_cache = {} 

    with app.app_context():
        while True:
            try:
                current_time = datetime.now()
                print(f"\n[{current_time.strftime('%H:%M:%S')}] 正在生成新数据...")
                
                roads = Road.query.all()
                if not roads:
                    print("❌ 未找到道路数据，请先运行 regenerate_data.py")
                    return

                # ==========================================
                # 1. 更新所有道路的交通状态 (TrafficStatus)
                # ==========================================
                new_statuses = []
                for road in roads:
                    # 获取该道路最近的状态作为基础
                    last_status = TrafficStatus.query.filter_by(road_id=road.id)\
                        .order_by(TrafficStatus.timestamp.desc()).first()
                    
                    if last_status:
                        base_congestion = last_status.congestion_index
                        base_speed = last_status.speed
                    else:
                        base_congestion = random.uniform(0, 5)
                        base_speed = 40
                    
                    # 模拟随机波动
                    change = random.uniform(-0.5, 0.5)
                    
                    # 模拟突发拥堵/消散
                    if random.random() < 0.05: change += random.uniform(1.0, 3.0)
                    if random.random() < 0.05: change -= random.uniform(1.0, 3.0)
                        
                    new_congestion = max(0, min(10, base_congestion + change))
                    
                    # 计算速度
                    max_speed = 100 if road.road_type == '快速路' else 60
                    new_speed = max(5, max_speed * (1 - new_congestion/12))
                    new_speed += random.uniform(-2, 2)
                    new_speed = max(0, min(max_speed * 1.2, new_speed))
                    
                    status_label = TrafficStatus.get_status_from_index(new_congestion)
                    
                    new_status = TrafficStatus(
                        road_id=road.id,
                        status=status_label,
                        speed=round(new_speed, 1),
                        congestion_index=round(new_congestion, 1),
                        vehicle_count=random.randint(10, 200),
                        timestamp=current_time
                    )
                    new_statuses.append(new_status)
                    
                    # 关键修复：更新 Road 表的 current_status_id
                    # 需要先 flush 以获取 new_status.id
                    db.session.add(new_status)
                    db.session.flush()
                    road.current_status_id = new_status.id
                    db.session.add(road)
                
                # db.session.add_all(new_statuses) # 已经在上面 add 过了
                print(f"✨ [状态] 更新 {len(new_statuses)} 条道路状态")

                # ==========================================
                # 2. 更新天气状况 (WeatherCondition)
                # ==========================================
                new_weathers = []
                weather_types = ['Sunny', 'Cloudy', 'Rainy', 'Foggy']
                
                for road in roads:
                    # 获取或初始化缓存的天气
                    if road.id not in weather_cache:
                        weather_cache[road.id] = {
                            'condition': random.choice(weather_types),
                            'temperature': random.uniform(20, 30),
                            'visibility': 10000,
                            'wind_speed': random.uniform(0, 10)
                        }
                    
                    w = weather_cache[road.id]
                    
                    # 天气渐变逻辑
                    # 1% 概率改变天气状况
                    if random.random() < 0.01:
                        w['condition'] = random.choice(weather_types)
                    
                    # 温度微调
                    w['temperature'] += random.uniform(-0.2, 0.2)
                    
                    # 根据天气状况调整参数
                    precipitation = 0
                    if w['condition'] == 'Rainy':
                        w['visibility'] = random.uniform(2000, 5000)
                        precipitation = random.uniform(1, 10)
                    elif w['condition'] == 'Foggy':
                        w['visibility'] = random.uniform(100, 1000)
                    else:
                        w['visibility'] = 10000
                    
                    w['wind_speed'] = max(0, w['wind_speed'] + random.uniform(-1, 1))

                    new_weather = WeatherCondition(
                        road_id=road.id,
                        condition=w['condition'],
                        temperature=round(w['temperature'], 1),
                        visibility=round(w['visibility'], 0),
                        precipitation=round(precipitation, 1),
                        wind_speed=round(w['wind_speed'], 1),
                        timestamp=current_time
                    )
                    new_weathers.append(new_weather)
                
                db.session.add_all(new_weathers)
                print(f"☁️  [天气] 更新 {len(new_weathers)} 条天气记录")

                # ==========================================
                # 3. 生成交通预测 (TrafficPrediction)
                # ==========================================
                # 每轮只为随机 5 条道路生成新的预测，避免数据量过大
                target_roads = random.sample(roads, k=min(5, len(roads)))
                new_predictions = []
                for road in target_roads:
                    # 预测未来 1 小时的状态
                    pred_time = current_time + timedelta(hours=1)
                    
                    # 简单预测逻辑：基于当前状态回归均值
                    current_status = next((s for s in new_statuses if s.road_id == road.id), None)
                    current_cong = current_status.congestion_index if current_status else 5.0
                    
                    # 预测值 = 当前值 * 0.7 + 均值(5.0) * 0.3 + 随机波动
                    pred_cong = current_cong * 0.7 + 1.5 + random.uniform(-1, 1)
                    pred_cong = max(0, min(10, pred_cong))
                    
                    pred_speed = max(10, (100 if road.road_type == '快速路' else 60) * (1 - pred_cong/12))
                    
                    pred = TrafficPrediction(
                        road_id=road.id,
                        predicted_time=pred_time,
                        predicted_congestion=round(pred_cong, 2),
                        predicted_speed=round(pred_speed, 1),
                        confidence_score=round(random.uniform(0.7, 0.95), 2)
                    )
                    new_predictions.append(pred)
                
                db.session.add_all(new_predictions)
                print(f"🔮 [预测] 生成 {len(new_predictions)} 条未来预测")

                # ==========================================
                # 4. 交通事件管理 (TrafficEvent)
                # ==========================================
                # 随机生成新事件 (10%概率)
                if random.random() < 0.1:
                    road = random.choice(roads)
                    event_types = ['事故', '故障', '拥堵', '施工', '积水']
                    event_type = random.choice(event_types)
                    
                    event = TrafficEvent(
                        road_id=road.id,
                        event_type=event_type,
                        description=f"实时监测: {road.name} 出现 {event_type}",
                        severity=random.choice(['低', '中', '高']),
                        status='active',
                        start_time=current_time
                    )
                    db.session.add(event)
                    print(f"⚠️  [事件] 新增: {road.name} - {event_type}")
                
                # 随机解决旧事件 (20%概率)
                active_events = TrafficEvent.query.filter_by(status='active').all()
                if active_events and random.random() < 0.2:
                    event_to_resolve = random.choice(active_events)
                    event_to_resolve.status = 'resolved'
                    event_to_resolve.end_time = current_time
                    print(f"✅ [事件] 解决: {event_to_resolve.description}")

                # ==========================================
                # 5. 维护计划更新 (MaintenanceSchedule)
                # ==========================================
                # 极低概率 (1%) 生成新的维护计划
                if random.random() < 0.01:
                    road = random.choice(roads)
                    m_types = ['紧急抢修', '路面清理', '设施维护']
                    m_type = random.choice(m_types)
                    
                    start = current_time + timedelta(hours=random.randint(1, 24))
                    end = start + timedelta(hours=random.randint(2, 8))
                    
                    schedule = MaintenanceSchedule(
                        road_id=road.id,
                        start_time=start,
                        end_time=end,
                        maintenance_type=m_type,
                        impact_level=random.choice(['Low', 'Medium']),
                        status='Planned',
                        description=f"计划任务: {road.name} {m_type}"
                    )
                    db.session.add(schedule)
                    print(f"🛠️  [维护] 新增计划: {road.name} - {m_type}")

                # 提交所有更改
                db.session.commit()
                
                # 通知后端推送更新
                try:
                    requests.post(
                        'http://localhost:5000/api/internal/notify-update',
                        json={'timestamp': current_time.isoformat(), 'type': 'full_update'},
                        headers={'X-Internal-Secret': 'traffic-sim-secret'},
                        timeout=2
                    )
                    print("📡 已通知前端更新数据")
                except Exception as req_err:
                    print(f"⚠️ 通知前端失败 (后端可能未启动): {req_err}")

                # 等待
                sleep_time = 5  # 加快模拟频率以展示实时效果
                print(f"⏳ 等待 {sleep_time} 秒...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print("\n🛑 模拟已停止")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                db.session.rollback()
                time.sleep(5)

if __name__ == '__main__':
    simulate_realtime_data()
