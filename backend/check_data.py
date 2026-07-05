"""
检查数据库中的数据时间范围
"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import TrafficStatus
from extensions import db
from datetime import datetime

app = create_app()
with app.app_context():
    # 检查交通数据
    earliest = db.session.query(TrafficStatus).order_by(TrafficStatus.timestamp).first()
    latest = db.session.query(TrafficStatus).order_by(TrafficStatus.timestamp.desc()).first()
    
    if earliest and latest:
        days_diff = (latest.timestamp - earliest.timestamp).days
        print(f"📊 交通数据时间范围:")
        print(f"  最早: {earliest.timestamp} (Road {earliest.road_id})")
        print(f"  最新: {latest.timestamp} (Road {latest.road_id})")
        print(f"  时间跨度: {days_diff} 天")
        
        total_count = db.session.query(TrafficStatus).count()
        print(f"  总记录数: {total_count}")
        
        # 统计每条道路的记录数
        from sqlalchemy import func
        road_stats = db.session.query(
            TrafficStatus.road_id,
            func.count(TrafficStatus.id).label('count'),
            func.min(TrafficStatus.timestamp).label('earliest'),
            func.max(TrafficStatus.timestamp).label('latest')
        ).group_by(TrafficStatus.road_id).all()
        
        print(f"\n🛣️  道路数据统计:")
        for stat in road_stats[:5]:  # 只显示前5条
            days = (stat.latest - stat.earliest).days
            print(f"  道路 {stat.road_id}: {stat.count} 条记录, {days} 天")
    else:
        print("❌ 数据库中没有交通数据")
