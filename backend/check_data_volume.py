from app import app
from models import db, TrafficStatus, Road, TrafficEvent

def check_volume():
    with app.app_context():
        road_count = db.session.query(Road).count()
        status_count = db.session.query(TrafficStatus).count()
        event_count = db.session.query(TrafficEvent).count()
        
        print(f"Roads: {road_count}")
        print(f"Traffic Status Records: {status_count}")
        print(f"Traffic Events: {event_count}")
        
        if status_count > 100000:
            print("SUCCESS: Traffic status records exceed 100,000.")
        else:
            print(f"WARNING: Traffic status records ({status_count}) are less than 100,000.")

if __name__ == "__main__":
    check_volume()
