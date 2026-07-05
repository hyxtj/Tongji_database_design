from extensions import db
from datetime import datetime

class TrafficPrediction(db.Model):
    """交通预测模型"""
    __tablename__ = 'traffic_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=False, index=True)
    predicted_time = db.Column(db.DateTime, nullable=False, index=True)
    predicted_congestion = db.Column(db.Float) # 0-10
    predicted_speed = db.Column(db.Float) # km/h
    confidence_score = db.Column(db.Float) # 0.0 - 1.0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    road = db.relationship('Road', backref='predictions')

    def to_dict(self):
        return {
            'id': self.id,
            'road_id': self.road_id,
            'road_name': self.road.name if self.road else None,
            'predicted_time': self.predicted_time.isoformat(),
            'predicted_congestion': self.predicted_congestion,
            'predicted_speed': self.predicted_speed,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }
