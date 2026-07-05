from extensions import db
from datetime import datetime


class TrafficEvent(db.Model):
    """交通事件模型"""
    __tablename__ = 'traffic_events'
    
    id = db.Column(db.Integer, primary_key=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)  # 事故/施工/管制/其他
    severity = db.Column(db.String(20))  # 轻微/一般/严重
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active/resolved
    start_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    end_time = db.Column(db.DateTime)
    affected_lanes = db.Column(db.String(100))  # 受影响车道
    source = db.Column(db.String(50))  # 数据来源
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'road_id': self.road_id,
            'road_name': self.road.name if self.road else None,
            'event_type': self.event_type,
            'severity': self.severity,
            'description': self.description,
            'location': {'lat': self.latitude, 'lng': self.longitude},
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'affected_lanes': self.affected_lanes,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TrafficEvent {self.event_type} on {self.road_id}>'
