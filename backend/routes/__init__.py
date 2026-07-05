from flask import Blueprint
from .auth import auth_bp
from .roads import roads_bp
from .traffic import traffic_bp
from .events import events_bp
from .admin import admin_bp
from .analytics import analytics_bp
from .advanced_analytics import advanced_analytics_bp
from .export import export_bp
from .mock import mock_bp
from .smart_traffic import smart_bp


def register_routes(app):
    """注册所有路由"""
    # API前缀
    api_prefix = '/api'
    
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(roads_bp, url_prefix=f'{api_prefix}/roads')
    app.register_blueprint(traffic_bp, url_prefix=f'{api_prefix}/traffic')
    app.register_blueprint(events_bp, url_prefix=f'{api_prefix}/events')
    app.register_blueprint(admin_bp, url_prefix=f'{api_prefix}/admin')
    app.register_blueprint(analytics_bp, url_prefix=f'{api_prefix}/analytics')
    app.register_blueprint(advanced_analytics_bp, url_prefix=f'{api_prefix}/advanced')
    app.register_blueprint(export_bp, url_prefix=f'{api_prefix}/export')
    app.register_blueprint(smart_bp, url_prefix=f'{api_prefix}/smart')
    app.register_blueprint(mock_bp)  # 模拟数据路由，包含自己的前缀

