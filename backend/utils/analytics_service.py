"""
数据分析服务模块
提供数据处理和分析的业务逻辑
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case, text
from models import TrafficStatus, TrafficEvent, Road
from extensions import db
import statistics


class TrafficAnalyticsService:
    """交通数据分析服务"""
    
    @staticmethod
    def get_road_statistics(road_id, hours=24):
        """获取道路的详细统计数据"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        statuses = TrafficStatus.query.filter(
            and_(
                TrafficStatus.road_id == road_id,
                TrafficStatus.timestamp >= time_threshold
            )
        ).all()
        
        if not statuses:
            return None
        
        congestion_values = [s.congestion_index for s in statuses if s.congestion_index is not None]
        speed_values = [s.speed for s in statuses if s.speed is not None]
        
        return {
            'road_id': road_id,
            'period_hours': hours,
            'record_count': len(statuses),
            'congestion': {
                'avg': round(sum(congestion_values) / len(congestion_values), 2) if congestion_values else 0,
                'min': round(min(congestion_values), 2) if congestion_values else 0,
                'max': round(max(congestion_values), 2) if congestion_values else 0,
                'median': round(statistics.median(congestion_values), 2) if congestion_values else 0,
                'std_dev': round(statistics.stdev(congestion_values), 2) if len(congestion_values) > 1 else 0
            },
            'speed': {
                'avg': round(sum(speed_values) / len(speed_values), 2) if speed_values else 0,
                'min': round(min(speed_values), 2) if speed_values else 0,
                'max': round(max(speed_values), 2) if speed_values else 0,
                'median': round(statistics.median(speed_values), 2) if speed_values else 0,
            },
            'status_distribution': TrafficAnalyticsService._count_status_distribution(statuses)
        }
    
    @staticmethod
    def _count_status_distribution(statuses):
        """统计状态分布"""
        distribution = {}
        for status in statuses:
            if status.status not in distribution:
                distribution[status.status] = 0
            distribution[status.status] += 1
        return distribution
    
    @staticmethod
    def get_peak_hours(days=7):
        """获取高峰时段分析"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        # 交通状态统计
        hourly_data = db.session.query(
            func.date_format(TrafficStatus.timestamp, '%H').label('hour'),
            func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
            func.avg(TrafficStatus.speed).label('avg_speed'),
            func.max(TrafficStatus.congestion_index).label('max_congestion'),
            func.min(TrafficStatus.speed).label('min_speed'),
            func.count(TrafficStatus.id).label('record_count')
        ).filter(
            TrafficStatus.timestamp >= time_threshold
        ).group_by('hour').all()

        # 事件统计
        event_counts = db.session.query(
            func.date_format(TrafficEvent.start_time, '%H').label('hour'),
            func.count(TrafficEvent.id).label('count')
        ).filter(
            TrafficEvent.start_time >= time_threshold
        ).group_by('hour').all()
        
        event_map = {int(e.hour): e.count for e in event_counts}
        
        result = []
        for data in hourly_data:
            hour = int(data.hour)
            result.append({
                'hour': hour,
                'avg_congestion': round(data.avg_congestion, 2) if data.avg_congestion else 0,
                'avg_speed': round(data.avg_speed, 1) if data.avg_speed else 0,
                'max_congestion': round(data.max_congestion, 2) if data.max_congestion else 0,
                'min_speed': round(data.min_speed, 1) if data.min_speed else 0,
                'record_count': data.record_count,
                'event_count': event_map.get(hour, 0),
                'status': TrafficAnalyticsService._classify_congestion(data.avg_congestion)
            })
        
        result.sort(key=lambda x: x['hour'])
        return result
    
    @staticmethod
    def _classify_congestion(congestion_index):
        """根据拥堵指数分类"""
        if congestion_index < 2:
            return '畅通'
        elif congestion_index < 4:
            return '缓行'
        elif congestion_index < 7:
            return '拥堵'
        else:
            return '严重拥堵'
    
    @staticmethod
    def get_event_impact_score(event_id):
        """计算事件的影响得分"""
        event = TrafficEvent.query.get(event_id)
        if not event:
            return None
        
        # 影响度计算公式
        severity_score = {'轻微': 1, '一般': 2, '严重': 3}.get(event.severity, 1)
        
        # 事件持续时间(小时)
        if event.end_time:
            duration_hours = (event.end_time - event.start_time).total_seconds() / 3600
        else:
            duration_hours = (datetime.utcnow() - event.start_time).total_seconds() / 3600
        
        # 受影响的拥堵增加量
        before_threshold = event.start_time - timedelta(hours=1)
        before_congestion = db.session.query(
            func.avg(TrafficStatus.congestion_index)
        ).filter(
            and_(
                TrafficStatus.road_id == event.road_id,
                TrafficStatus.timestamp >= before_threshold,
                TrafficStatus.timestamp < event.start_time
            )
        ).scalar() or 0
        
        during_congestion = db.session.query(
            func.avg(TrafficStatus.congestion_index)
        ).filter(
            and_(
                TrafficStatus.road_id == event.road_id,
                TrafficStatus.timestamp >= event.start_time,
                TrafficStatus.timestamp <= (event.end_time if event.end_time else datetime.utcnow())
            )
        ).scalar() or 0
        
        congestion_increase = max(0, during_congestion - before_congestion)
        
        # 综合影响得分 = 严重程度 * 持续时间 * 拥堵增量
        impact_score = severity_score * (1 + duration_hours / 24) * (1 + congestion_increase / 10)
        
        return round(impact_score, 2)
    
    @staticmethod
    def get_event_trend(days=30):
        """获取事件趋势"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        daily_events = db.session.query(
            func.date(TrafficEvent.start_time).label('date'),
            func.count(TrafficEvent.id).label('total'),
            func.sum(
                case(
                    (TrafficEvent.severity == '严重', 1),
                    else_=0
                )
            ).label('severe')
        ).filter(
            TrafficEvent.start_time >= time_threshold
        ).group_by('date').order_by('date').all()
        
        result = []
        for day in daily_events:
            result.append({
                'date': str(day.date),
                'total_events': day.total,
                'severe_events': day.severe or 0,
                'avg_severity': round((day.severe or 0) / day.total, 2)
            })
        
        return result
    
    @staticmethod
    def get_road_ranking(metric='congestion', hours=24, limit=10):
        """获取道路排名(按拥堵或其他指标)"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        if metric == 'congestion':
            roads_stats = db.session.query(
                TrafficStatus.road_id,
                func.avg(TrafficStatus.congestion_index).label('value')
            ).filter(
                TrafficStatus.timestamp >= time_threshold
            ).group_by(TrafficStatus.road_id).order_by(
                func.avg(TrafficStatus.congestion_index).desc()
            ).limit(limit).all()
        
        elif metric == 'speed':
            roads_stats = db.session.query(
                TrafficStatus.road_id,
                func.avg(TrafficStatus.speed).label('value')
            ).filter(
                and_(
                    TrafficStatus.timestamp >= time_threshold,
                    TrafficStatus.speed.isnot(None)
                )
            ).group_by(TrafficStatus.road_id).order_by(
                func.avg(TrafficStatus.speed).asc()
            ).limit(limit).all()
        
        else:
            return []
        
        result = []
        for i, stat in enumerate(roads_stats, 1):
            road = Road.query.get(stat.road_id)
            if road:
                result.append({
                    'rank': i,
                    'road': road.to_dict(),
                    'value': round(stat.value, 2) if stat.value else 0,
                    'metric': metric
                })
        
        return result
    
    @staticmethod
    def compare_roads(road_ids, metric='congestion', hours=24, start_date=None, end_date=None):
        """对比多条道路的指标时间序列"""
        # 使用传入的日期范围，如果没有则使用小时数
        if start_date and end_date:
            try:
                time_start = datetime.strptime(start_date, '%Y-%m-%d')
                time_end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                print(f'🔍 使用日期范围对比: {time_start} 到 {time_end}')
            except Exception as e:
                print(f'⚠️ 日期范围格式错误: {e}，改用小时数: {hours}')
                time_start = datetime.now() - timedelta(hours=hours)
                time_end = datetime.now()
        else:
            time_start = datetime.now() - timedelta(hours=hours)
            time_end = datetime.now()
            print(f'⏰ 使用小时数: {hours}小时')
        
        print(f'📊 查询范围: {time_start} 到 {time_end}')
        print(f'📍 查询道路: {road_ids}')
        
        result = []
        
        # 获取时间序列数据
        data_points = db.session.query(
            TrafficStatus.road_id,
            func.date_format(TrafficStatus.timestamp, '%Y-%m-%d %H:00:00').label('time_bucket'),
            func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
            func.avg(TrafficStatus.speed).label('avg_speed')
        ).filter(
            and_(
                TrafficStatus.road_id.in_(road_ids),
                TrafficStatus.timestamp >= time_start,
                TrafficStatus.timestamp <= time_end
            )
        ).group_by('time_bucket', TrafficStatus.road_id).order_by('time_bucket').all()
        
        print(f'📈 查询结果: {len(data_points)} 条记录')
        
        for point in data_points:
            result.append({
                'timestamp': point.time_bucket,
                'road_id': point.road_id,
                'avg_congestion': round(point.avg_congestion, 2) if point.avg_congestion else 0,
                'avg_speed': round(point.avg_speed, 2) if point.avg_speed else 0
            })
        
        return result
    
    @staticmethod
    def get_road_performance_summary(days=7, limit=5):
        """获取道路绩效汇总(用于行政报告)"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        # 1. 获取最拥堵的道路
        congested_roads_query = db.session.query(
            TrafficStatus.road_id,
            func.avg(TrafficStatus.congestion_index).label('avg_congestion'),
            func.count(TrafficStatus.id).label('total_records'),
            func.sum(case((TrafficStatus.congestion_index >= 7, 1), else_=0)).label('congested_records')
        ).filter(
            TrafficStatus.timestamp >= time_threshold
        ).group_by(TrafficStatus.road_id).order_by(
            func.avg(TrafficStatus.congestion_index).desc()
        ).limit(limit).all()
        
        most_congested = []
        for r in congested_roads_query:
            road = Road.query.get(r.road_id)
            if road:
                most_congested.append({
                    'road_name': road.name,
                    'avg_congestion': round(r.avg_congestion, 2),
                    'congestion_percentage': round(r.congested_records / r.total_records, 2) if r.total_records > 0 else 0
                })

        # 2. 获取最畅通的道路 (按速度)
        smoothest_roads_query = db.session.query(
            TrafficStatus.road_id,
            func.avg(TrafficStatus.speed).label('avg_speed'),
            func.count(TrafficStatus.id).label('total_records'),
            func.sum(case((TrafficStatus.congestion_index < 2, 1), else_=0)).label('smooth_records')
        ).filter(
            and_(
                TrafficStatus.timestamp >= time_threshold,
                TrafficStatus.speed.isnot(None)
            )
        ).group_by(TrafficStatus.road_id).order_by(
            func.avg(TrafficStatus.speed).desc()
        ).limit(limit).all()
        
        smoothest = []
        for r in smoothest_roads_query:
            road = Road.query.get(r.road_id)
            if road:
                smoothest.append({
                    'road_name': road.name,
                    'avg_speed': round(r.avg_speed, 1),
                    'smooth_percentage': round(r.smooth_records / r.total_records, 2) if r.total_records > 0 else 0
                })
                
        return {
            'most_congested_roads': most_congested,
            'smoothest_roads': smoothest
        }

    @staticmethod
    def generate_recommendations(summary):
        """生成智能建议"""
        recommendations = []
        
        # 基于拥堵的建议
        avg_congestion = summary.get('avg_congestion', 0)
        if avg_congestion > 6:
            recommendations.append("全路网平均拥堵指数较高，建议检查主干道信号灯配时方案。")
        elif avg_congestion > 4:
            recommendations.append("路网运行处于缓行状态，建议加强高峰期交通疏导。")
            
        # 基于事件的建议
        resolution_rate = summary.get('event_resolution_rate', 0)
        if resolution_rate < 0.8:
            recommendations.append(f"事件处理率仅为 {int(resolution_rate*100)}%，建议增加应急响应团队人手。")
            
        # 基于数据质量的建议
        completeness = summary.get('data_completeness', 0)
        if completeness < 90:
            recommendations.append("数据采集完整性不足 90%，建议检查传感器设备状态。")
            
        # 如果没有建议，添加默认建议
        if not recommendations:
            recommendations.append("路网运行整体平稳，建议继续保持当前管理措施。")
            
        return recommendations


