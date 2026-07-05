from extensions import db
from datetime import datetime


class Road(db.Model):
    """道路模型"""
    __tablename__ = 'roads'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    road_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    start_point = db.Column(db.String(200), nullable=False)
    end_point = db.Column(db.String(200), nullable=False)
    length = db.Column(db.Float)  # 道路长度(公里)
    lanes = db.Column(db.Integer)  # 车道数
    road_type = db.Column(db.String(50))  # 道路类型: 高速/主干道/次干道/支路
    latitude_start = db.Column(db.Float)
    longitude_start = db.Column(db.Float)
    latitude_end = db.Column(db.Float)
    longitude_end = db.Column(db.Float)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 优化字段：记录当前最新状态ID，避免复杂的聚合查询
    current_status_id = db.Column(db.Integer, db.ForeignKey('traffic_statuses.id', use_alter=True))
    
    # 关系
    traffic_statuses = db.relationship('TrafficStatus', backref='road', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='TrafficStatus.road_id')
    current_status = db.relationship('TrafficStatus', foreign_keys=[current_status_id], post_update=True)
    traffic_events = db.relationship('TrafficEvent', backref='road', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'road_code': self.road_code,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'length': self.length,
            'lanes': self.lanes,
            'road_type': self.road_type,
            'coordinates': {
                'start': {'lat': self.latitude_start, 'lng': self.longitude_start},
                'end': {'lat': self.latitude_end, 'lng': self.longitude_end}
            },
            'description': self.description,
            'current_status': self.current_status.status if self.current_status else '未知',
            'congestion_index': self.current_status.congestion_index if self.current_status else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Road {self.name}>'
