"""
添加测试数据到数据库
运行方式: uv run python seed_data.py
"""
from app import create_app
from models import Road, TrafficStatus, TrafficEvent, WeatherCondition, TrafficPrediction, MaintenanceSchedule
from extensions import db
from datetime import datetime, timedelta
import random


def seed_roads():
    """添加道路数据 - 使用真实上海道路名称"""
    
    # 上海大致坐标范围
    SH_LAT_MIN, SH_LAT_MAX = 31.10, 31.30
    SH_LNG_MIN, SH_LNG_MAX = 121.30, 121.60
    
    def get_random_coords():
        lat1 = random.uniform(SH_LAT_MIN, SH_LAT_MAX)
        lng1 = random.uniform(SH_LNG_MIN, SH_LNG_MAX)
        # 终点在起点附近 (0.01 - 0.05 度)
        lat2 = lat1 + random.uniform(-0.05, 0.05)
        lng2 = lng1 + random.uniform(-0.05, 0.05)
        return lat1, lng1, lat2, lng2

    roads_data = [
        # 快速路/高架
        {'name': '延安高架路', 'road_type': '快速路', 'road_code': 'YAGJ001', 'start_point': '外滩', 'end_point': '虹桥机场', 'length': 15.0, 'lanes': 6, 'description': '上海东西向交通大动脉'},
        {'name': '南北高架路', 'road_type': '快速路', 'road_code': 'NBGJ001', 'start_point': '卢浦大桥', 'end_point': '蕴川路', 'length': 18.5, 'lanes': 6, 'description': '上海南北向交通大动脉'},
        {'name': '内环高架路', 'road_type': '快速路', 'road_code': 'NHGJ001', 'start_point': '南浦大桥', 'end_point': '杨浦大桥', 'length': 47.7, 'lanes': 8, 'description': '上海中心城区环线'},
        {'name': '中环路', 'road_type': '快速路', 'road_code': 'ZHL001', 'start_point': '军工路隧道', 'end_point': '翔殷路隧道', 'length': 70.0, 'lanes': 8, 'description': '上海城市快速路网骨干'},
        {'name': '外环高速', 'road_type': '快速路', 'road_code': 'S20', 'start_point': '外环隧道', 'end_point': '徐浦大桥', 'length': 99.0, 'lanes': 8, 'description': '环绕上海中心城区的快速干道'},
        
        # 浦西主干道
        {'name': '南京东路', 'road_type': '主干道', 'road_code': 'NJD001', 'start_point': '外滩', 'end_point': '西藏中路', 'length': 1.6, 'lanes': 4, 'description': '中华商业第一街'},
        {'name': '南京西路', 'road_type': '主干道', 'road_code': 'NJX001', 'start_point': '西藏中路', 'end_point': '延安西路', 'length': 3.0, 'lanes': 6, 'description': '著名商业商务街'},
        {'name': '淮海中路', 'road_type': '主干道', 'road_code': 'HHZ001', 'start_point': '西藏南路', 'end_point': '华山路', 'length': 5.5, 'lanes': 4, 'description': '高雅时尚的商业街'},
        {'name': '西藏中路', 'road_type': '主干道', 'road_code': 'XZZ001', 'start_point': '延安东路', 'end_point': '南苏州路', 'length': 1.3, 'lanes': 6, 'description': '市中心南北向重要干道'},
        {'name': '四川北路', 'road_type': '主干道', 'road_code': 'SCB001', 'start_point': '四川路桥', 'end_point': '鲁迅公园', 'length': 3.7, 'lanes': 4, 'description': '传统商业街区'},
        {'name': '衡山路', 'road_type': '主干道', 'road_code': 'HSL001', 'start_point': '桃江路', 'end_point': '徐家汇', 'length': 2.3, 'lanes': 4, 'description': '著名的酒吧休闲街'},
        {'name': '肇嘉浜路', 'road_type': '主干道', 'road_code': 'ZJB001', 'start_point': '瑞金二路', 'end_point': '徐家汇', 'length': 3.0, 'lanes': 8, 'description': '徐汇区东西向主干道'},
        {'name': '漕溪北路', 'road_type': '主干道', 'road_code': 'CXB001', 'start_point': '徐家汇', 'end_point': '中山西路', 'length': 1.5, 'lanes': 8, 'description': '连接徐家汇与上海体育馆'},
        {'name': '长寿路', 'road_type': '主干道', 'road_code': 'CSL001', 'start_point': '长寿路桥', 'end_point': '曹家渡', 'length': 2.8, 'lanes': 6, 'description': '普陀区主要商业街'},
        {'name': '共和新路', 'road_type': '主干道', 'road_code': 'GHX001', 'start_point': '天目中路', 'end_point': '蕴川路', 'length': 12.0, 'lanes': 8, 'description': '闸北南北向交通大动脉'},
        
        # 浦东主干道
        {'name': '世纪大道', 'road_type': '主干道', 'road_code': 'SJDD001', 'start_point': '陆家嘴', 'end_point': '世纪公园', 'length': 5.0, 'lanes': 10, 'description': '浦东新区标志性景观大道'},
        {'name': '张杨路', 'road_type': '主干道', 'road_code': 'ZYL001', 'start_point': '复兴东路隧道', 'end_point': '金桥路', 'length': 8.5, 'lanes': 6, 'description': '浦东繁华商业街'},
        {'name': '东方路', 'road_type': '主干道', 'road_code': 'DFL001', 'start_point': '浦东大道', 'end_point': '浦东南路', 'length': 6.2, 'lanes': 6, 'description': '连接陆家嘴与世博园区'},
        {'name': '杨高南路', 'road_type': '主干道', 'road_code': 'YGN001', 'start_point': '世纪大道', 'end_point': '林海公路', 'length': 10.5, 'lanes': 8, 'description': '浦东南北向重要通道'},
        {'name': '罗山路', 'road_type': '主干道', 'road_code': 'LSL001', 'start_point': '杨浦大桥', 'end_point': 'S20外环', 'length': 11.0, 'lanes': 8, 'description': '连接杨浦大桥与浦东机场'},
        
        # 次干道/支路
        {'name': '武康路', 'road_type': '次干道', 'road_code': 'WKL001', 'start_point': '华山路', 'end_point': '淮海中路', 'length': 1.2, 'lanes': 2, 'description': '历史文化名街'},
        {'name': '甜爱路', 'road_type': '支路', 'road_code': 'TAL001', 'start_point': '四川北路', 'end_point': '甜爱支路', 'length': 0.5, 'lanes': 2, 'description': '著名的爱情之路'},
        {'name': '多伦路', 'road_type': '支路', 'road_code': 'DLL001', 'start_point': '四川北路', 'end_point': '四川北路', 'length': 0.6, 'lanes': 2, 'description': '文化名人街'},
        {'name': '大学路', 'road_type': '次干道', 'road_code': 'DXL001', 'start_point': '智星路', 'end_point': '国定路', 'length': 0.8, 'lanes': 2, 'description': '创智天地核心街区'},
        {'name': '愚园路', 'road_type': '次干道', 'road_code': 'YYL001', 'start_point': '常德路', 'end_point': '定西路', 'length': 2.5, 'lanes': 2, 'description': '拥有众多历史建筑的街道'},
    ]

    # 补充更多上海道路名称以达到数量要求
    shanghai_roads = [
        '福州路', '广东路', '汉口路', '九江路', '北京东路', '北京西路', '延安东路', '延安西路',
        '黄陂南路', '黄陂北路', '马当路', '淡水路', '重庆南路', '重庆北路', '成都南路', '成都北路',
        '瑞金一路', '瑞金二路', '石门一路', '石门二路', '陕西南路', '陕西北路', '常熟路', '乌鲁木齐路',
        '华山路', '江苏路', '万航渡路', '愚园路', '长宁路', '虹桥路', '古北路', '天山路', '仙霞路',
        '吴中路', '漕宝路', '宜山路', '虹梅路', '莲花路', '合川路', '金汇路', '龙柏路', '紫藤路',
        '浦东大道', '浦东南路', '陆家嘴环路', '银城中路', '金茂大厦', '滨江大道', '世博大道', '耀华路',
        '成山路', '德州路', '上南路', '云台路', '东明路', '邹平路', '昌里路', '齐河路', '高科西路',
        '龙阳路', '芳甸路', '花木路', '锦绣路', '前程路', '北海路', '云南路', '西藏路', '浙江路',
        '福建路', '山东路', '山西路', '河南路', '江西路', '四川路', '中山路'
    ]
    
    road_types = ['主干道', '次干道', '支路']
    
    existing_names = set(r['name'] for r in roads_data)
    
    count = len(roads_data)
    sh_road_index = 0
    
    while count < 80 and sh_road_index < len(shanghai_roads):
        name = shanghai_roads[sh_road_index]
        sh_road_index += 1
        
        if name in existing_names:
            continue
            
        existing_names.add(name)
        
        # 随机分配类型
        rand_val = random.random()
        if rand_val > 0.7:
            road_type = '主干道'
            lanes = random.choice([4, 6])
            length = random.uniform(3, 10)
        elif rand_val > 0.3:
            road_type = '次干道'
            lanes = 4
            length = random.uniform(1, 5)
        else:
            road_type = '支路'
            lanes = 2
            length = random.uniform(0.5, 2)
            
        roads_data.append({
            'name': name,
            'road_type': road_type,
            'road_code': f"SH{count+1:03d}",
            'start_point': f"路口A-{count}",
            'end_point': f"路口B-{count}",
            'length': round(length, 1),
            'lanes': lanes,
            'description': f"上海市{name}"
        })
        count += 1
    
    roads = []
    for data in roads_data:
        # 为每条道路生成坐标
        lat1, lng1, lat2, lng2 = get_random_coords()
        data['latitude_start'] = lat1
        data['longitude_start'] = lng1
        data['latitude_end'] = lat2
        data['longitude_end'] = lng2
        
        road = Road(**data)
        roads.append(road)
    
    db.session.add_all(roads)
    db.session.commit()
    
    return roads