class EventAnalyticsService:
    """交通事件分析服务"""
    
    @staticmethod
    def get_event_statistics(days=30):
        """获取事件综合统计"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        # 按类型统计
        by_type = db.session.query(
            TrafficEvent.event_type,
            func.count(TrafficEvent.id).label('count'),
            func.avg(
                case(
                    (TrafficEvent.severity == '严重', 3),
                    (TrafficEvent.severity == '一般', 2),
                    else_=1
                )
            ).label('avg_severity')
        ).filter(
            TrafficEvent.start_time >= time_threshold
        ).group_by(TrafficEvent.event_type).all()
        
        # 按状态统计
        by_status = db.session.query(
            TrafficEvent.status,
            func.count(TrafficEvent.id).label('count')
        ).group_by(TrafficEvent.status).all()
        
        # 平均处理时间
        avg_resolution = db.session.query(
            func.avg(
                (func.unix_timestamp(TrafficEvent.end_time) - func.unix_timestamp(TrafficEvent.start_time)) / 86400
            ).label('days')
        ).filter(
            and_(
                TrafficEvent.status == 'resolved',
                TrafficEvent.end_time.isnot(None)
            )
        ).first()
        
        avg_resolution_hours = (avg_resolution.days * 24) if avg_resolution.days else 0
        
        return {
            'by_type': [
                {
                    'type': t.event_type,
                    'count': t.count,
                    'avg_severity': round(t.avg_severity, 2)
                } for t in by_type
            ],
            'by_status': {s.status: s.count for s in by_status},
            'avg_resolution_hours': round(avg_resolution_hours, 2),
            'period_days': days
        }
    
    @staticmethod
    def get_high_impact_events(days=30, limit=10):
        """获取高影响事件"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        events = TrafficEvent.query.filter(
            TrafficEvent.start_time >= time_threshold
        ).order_by(
            TrafficEvent.severity.desc(),
            TrafficEvent.start_time.desc()
        ).limit(limit).all()
        
        result = []
        for event in events:
            impact_score = TrafficAnalyticsService.get_event_impact_score(event.id)
            result.append({
                'event': event.to_dict(),
                'impact_score': impact_score
            })
        
        result.sort(key=lambda x: x['impact_score'], reverse=True)
        return result
    
    @staticmethod
    def get_frequent_event_locations(days=30, limit=10):
        """获取事件多发地点"""
        time_threshold = datetime.utcnow() - timedelta(days=days)
        
        locations = db.session.query(
            TrafficEvent.road_id,
            func.count(TrafficEvent.id).label('count')
        ).filter(
            TrafficEvent.start_time >= time_threshold
        ).group_by(TrafficEvent.road_id).order_by(
            func.count(TrafficEvent.id).desc()
        ).limit(limit).all()
        
        result = []
        for loc in locations:
            road = Road.query.get(loc.road_id)
            if road:
                result.append({
                    'road': road.to_dict(),
                    'event_count': loc.count
                })
        
        return result


