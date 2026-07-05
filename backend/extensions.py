from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

try:
    from flask_migrate import Migrate
    migrate = Migrate()
except ImportError:
    # flask_migrate is optional
    migrate = None

db = SQLAlchemy()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO(cors_allowed_origins="*")
