from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from extensions import db, migrate, cache, limiter, socketio
from routes import register_routes
from utils.temp_storage import temp_storage
import os
import threading
import time
from datetime import datetime


def cleanup_expired_registrations():
    """定期清理过期的注册信息"""
    while True:
        time.sleep(300)  # 每5分钟清理一次
        try:
            count = temp_storage.cleanup_expired()
            if count > 0:
                print(f'清理了 {count} 个过期的注册信息')
        except Exception as e:
            print(f'清理过期注册信息时出错: {e}')


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    if migrate is not None:
        migrate.init_app(app, db)
    JWTManager(app)
    cache.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app)
    
    # 注册路由
    register_routes(app)

    # 内部通知接口，用于模拟脚本通知前端更新
    @app.route('/api/internal/notify-update', methods=['POST'])
    def notify_update():
        # 验证简单的密钥（实际生产中应更安全）
        if request.headers.get('X-Internal-Secret') != 'traffic-sim-secret':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        # 通过 WebSocket 广播更新消息
        socketio.emit('traffic_update', data)
        return jsonify({'status': 'ok', 'message': 'Update broadcasted'})
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源未找到'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': '服务器内部错误'}), 500
    
    # 启动后台清理任务
    cleanup_thread = threading.Thread(target=cleanup_expired_registrations, daemon=True)
    cleanup_thread.start()
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })

    # 根路径欢迎页面
    @app.route('/')
    def index():
        return jsonify({
            'name': '城市交通状态查询系统 API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api_docs': '/api',
                'frontend': 'http://localhost:3000'
            },
            'api_routes': {
                'auth': '/api/auth/*',
                'roads': '/api/roads',
                'traffic': '/api/traffic/*',
                'events': '/api/events',
                'admin': '/api/admin/*'
            }
        })
    
    # API概览
    @app.route('/api')
    def api_overview():
        return jsonify({
            'message': '城市交通状态查询系统 API',
            'version': '1.0.0',
            'endpoints': {
                'authentication': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'refresh': 'POST /api/auth/refresh',
                    'current_user': 'GET /api/auth/me'
                },
                'roads': {
                    'list': 'GET /api/roads',
                    'detail': 'GET /api/roads/<id>',
                    'create': 'POST /api/roads (需要管理员权限)',
                    'update': 'PUT /api/roads/<id> (需要管理员权限)',
                    'delete': 'DELETE /api/roads/<id> (需要管理员权限)'
                },
                'traffic': {
                    'status_list': 'GET /api/traffic/status',
                    'latest_status': 'GET /api/traffic/status/latest',
                    'create_status': 'POST /api/traffic/status (需要管理员权限)',
                    'road_history': 'GET /api/traffic/status/<road_id>/history',
                    'statistics': 'GET /api/traffic/statistics'
                },
                'events': {
                    'list': 'GET /api/events',
                    'detail': 'GET /api/events/<id>',
                    'create': 'POST /api/events (需要管理员权限)',
                    'update': 'PUT /api/events/<id> (需要管理员权限)',
                    'delete': 'DELETE /api/events/<id> (需要管理员权限)',
                    'active': 'GET /api/events/active'
                },
                'admin': {
                    'dashboard': 'GET /api/admin/dashboard (需要管理员权限)',
                    'users': 'GET /api/admin/users (需要管理员权限)',
                    'toggle_admin': 'PUT /api/admin/users/<id>/admin (需要管理员权限)',
                    'delete_user': 'DELETE /api/admin/users/<id> (需要管理员权限)',
                    'init_data': 'POST /api/admin/init-data (需要管理员权限)'
                }
            },
            'documentation': '请访问前端应用: http://localhost:3000'
        })
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True') == 'True',
        allow_unsafe_werkzeug=True
    )
