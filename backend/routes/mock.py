"""
模拟数据路由 - 用于测试和开发
当真实的 API 端点不可用时，返回模拟数据
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

mock_bp = Blueprint('mock', __name__, url_prefix='/api/mock')


# ============ 模拟实时数据 ==============

@mock_bp.route('/traffic/realtime/summary', methods=['GET'])
def mock_realtime_summary():
    """模拟实时交通概览"""
    return jsonify({
        'total_roads': 6,
        'status_breakdown': {
            '畅通': 2,
            '缓行': 2,
            '拥堵': 1,
            '严重拥堵': 1
        },
        'avg_congestion_index': 3.5,
        'avg_speed': 35.8,
        'update_time': datetime.utcnow().isoformat()
    }), 200


@mock_bp.route('/traffic/status/latest', methods=['GET'])
def mock_latest_status():
    """模拟最新交通状态"""
    now = datetime.utcnow()
    return jsonify({
        'statuses': [
            {
                'id': 1,
                'road_id': 1,
                'road_name': '解放大道',
                'status': '拥堵',
                'speed': 25.5,
                'congestion_index': 6.5,
                'travel_time': 3600,
                'timestamp': now.isoformat(),
                'vehicle_count': 150
            },
            {
                'id': 2,
                'road_id': 2,
                'road_name': '中山大道',
                'status': '缓行',
                'speed': 35.2,
                'congestion_index': 4.2,
                'travel_time': 2400,
                'timestamp': now.isoformat(),
                'vehicle_count': 100
            },
            {
                'id': 3,
                'road_id': 3,
                'road_name': '亚洲大道',
                'status': '畅通',
                'speed': 50.0,
                'congestion_index': 1.2,
                'travel_time': 1800,
                'timestamp': now.isoformat(),
                'vehicle_count': 60
            },
            {
                'id': 4,
                'road_id': 4,
                'road_name': '江汉路',
                'status': '严重拥堵',
                'speed': 15.3,
                'congestion_index': 8.5,
                'travel_time': 5400,
                'timestamp': now.isoformat(),
                'vehicle_count': 200
            },
            {
                'id': 5,
                'road_id': 5,
                'road_name': '武汉大道',
                'status': '缓行',
                'speed': 38.6,
                'congestion_index': 3.8,
                'travel_time': 2200,
                'timestamp': now.isoformat(),
                'vehicle_count': 90
            },
            {
                'id': 6,
                'road_id': 6,
                'road_name': '中北路',
                'status': '畅通',
                'speed': 48.5,
                'congestion_index': 1.5,
                'travel_time': 1900,
                'timestamp': now.isoformat(),
                'vehicle_count': 70
            }
        ],
        'count': 6
    }), 200


@mock_bp.route('/events/active', methods=['GET'])
def mock_active_events():
    """模拟活跃交通事件"""
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    return jsonify({
        'events': [
            {
                'id': 1,
                'event_type': '事故',
                'severity': '高',
                'status': 'active',
                'description': '中山大道与武汉大道交叉口发生轻微车碰撞',
                'road_name': '中山大道',
                'affected_lanes': 2,
                'start_time': one_hour_ago.isoformat(),
                'latitude': 30.593,
                'longitude': 114.305
            },
            {
                'id': 2,
                'event_type': '施工',
                'severity': '中',
                'status': 'active',
                'description': '江汉路进行路面维修，占用一条车道',
                'road_name': '江汉路',
                'affected_lanes': 1,
                'start_time': (now - timedelta(hours=2)).isoformat(),
                'latitude': 30.590,
                'longitude': 114.265
            },
            {
                'id': 3,
                'event_type': '故障',
                'severity': '高',
                'status': 'active',
                'description': '大型货车抛锚占用主车道',
                'road_name': '解放大道',
                'affected_lanes': 3,
                'start_time': (now - timedelta(minutes=30)).isoformat(),
                'latitude': 30.578,
                'longitude': 114.298
            }
        ],
        'count': 3
    }), 200


@mock_bp.route('/traffic/analysis/peak-hours', methods=['GET'])
def mock_peak_hours():
    """模拟高峰时段分析"""
    hours_data = []
    for hour in range(24):
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            congestion = 5.8 + random.random() * 2
        elif 10 <= hour <= 16:
            congestion = 3.0 + random.random() * 2
        else:
            congestion = 0.5 + random.random() * 1.5
        
        hours_data.append({
            'hour': hour,
            'avg_congestion': round(congestion, 2),
            'event_count': random.randint(1, 5)
        })
    
    return jsonify({
        'peak_hours_analysis': hours_data
    }), 200


@mock_bp.route('/traffic/analysis/congested-roads', methods=['GET'])
def mock_congested_roads():
    """模拟最拥堵道路"""
    limit = request.args.get('limit', 5, type=int)
    roads = [
        {
            'road': {'id': 4, 'name': '江汉路', 'start_point': '武汉站', 'end_point': '江汉关'},
            'avg_congestion_index': 8.5,
            'avg_speed': 15.3
        },
        {
            'road': {'id': 1, 'name': '解放大道', 'start_point': '武昌首义广场', 'end_point': '汉口北'},
            'avg_congestion_index': 6.5,
            'avg_speed': 25.5
        },
        {
            'road': {'id': 2, 'name': '中山大道', 'start_point': '汉口', 'end_point': '武昌'},
            'avg_congestion_index': 4.2,
            'avg_speed': 35.2
        },
        {
            'road': {'id': 5, 'name': '武汉大道', 'start_point': '青山', 'end_point': '光谷'},
            'avg_congestion_index': 3.8,
            'avg_speed': 38.6
        },
        {
            'road': {'id': 3, 'name': '亚洲大道', 'start_point': '武汉客运港', 'end_point': '三环线'},
            'avg_congestion_index': 1.2,
            'avg_speed': 50.0
        }
    ]
    return jsonify({
        'most_congested_roads': roads[:limit]
    }), 200


@mock_bp.route('/traffic/analysis/smooth-roads', methods=['GET'])
def mock_smooth_roads():
    """模拟最畅通道路"""
    limit = request.args.get('limit', 5, type=int)
    roads = [
        {
            'road': {'id': 3, 'name': '亚洲大道', 'start_point': '武汉客运港', 'end_point': '三环线'},
            'avg_congestion_index': 1.2,
            'avg_speed': 50.0
        },
        {
            'road': {'id': 6, 'name': '中北路', 'start_point': '解放公园', 'end_point': '中北路隧道'},
            'avg_congestion_index': 1.5,
            'avg_speed': 48.5
        },
        {
            'road': {'id': 2, 'name': '中山大道', 'start_point': '汉口', 'end_point': '武昌'},
            'avg_congestion_index': 4.2,
            'avg_speed': 35.2
        },
        {
            'road': {'id': 5, 'name': '武汉大道', 'start_point': '青山', 'end_point': '光谷'},
            'avg_congestion_index': 3.8,
            'avg_speed': 38.6
        },
        {
            'road': {'id': 1, 'name': '解放大道', 'start_point': '武昌首义广场', 'end_point': '汉口北'},
            'avg_congestion_index': 6.5,
            'avg_speed': 25.5
        }
    ]
    return jsonify({
        'smoothest_roads': roads[:limit]
    }), 200


# ============ 高级分析数据路由 ==============

@mock_bp.route('/advanced/traffic/road-ranking', methods=['GET'])
def mock_advanced_road_ranking():
    """模拟高级分析 - 道路排名"""
    metric = request.args.get('metric', 'congestion')
    limit = request.args.get('limit', 10, type=int)
    
    roads = [
        {'road_name': '解放大道', 'avg_congestion': 6.5, 'avg_speed': 25.5},
        {'road_name': '中山大道', 'avg_congestion': 5.2, 'avg_speed': 35.2},
        {'road_name': '江汉路', 'avg_congestion': 8.5, 'avg_speed': 15.3},
        {'road_name': '汉口北', 'avg_congestion': 3.2, 'avg_speed': 45.2},
        {'road_name': '汉阳大道', 'avg_congestion': 4.8, 'avg_speed': 38.5},
        {'road_name': '武昌中路', 'avg_congestion': 5.1, 'avg_speed': 32.8},
        {'road_name': '三阳路', 'avg_congestion': 3.8, 'avg_speed': 42.5},
        {'road_name': '洪山路', 'avg_congestion': 4.5, 'avg_speed': 39.2},
        {'road_name': '珞喻路', 'avg_congestion': 2.1, 'avg_speed': 48.3},
        {'road_name': '关山大道', 'avg_congestion': 2.8, 'avg_speed': 46.5}
    ]
    
    # 按指标排序
    if metric == 'congestion':
        roads.sort(key=lambda x: x['avg_congestion'], reverse=True)
    else:
        roads.sort(key=lambda x: x['avg_speed'], reverse=True)
    
    return jsonify({
        'roads': roads[:limit]
    }), 200


@mock_bp.route('/advanced/traffic/peak-hours', methods=['GET'])
def mock_advanced_peak_hours():
    """模拟高级分析 - 高峰时段"""
    hours_data = []
    for hour in range(24):
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            congestion = 5.8 + random.random() * 2
        elif 10 <= hour <= 16:
            congestion = 3.0 + random.random() * 2
        else:
            congestion = 0.5 + random.random() * 1.5
        
        hours_data.append({
            'hour': hour,
            'avg_congestion': round(congestion, 2),
            'event_count': random.randint(1, 5)
        })
    
    return jsonify({
        'data': hours_data
    }), 200


@mock_bp.route('/advanced/events/frequent-locations', methods=['GET'])
def mock_frequent_event_locations():
    """模拟高级分析 - 高频事件地点"""
    locations = [
        {
            'location': '解放大道与民权路交叉口',
            'event_count': 45,
            'avg_duration': 32,
            'severity': '高'
        },
        {
            'location': '江汉路与中山大道交叉口',
            'event_count': 38,
            'avg_duration': 28,
            'severity': '中'
        },
        {
            'location': '汉口北站',
            'event_count': 32,
            'avg_duration': 25,
            'severity': '中'
        },
        {
            'location': '武昌火车站',
            'event_count': 28,
            'avg_duration': 30,
            'severity': '高'
        },
        {
            'location': '三阳路与武昌大道交叉口',
            'event_count': 22,
            'avg_duration': 20,
            'severity': '低'
        }
    ]
    return jsonify({
        'locations': locations
    }), 200


@mock_bp.route('/advanced/events/trend', methods=['GET'])
def mock_event_trend():
    """模拟高级分析 - 事件趋势"""
    now = datetime.utcnow()
    trend_data = []
    for i in range(7):
        date = (now - timedelta(days=6-i)).date()
        trend_data.append({
            'date': str(date),
            'event_count': random.randint(15, 45),
            'avg_duration': random.randint(20, 40)
        })
    
    return jsonify({
        'data': trend_data
    }), 200


@mock_bp.route('/advanced/quality/completeness', methods=['GET'])
def mock_data_completeness():
    """模拟高级分析 - 数据完整性"""
    return jsonify({
        'quality': {
            'overall_completeness': 95.5,
            'missing_records': 45,
            'total_expected': 1000,
            'status': 'good'
        }
    }), 200


@mock_bp.route('/advanced/quality/consistency', methods=['GET'])
def mock_data_consistency():
    """模拟高级分析 - 数据一致性"""
    return jsonify({
        'consistency': {
            'overall_consistency': 92.3,
            'inconsistent_records': 77,
            'total_records': 1000,
            'status': 'acceptable'
        }
    }), 200


@mock_bp.route('/advanced/report/executive-summary', methods=['GET'])
def mock_executive_summary():
    """模拟高级分析 - 行政汇总"""
    return jsonify({
        'summary': {
            'total_events': 342,
            'avg_response_time': '8分钟',
            'critical_roads': ['解放大道', '江汉路', '中山大道'],
            'recommendations': [
                '增加解放大道的交通管理人员',
                '优化江汉路的信号灯时序',
                '建议在中山大道设置临时停车场'
            ]
        }
    }), 200


# ============ 分析数据路由 ==============

@mock_bp.route('/analytics/events/high-impact', methods=['GET'])
def mock_high_impact_events():
    """模拟分析 - 高影响事件"""
    limit = request.args.get('limit', 10, type=int)
    events = [
        {
            'road_name': '解放大道',
            'event_type': '事故',
            'severity': '高',
            'impact_score': 8.5,
            'start_time': datetime.utcnow().isoformat(),
            'description': '多车碰撞'
        },
        {
            'road_name': '江汉路',
            'event_type': '积水',
            'severity': '高',
            'impact_score': 7.8,
            'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'description': '暴雨导致严重积水'
        },
        {
            'road_name': '中山大道',
            'event_type': '施工',
            'severity': '中',
            'impact_score': 6.2,
            'start_time': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'description': '路面维修施工'
        },
        {
            'road_name': '汉口北',
            'event_type': '事故',
            'severity': '中',
            'impact_score': 5.5,
            'start_time': (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            'description': '轻微追尾'
        },
        {
            'road_name': '武昌中路',
            'event_type': '拥堵',
            'severity': '低',
            'impact_score': 3.2,
            'start_time': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            'description': '局部缓行'
        }
    ]
    return jsonify({
        'events': events[:limit]
    }), 200

def register_mock_routes(app):
    """将模拟路由注册到应用"""
    app.register_blueprint(mock_bp)
