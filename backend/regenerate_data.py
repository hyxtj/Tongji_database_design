"""
生成新数据
运行方式: python regenerate_data.py
"""
import sys
sys.path.insert(0, '.')

from app import create_app
from extensions import db
from models import Road
from seed_data import seed_roads, seed_traffic_status, seed_events, seed_weather, seed_predictions, seed_maintenance

def regenerate_database():
    """批量添加数据(不删除原有数据)"""
    app = create_app()
    with app.app_context():
        # print("🗑️  正在清空数据库...")
        # db.drop_all()
        
        # print("📋 正在创建表结构...")
        # db.create_all()
        
        print("🛣️  正在检查道路数据...")
        roads = Road.query.all()
        if not roads:
            print("道路数据不存在，正在创建...")
            roads = seed_roads()
            print(f"✅ 添加了 {len(roads)} 条道路")
        else:
            print(f"✅ 发现 {len(roads)} 条现有道路，跳过创建")
        
        # 设置生成的天数，可以根据需要修改
        days = 90
        print(f"🚗 正在添加交通状态数据({days}天历史数据)...")
        statuses = seed_traffic_status(roads, days=days)
        print(f"✅ 添加了交通状态数据")
        
        print("⚠️  正在添加事件数据...")
        events = seed_events(roads)
        print(f"✅ 添加了 {len(events)} 条事件记录")

        print("🧠 正在添加智能交通数据...")
        seed_weather(roads)
        seed_predictions(roads)
        seed_maintenance(roads)
        print("✅ 智能交通数据添加完成")
        
        print("\n📊 数据批量添加完成!")
        print(f"   - 道路: {len(roads)} 条")
        print(f"   - 事件: {len(events)} 条")

if __name__ == '__main__':
    regenerate_database()