def seed_traffic_status(roads, days=60):
    """添加交通状态数据"""
    statuses = ['畅通', '缓行', '拥堵', '严重拥堵']
    status_weights = [0.5, 0.3, 0.15, 0.05]  # 概率权重
    
    traffic_statuses = []
    latest_status_map = {}
    
    # 为每条道路生成最新状态
    for road in roads:
        # 根据道路类型调整拥堵概率
        if road.road_type == '快速路':
            weights = [0.7, 0.2, 0.08, 0.02]  # 快速路更畅通
        elif road.road_type == '支路':
            weights = [0.4, 0.35, 0.2, 0.05]  # 支路更容易拥堵
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
            timestamp=datetime.now()
        )
        traffic_statuses.append(traffic_status)
        latest_status_map[road.id] = traffic_status
        
        # 为所有道路添加历史数据
        print(f'生成 {road.name} 的历史数据({days}天)...')
        for days_ago in range(1, days + 1):
            for hour_of_day in range(0, 24):  # 每天24小时
                # 模拟早晚高峰
                is_peak = (7 <= hour_of_day <= 9) or (17 <= hour_of_day <= 19)
                
                current_weights = weights
                if is_peak:
                    # 高峰期更容易拥堵
                    if road.road_type in ['主干道', '快速路']:
                         current_weights = [0.2, 0.3, 0.3, 0.2]
                    else:
                         current_weights = [0.3, 0.4, 0.2, 0.1]
                
                status = random.choices(statuses, weights=current_weights)[0]
                
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

                historical_status = TrafficStatus(
                    road_id=road.id,
                    status=status,
                    speed=round(speed, 1),
                    congestion_index=round(congestion_index, 1),
                    vehicle_count=random.randint(50, 500),
                    timestamp=datetime.now() - timedelta(days=days_ago, hours=hour_of_day)
                )
                traffic_statuses.append(historical_status)
    
    db.session.add_all(traffic_statuses)
    db.session.commit()
    
    # 更新道路的最新状态ID
    print('正在更新道路最新状态关联...')
    for road in roads:
        if road.id in latest_status_map:
            road.current_status_id = latest_status_map[road.id].id
            db.session.add(road)
    db.session.commit()

    print(f'✅ 已添加 {len(traffic_statuses)} 条交通状态记录')
    
    return traffic_statuses


