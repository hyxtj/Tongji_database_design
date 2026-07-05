from extensions import db
from datetime import datetime


class TrafficStatus(db.Model):
    """交通状态模型"""
    __tablename__ = 'traffic_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # 畅通/缓行/拥堵/严重拥堵
    speed = db.Column(db.Float)  # 平均速度(km/h)
    congestion_index = db.Column(db.Float)  # 拥堵指数(0-10)
    travel_time = db.Column(db.Integer)  # 预计通行时间(秒)
    vehicle_count = db.Column(db.Integer)  # 车辆数量
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    source = db.Column(db.String(50))  # 数据来源: manual/amap/baidu
    
    # 复合索引，加速查询某条道路的最新状态
    __table_args__ = (
        db.Index('idx_road_timestamp', 'road_id', 'timestamp'),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'road_id': self.road_id,
            'road_name': self.road.name if self.road else None,
            'status': self.status,
            'speed': self.speed,
            'congestion_index': self.congestion_index,
            'travel_time': self.travel_time,
            'vehicle_count': self.vehicle_count,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }
    
    @staticmethod
    def get_status_from_index(index):
        """根据拥堵指数获取状态"""
        if index < 2:
            return '畅通'
        elif index < 4:
            return '缓行'
        elif index < 7:
            return '拥堵'
        else:
            return '严重拥堵'
    
    def __repr__(self):
        return f'<TrafficStatus {self.road_id} - {self.status}>'