class DataQualityService:
    """数据质量管理服务"""
    
    @staticmethod
    def check_data_completeness(hours=24):
        """检查数据完整性"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        total_statuses = TrafficStatus.query.filter(
            TrafficStatus.timestamp >= time_threshold
        ).count()
        
        roads = Road.query.all()
        expected_records = len(roads) * (hours * 60 // 10)  # 假设10分钟一条记录
        
        completeness = round((total_statuses / expected_records * 100), 2) if expected_records > 0 else 0
        missing_records = max(0, expected_records - total_statuses)
        
        return {
            'total_records': total_statuses,
            'expected_records': expected_records,
            'missing_records': missing_records,
            'completeness_percentage': min(100, completeness),
            'period_hours': hours
        }
    
    @staticmethod
    def check_data_consistency():
        """检查数据一致性"""
        issues = []
        
        # 检查孤立的交通状态记录(对应的道路不存在)
        orphan_statuses = db.session.query(TrafficStatus).filter(
            ~db.session.query(Road).filter(
                Road.id == TrafficStatus.road_id
            ).exists()
        ).count()
        
        # 检查孤立的交通事件记录
        orphan_events = db.session.query(TrafficEvent).filter(
            ~db.session.query(Road).filter(
                Road.id == TrafficEvent.road_id
            ).exists()
        ).count()
        
        total_orphans = orphan_statuses + orphan_events
        
        if total_orphans > 0:
            issues.append({
                'type': 'orphan_records',
                'count': total_orphans,
                'description': '存在对应道路已删除的记录'
            })
        
        # 检查时间戳异常(未来的数据)
        future_timestamps = TrafficStatus.query.filter(
            TrafficStatus.timestamp > datetime.utcnow()
        ).count()
        
        if future_timestamps > 0:
            issues.append({
                'type': 'future_timestamps',
                'count': future_timestamps,
                'description': '存在时间戳在未来的记录'
            })
            
        # 检查异常关闭事件 (已解决但无结束时间，或结束时间早于开始时间)
        anomalous_closures = TrafficEvent.query.filter(
            or_(
                and_(TrafficEvent.status == 'resolved', TrafficEvent.end_time.is_(None)),
                TrafficEvent.end_time < TrafficEvent.start_time
            )
        ).count()
        
        if anomalous_closures > 0:
            issues.append({
                'type': 'anomalous_closures',
                'count': anomalous_closures,
                'description': '存在异常关闭的事件记录'
            })
        
        return {
            'issues_found': len(issues),
            'issues': issues,
            'status': 'good' if len(issues) == 0 else 'warning',
            'orphan_records': total_orphans,
            'future_timestamps': future_timestamps,
            'anomalous_closures': anomalous_closures,
            'is_consistent': len(issues) == 0
        }