def seed_events(roads):
    """添加交通事件数据"""
    event_types = ['事故', '故障', '施工', '交通管制', '积水', '障碍物', '恶劣天气', '其他']
    severities = ['低', '中', '高']
    statuses = ['active', 'processing', 'resolved']
    
    events = []
    
    # 生成一些活跃事件
    active_event_count = random.randint(15, 30)
    for _ in range(active_event_count):
        road = random.choice(roads)
        event_type = random.choice(event_types)
        
        # 根据事件类型生成合适的描述
        descriptions = {
            '事故': [
                '两车追尾事故,占用一条车道',
                '轻微碰擦事故,车辆已移至路边',
                '多车连环相撞,交警正在处理',
                '车辆故障抛锚,影响通行'
            ],
            '故障': [
                '车辆故障抛锚,占用一条车道',
                '公交车故障,乘客已疏散',
                '货车爆胎,等待救援',
                '车辆自燃,消防已到场'
            ],
            '施工': [
                '道路维修施工,占用两条车道',
                '地铁施工围挡,请绕行',
                '路面坑洞修复中',
                '排水管道维护,单向通行'
            ],
            '交通管制': [
                '大型活动,临时交通管制',
                'VIP车队通行,暂时封闭',
                '马拉松赛事,道路封闭',
                '消防演练,临时管制'
            ],
            '积水': [
                '低洼路段积水严重,车辆无法通行',
                '暴雨导致路面积水,请绕行',
                '排水不畅,路面有少量积水',
                '涵洞积水,已设置警示标志'
            ],
            '障碍物': [
                '路面有散落货物,正在清理',
                '大型石块掉落路面,影响通行',
                '路面有遗撒物,请注意避让',
                '倒塌广告牌占用车道'
            ],
            '恶劣天气': [
                '大雨导致路面积水',
                '大雾影响能见度,请谨慎驾驶',
                '路面结冰,车辆缓行',
                '暴雨预警,建议延迟出行'
            ],
            '其他': [
                '路边停车占道',
                '井盖丢失,已设置警示标志',
                '树木倒伏,正在清理',
                '路灯损坏,夜间请注意安全'
            ]
        }
        
        description = random.choice(descriptions[event_type])
        
        # 事故和恶劣天气通常严重度较高
        if event_type in ['事故', '恶劣天气']:
            severity = random.choices(severities, weights=[0.2, 0.5, 0.3])[0]
        else:
            severity = random.choices(severities, weights=[0.5, 0.3, 0.2])[0]
        
        # 大部分事件是进行中
        status = random.choices(statuses, weights=[0.7, 0.2, 0.1])[0]
        
        # 计算开始时间(最近24小时内)
        hours_ago = random.uniform(0, 24)
        start_time = datetime.now() - timedelta(hours=hours_ago)
        
        # 如果已解决,设置结束时间
        end_time = None
        if status == 'resolved':
            end_time = start_time + timedelta(hours=random.uniform(0.5, 6))
        
        event = TrafficEvent(
            road_id=road.id,
            event_type=event_type,
            description=description,
            severity=severity,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
        events.append(event)
    
    # 生成一些历史事件(已解决)
    historical_event_count = random.randint(100, 200)
    for _ in range(historical_event_count):
        road = random.choice(roads)
        event_type = random.choice(event_types)
        
        # 改为生成最近60天的历史事件
        days_ago = random.uniform(1, 60)
        start_time = datetime.now() - timedelta(days=days_ago)
        end_time = start_time + timedelta(hours=random.uniform(1, 12))
        
        event = TrafficEvent(
            road_id=road.id,
            event_type=event_type,
            description=random.choice(descriptions[event_type]),
            severity=random.choice(severities),
            status='resolved',
            start_time=start_time,
            end_time=end_time
        )
        events.append(event)
    
    # 额外生成更多历史事件(确保数据足够丰富)
    for _ in range(500):  # 添加500条额外的事件
        road = random.choice(roads)
        event_type = random.choice(event_types)
        
        # 生成时间跨度更广的事件
        days_ago = random.uniform(0.1, 60)
        start_time = datetime.now() - timedelta(days=days_ago)
        end_time = start_time + timedelta(hours=random.uniform(1, 12))
        
        event = TrafficEvent(
            road_id=road.id,
            event_type=event_type,
            description=random.choice(descriptions[event_type]),
            severity=random.choice(severities),
            status='resolved',
            start_time=start_time,
            end_time=end_time
        )
        events.append(event)
    
    db.session.add_all(events)
    db.session.commit()
    
    return events


def seed_weather(roads):
    """添加天气数据"""
    conditions = ['Sunny', 'Rainy', 'Foggy', 'Cloudy', 'Snowy']
    weather_data = []
    
    # 为每条道路生成当前天气
    for road in roads:
        condition = random.choice(conditions)
        temp = random.uniform(15, 30)
        if condition == 'Rainy':
            temp -= 5
            precip = random.uniform(1, 10)
            vis = random.uniform(2000, 8000)
        elif condition == 'Foggy':
            temp -= 2
            precip = 0
            vis = random.uniform(100, 1000)
        else:
            precip = 0
            vis = 10000
            
        weather = WeatherCondition(
            road_id=road.id,
            condition=condition,
            temperature=round(temp, 1),
            visibility=round(vis, 0),
            precipitation=round(precip, 1),
            wind_speed=round(random.uniform(0, 20), 1),
            timestamp=datetime.utcnow()
        )
        weather_data.append(weather)
        
    db.session.add_all(weather_data)
    db.session.commit()
    return weather_data


def seed_predictions(roads):
    """添加预测数据"""
    predictions = []
    now = datetime.utcnow()
    
    for road in roads:
        # 生成未来24小时的预测
        base_congestion = random.uniform(1, 5)
        for i in range(24):
            pred_time = now + timedelta(hours=i)
            hour = pred_time.hour
            
            # 模拟早晚高峰
            peak_factor = 1.0
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                peak_factor = 1.8
            
            congestion = min(10, max(0, base_congestion * peak_factor + random.uniform(-1, 1)))
            speed = max(10, 80 - congestion * 8)
            
            pred = TrafficPrediction(
                road_id=road.id,
                predicted_time=pred_time,
                predicted_congestion=round(congestion, 2),
                predicted_speed=round(speed, 1),
                confidence_score=round(random.uniform(0.8, 0.98), 2)
            )
            predictions.append(pred)
            
    db.session.add_all(predictions)
    db.session.commit()
    return predictions


def seed_maintenance(roads):
    """添加维护计划"""
    schedules = []
    types = ['路面重铺', '标线刷新', '绿化修剪', '路灯维修', '排水清理']
    
    # 随机选择几条路进行维护
    target_roads = random.sample(roads, k=min(5, len(roads)))
    
    for road in target_roads:
        start_time = datetime.utcnow() + timedelta(days=random.randint(1, 7))
        duration = random.randint(4, 48)
        end_time = start_time + timedelta(hours=duration)
        
        m_type = random.choice(types)
        impact = 'Low'
        if duration > 24:
            impact = 'High'
        elif duration > 8:
            impact = 'Medium'
            
        schedule = MaintenanceSchedule(
            road_id=road.id,
            start_time=start_time,
            end_time=end_time,
            maintenance_type=m_type,
            impact_level=impact,
            status='Planned',
            description=f'计划对 {road.name} 进行 {m_type} 作业'
        )
        schedules.append(schedule)
        
    db.session.add_all(schedules)
    db.session.commit()
    return schedules


def seed_all():
    """添加所有测试数据"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("🌱 开始添加测试数据")
        print("="*50 + "\n")
        
        # 检查是否已有数据
        existing_roads = Road.query.count()
        if existing_roads > 0:
            print(f"⚠️  数据库已有 {existing_roads} 条道路记录")
            response = input("是否清空现有数据并重新添加? (y/N): ").strip().lower()
            
            if response == 'y':
                print("\n🗑️  正在清空数据...")
                TrafficEvent.query.delete()
                TrafficStatus.query.delete()
                Road.query.delete()
                db.session.commit()
                print("✅ 数据已清空\n")
            else:
                print("❌ 已取消操作")
                return
        
        # 添加道路
        print("📍 正在添加道路数据...")
        roads = seed_roads()
        print(f"✅ 已添加 {len(roads)} 条道路\n")
        
        # 添加交通状态
        print("🚦 正在添加交通状态数据...")
        traffic_statuses = seed_traffic_status(roads)
        print(f"✅ 已添加 {len(traffic_statuses)} 条交通状态记录\n")
        
        # 添加事件
        print("⚠️  正在添加交通事件数据...")
        events = seed_events(roads)
        print(f"✅ 已添加 {len(events)} 条交通事件\n")
        
        # 添加天气数据
        print("☁️  正在添加天气数据...")
        weather_data = seed_weather(roads)
        print(f"✅ 已添加 {len(weather_data)} 条天气记录\n")
        
        # 添加预测数据
        print("🔮 正在添加交通预测数据...")
        predictions = seed_predictions(roads)
        print(f"✅ 已添加 {len(predictions)} 条预测记录\n")
        
        # 添加维护计划
        print("🛠️  正在添加维护计划...")
        maintenance_schedules = seed_maintenance(roads)
        print(f"✅ 已添加 {len(maintenance_schedules)} 条维护计划\n")
        
        # 添加智能交通数据
        print("🧠 正在添加智能交通数据(天气/预测/维护)...")
        seed_weather(roads)
        seed_predictions(roads)
        seed_maintenance(roads)
        print("✅ 智能交通数据添加完成\n")
        
        # 统计
        print("="*50)
        print("📊 数据统计")
        print("="*50)
        print(f"道路总数: {Road.query.count()}")
        print(f"  - 快速路: {Road.query.filter_by(road_type='快速路').count()}")
        print(f"  - 主干道: {Road.query.filter_by(road_type='主干道').count()}")
        print(f"  - 次干道: {Road.query.filter_by(road_type='次干道').count()}")
        print(f"  - 支路: {Road.query.filter_by(road_type='支路').count()}")
        print(f"\n交通状态记录: {TrafficStatus.query.count()}")
        
        # 最新状态统计
        latest_statuses = db.session.query(
            TrafficStatus.status,
            db.func.count(TrafficStatus.id)
        ).join(Road).group_by(TrafficStatus.status).all()
        
        print(f"\n当前路况分布:")
        for status, count in latest_statuses:
            print(f"  - {status}: {count}")
        
        print(f"\n交通事件总数: {TrafficEvent.query.count()}")
        active_events = TrafficEvent.query.filter_by(status='active').count()
        print(f"  - 进行中: {active_events}")
        print(f"  - 处理中: {TrafficEvent.query.filter_by(status='processing').count()}")
        print(f"  - 已解决: {TrafficEvent.query.filter_by(status='resolved').count()}")
        
        print("\n" + "="*50)
        print("✅ 测试数据添加完成!")
        print("="*50 + "\n")


if __name__ == '__main__':
    seed_all()
