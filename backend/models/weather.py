from extensions import db
from datetime import datetime

class WeatherCondition(db.Model):
    """天气状况模型"""
    __tablename__ = 'weather_conditions'
    
    id = db.Column(db.Integer, primary_key=True)
    road_id = db.Column(db.Integer, db.ForeignKey('roads.id'), nullable=True, index=True) # Nullable for city-wide weather
    condition = db.Column(db.String(50), nullable=False) # Sunny, Rainy, Foggy, Snowy, Stormy
    temperature = db.Column(db.Float) # Celsius
    visibility = db.Column(db.Float) # Meters
    precipitation = db.Column(db.Float) # mm/h
    wind_speed = db.Column(db.Float) # km/h
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    road = db.relationship('Road', backref='weather_conditions')

    def to_dict(self):
        return {
            'id': self.id,
            'road_id': self.road_id,
            'road_name': self.road.name if self.road else 'City Wide',
            'condition': self.condition,
            'temperature': self.temperature,
            'visibility': self.visibility,
            'precipitation': self.precipitation,
            'wind_speed': self.wind_speed,
            'timestamp': self.timestamp.isoformat()
        }
