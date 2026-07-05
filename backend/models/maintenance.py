from extensions import db
from datetime import datetime

class MaintenanceSchedule(db.Model):
    """道路维护计划模型"""
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    maintenance_type = db.Column(db.String(100), nullable=False) # e.g., Resurfacing
    impact_level = db.Column(db.String(20)) # Low, Medium, High
    status = db.Column(db.String(20), default='Planned') # Planned, In Progress, Completed, Cancelled
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    road = db.relationship('Road', backref='maintenance_schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'road_id': self.road_id,
            'road_name': self.road.name if self.road else None,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'maintenance_type': self.maintenance_type,
            'impact_level': self.impact_level,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
