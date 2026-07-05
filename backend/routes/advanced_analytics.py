"""
高级数据分析和报告API
基于分析服务类的高级功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from utils.analytics_service import (
    TrafficAnalyticsService, 
    EventAnalyticsService, 
    DataQualityService
)

advanced_analytics_bp = Blueprint('advanced_analytics', __name__, url_prefix='')


# ============== 交通分析 ==============

@advanced_analytics_bp.route('/traffic/road-stats', methods=['GET'])
def get_road_detailed_stats():
    """获取单条道路的详细统计"""
    road_id = request.args.get('road_id', type=int)
    hours = request.args.get('hours', 24, type=int)
    
    if not road_id:
        return jsonify({'error': '请提供道路ID'}), 400
    
    stats = TrafficAnalyticsService.get_road_statistics(road_id, hours)
    
    if not stats:
        return jsonify({'error': '未找到该道路的数据'}), 404
    
    return jsonify(stats), 200


@advanced_analytics_bp.route('/traffic/peak-hours', methods=['GET'])
def get_peak_hours_analysis():
    """获取高峰时段分析"""
    start_date = request.args.get('startDate')  # YYYY-MM-DD 格式
    end_date = request.args.get('endDate')      # YYYY-MM-DD 格式
    
    # 如果提供了日期范围，计算天数；否则使用默认 7 天
    days = 7
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 7
        except:
            days = 7
    
    peak_hours = TrafficAnalyticsService.get_peak_hours(days)
    
    # 找出最繁忙和最畅通的时段
    if peak_hours:
        peak_hours.sort(key=lambda x: x['avg_congestion'], reverse=True)
        busiest_hours = peak_hours[:3]
        smoothest_hours = peak_hours[-3:]
    else:
        busiest_hours = []
        smoothest_hours = []
    
    return jsonify({
        'data': peak_hours,
        'peak_hours_all': peak_hours,
        'busiest_hours': busiest_hours,
        'smoothest_hours': smoothest_hours,
        'period_days': days
    }), 200


@advanced_analytics_bp.route('/traffic/road-ranking', methods=['GET'])
def get_road_ranking():
    """获取道路排名"""
    metric = request.args.get('metric', 'congestion')  # congestion 或 speed
    start_date = request.args.get('startDate')  # YYYY-MM-DD 格式
    end_date = request.args.get('endDate')      # YYYY-MM-DD 格式
    limit = request.args.get('limit', 10, type=int)
    
    # 如果提供了日期范围，计算小时数；否则使用默认 24 小时
    hours = 24
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            hours = int((end - start).total_seconds() / 3600)
            if hours <= 0:
                hours = 24
        except:
            hours = 24
    
    if metric not in ['congestion', 'speed']:
        return jsonify({'error': '无效的指标类型'}), 400
    
    ranking = TrafficAnalyticsService.get_road_ranking(metric, hours, limit)
    
    # 转换格式以符合前端期望
    roads = []
    for item in ranking:
        road_data = item['road']
        roads.append({
            'rank': item['rank'],
            'road_id': road_data.get('id'),
            'road_name': road_data.get('name'),
            'road_code': road_data.get('road_code'),
            'road_type': road_data.get('road_type'),
            'avg_congestion': item['value'] if metric == 'congestion' else None,
            'avg_speed': item['value'] if metric == 'speed' else None,
        })
    
    return jsonify({
        'roads': roads,
        'metric': metric,
        'period_hours': hours,
        'total': len(roads)
    }), 200


@advanced_analytics_bp.route('/traffic/road-comparison', methods=['POST'])
def compare_roads():
    """对比多条道路"""
    data = request.get_json()
    
    # 支持 camelCase 和 snake_case
    road_ids = data.get('roadIds') or data.get('road_ids', [])
    metric = data.get('metric', 'congestion')
    
    # 支持日期范围或小时数
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    hours = data.get('hours', 24)
    
    print(f'📨 收到道路对比请求: roads={road_ids}, metric={metric}')
    print(f'   startDate={start_date}, endDate={end_date}, hours={hours}')
    
    # 如果提供了日期范围，使用日期范围而不是小时数
    if start_date and end_date:
        try:
            from datetime import datetime, timedelta
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # 包含结束日期
            days = (end - start).days
            hours = days * 24  # 计算实际天数的小时数
            print(f'📅 日期范围对比: {start_date} 到 {end_date}')
            print(f'   计算得到: {days}天, {hours}小时')
            print(f'   时间范围: {start} 到 {end}')
        except Exception as e:
            print(f'❌ 日期解析失败: {e}')
            pass
    
    if not road_ids or not isinstance(road_ids, list):
        return jsonify({'error': '请提供有效的道路ID列表'}), 400
    
    if metric not in ['congestion', 'speed']:
        return jsonify({'error': '无效的指标类型'}), 400
    
    comparison = TrafficAnalyticsService.compare_roads(road_ids, metric, hours, start_date, end_date)
    
    print(f'✅ 返回 {len(comparison)} 条对比数据')
    
    if not comparison:
        return jsonify({'error': '未找到指定的道路或数据'}), 404
    
    return jsonify({
        'data': comparison,
        'metric': metric,
        'period_hours': hours,
        'roads_compared': len(road_ids)
    }), 200


# ============== 事件分析 ==============

@advanced_analytics_bp.route('/events/statistics', methods=['GET'])
def get_event_statistics():
    """获取事件统计"""
    days = request.args.get('days', 30, type=int)
    
    stats = EventAnalyticsService.get_event_statistics(days)
    
    return jsonify(stats), 200


@advanced_analytics_bp.route('/events/high-impact', methods=['GET'])
def get_high_impact_events():
    """获取高影响事件"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    limit = request.args.get('limit', 10, type=int)
    
    # 计算天数
    days = 30
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 30
        except:
            days = 30
    
    events = EventAnalyticsService.get_high_impact_events(days, limit)
    
    return jsonify({
        'events': events,
        'period_days': days,
        'total': len(events)
    }), 200


@advanced_analytics_bp.route('/events/frequent-locations', methods=['GET'])
def get_frequent_event_locations():
    """获取事件多发地点"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    limit = request.args.get('limit', 10, type=int)
    
    # 计算天数
    days = 30
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 30
        except:
            days = 30
    
    locations = EventAnalyticsService.get_frequent_event_locations(days, limit)
    
    return jsonify({
        'locations': locations,
        'period_days': days,
        'total': len(locations)
    }), 200


@advanced_analytics_bp.route('/events/impact-score/<int:event_id>', methods=['GET'])
def get_event_impact_score(event_id):
    """获取单个事件的影响得分"""
    score = TrafficAnalyticsService.get_event_impact_score(event_id)
    
    if score is None:
        return jsonify({'error': '事件不存在'}), 404
    
    return jsonify({
        'event_id': event_id,
        'impact_score': score,
        'rating': TrafficAnalyticsService._classify_impact(score)
    }), 200


@advanced_analytics_bp.route('/events/trend', methods=['GET'])
def get_event_trend():
    """获取事件趋势"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    # 计算天数
    days = 30
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 30
        except:
            days = 30
    
    trend = TrafficAnalyticsService.get_event_trend(days)
    
    return jsonify({
        'data': trend,
        'period_days': days
    }), 200


# ============== 数据质量 ==============

@advanced_analytics_bp.route('/quality/completeness', methods=['GET'])
def check_data_completeness():
    """检查数据完整性"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    # 计算小时数
    hours = 24
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            hours = int((end - start).total_seconds() / 3600)
            if hours <= 0:
                hours = 24
        except:
            hours = 24
    
    completeness = DataQualityService.check_data_completeness(hours)
    
    return jsonify({
        'quality': completeness
    }), 200


@advanced_analytics_bp.route('/quality/consistency', methods=['GET'])
def check_data_consistency():
    """检查数据一致性"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    # 计算小时数
    hours = 24
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            hours = int((end - start).total_seconds() / 3600)
            if hours <= 0:
                hours = 24
        except:
            hours = 24
    
    consistency = DataQualityService.check_data_consistency()
    
    return jsonify({
        'consistency': consistency
    }), 200


@advanced_analytics_bp.route('/quality/report', methods=['GET'])
@jwt_required()
def get_quality_report():
    """获取数据质量完整报告(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    completeness = DataQualityService.check_data_completeness(24)
    consistency = DataQualityService.check_data_consistency()
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'completeness': completeness,
        'consistency': consistency,
        'overall_status': 'good' if consistency['issues_found'] == 0 and completeness['completeness_percentage'] >= 80 else 'warning'
    }), 200


# ============== 综合报告 ==============

@advanced_analytics_bp.route('/report/executive-summary', methods=['GET'])
def get_executive_summary():
    """获取行政汇总报告"""
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    
    # 计算天数
    days = 7
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days
            if days <= 0:
                days = 7
        except:
            days = 7
    
    # 交通分析
    traffic_stats = TrafficAnalyticsService.get_peak_hours(days)
    avg_congestion = sum(s['avg_congestion'] for s in traffic_stats) / len(traffic_stats) if traffic_stats else 0
    avg_speed = sum(s['avg_speed'] for s in traffic_stats) / len(traffic_stats) if traffic_stats else 0
    
    # 获取道路绩效汇总
    road_performance = TrafficAnalyticsService.get_road_performance_summary(days)
    
    # 事件分析
    event_stats = EventAnalyticsService.get_event_statistics(days)
    total_events = sum(event_stats['by_status'].values())
    resolved_events = event_stats['by_status'].get('resolved', 0)
    resolution_rate = resolved_events / total_events if total_events > 0 else 0
    
    high_impact = EventAnalyticsService.get_high_impact_events(days, 5)
    
    # 数据质量
    completeness = DataQualityService.check_data_completeness(24 * days)
    
    summary_data = {
        'period_days': days,
        'avg_congestion': round(avg_congestion, 2),
        'avg_speed': round(avg_speed, 1),
        'total_events': total_events,
        'event_resolution_rate': round(resolution_rate, 2),
        'critical_events': event_stats['by_status'].get('active', 0),
        'data_completeness': completeness['completeness_percentage'],
        'most_congested_roads': road_performance['most_congested_roads'],
        'smoothest_roads': road_performance['smoothest_roads']
    }
    
    recommendations = TrafficAnalyticsService.generate_recommendations(summary_data)
    summary_data['recommendations'] = recommendations
    
    return jsonify({
        'summary': summary_data,
        'highlights': {
            'peak_hours': traffic_stats[:3] if traffic_stats else [],
            'top_events': high_impact[:5]
        }
    }), 200


# ============== 辅助函数 ==============

def _classify_impact(score):
    """影响得分分类"""
    if score < 5:
        return '低'
    elif score < 15:
        return '中'
    elif score < 30:
        return '高'
    else:
        return '严重'


# 更新TrafficAnalyticsService，添加影响分类方法
TrafficAnalyticsService._classify_impact = staticmethod(_classify_impact)


from datetime import datetime
