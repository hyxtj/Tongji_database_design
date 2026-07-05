from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Road, User, TrafficStatus
from extensions import db, cache
from sqlalchemy import func
from sqlalchemy.orm import joinedload

roads_bp = Blueprint('roads', __name__)


@roads_bp.route('', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=3, query_string=True)
def get_roads():
    """获取道路列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    road_type = request.args.get('type', None)
    search = request.args.get('search', None)
    status = request.args.get('status', None)
    
    # Viewport filtering
    min_lat = request.args.get('min_lat', type=float)
    max_lat = request.args.get('max_lat', type=float)
    min_lng = request.args.get('min_lng', type=float)
    max_lng = request.args.get('max_lng', type=float)
    
    # Eager load current_status to avoid N+1 queries
    query = Road.query.options(joinedload(Road.current_status))
    
    if min_lat and max_lat and min_lng and max_lng:
        query = query.filter(
            Road.latitude_start >= min_lat,
            Road.latitude_start <= max_lat,
            Road.longitude_start >= min_lng,
            Road.longitude_start <= max_lng
        )

    if status:
        # 子查询获取每条道路的最新时间戳
        subquery = db.session.query(
            TrafficStatus.road_id,
            func.max(TrafficStatus.timestamp).label('max_timestamp')
        ).group_by(TrafficStatus.road_id).subquery()
        
        # 连接查询筛选状态
        query = query.join(TrafficStatus, Road.id == TrafficStatus.road_id).join(
            subquery,
            db.and_(
                TrafficStatus.road_id == subquery.c.road_id,
                TrafficStatus.timestamp == subquery.c.max_timestamp
            )
        ).filter(TrafficStatus.status == status)

    if road_type:
        query = query.filter(Road.road_type == road_type)
    
    if search:
        query = query.filter(Road.name.contains(search))
    
    pagination = query.order_by(Road.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'roads': [road.to_dict() for road in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@roads_bp.route('/<int:road_id>', methods=['GET'])
def get_road(road_id):
    """获取单个道路详情"""
    road = Road.query.get_or_404(road_id)
    return jsonify(road.to_dict()), 200


@roads_bp.route('', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_road():
    """创建道路(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'road_code', 'start_point', 'end_point']
    if not all(k in data for k in required_fields):
        return jsonify({'error': '缺少必填字段'}), 400
    
    # 检查road_code是否已存在
    if Road.query.filter_by(road_code=data['road_code']).first():
        return jsonify({'error': '道路编码已存在'}), 400
    
    road = Road(
        name=data['name'],
        road_code=data['road_code'],
        start_point=data['start_point'],
        end_point=data['end_point'],
        length=data.get('length'),
        lanes=data.get('lanes'),
        road_type=data.get('road_type'),
        latitude_start=data.get('latitude_start'),
        longitude_start=data.get('longitude_start'),
        latitude_end=data.get('latitude_end'),
        longitude_end=data.get('longitude_end'),
        description=data.get('description')
    )
    
    db.session.add(road)
    db.session.commit()
    
    return jsonify({
        'message': '道路创建成功',
        'road': road.to_dict()
    }), 201


@roads_bp.route('/<int:road_id>', methods=['PUT'])
@jwt_required()
def update_road(road_id):
    """更新道路信息(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    road = Road.query.get_or_404(road_id)
    data = request.get_json()
    
    # 更新字段
    for key in ['name', 'start_point', 'end_point', 'length', 'lanes', 
                'road_type', 'latitude_start', 'longitude_start', 
                'latitude_end', 'longitude_end', 'description']:
        if key in data:
            setattr(road, key, data[key])
    
    db.session.commit()
    
    return jsonify({
        'message': '道路更新成功',
        'road': road.to_dict()
    }), 200


@roads_bp.route('/<int:road_id>', methods=['DELETE'])
@jwt_required()
def delete_road(road_id):
    """删除道路(需要管理员权限)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': '需要管理员权限'}), 403
    
    road = Road.query.get_or_404(road_id)
    db.session.delete(road)
    db.session.commit()
    
    return jsonify({'message': '道路删除成功'}), 200
