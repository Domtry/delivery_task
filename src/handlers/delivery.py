from datetime import datetime
from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_404_NOT_FOUND
from src.models.model import Delivery
from flask_jwt_extended import (get_jwt_identity, jwt_required)

delivery = Blueprint("delivery", __name__, url_prefix="/api/v1/delivery")

@delivery.get('')
@jwt_required()
def get_all():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    delivery_list = []
    
    delivery_obj = Delivery.objects(user_id=current_user).paginate(page=page, per_page=per_page)
    paginate_data = {
        "page": delivery_obj.page,
        "per_page": delivery_obj.per_page,
        "total_count": delivery_obj.total,
        "prev_page": delivery_obj.prev_num,
        "next_page": delivery_obj.next_num,
        "has_next": delivery_obj.has_next,
        "has_prev": delivery_obj.has_prev,
    }  
    
    for delivery_item in delivery_obj.items :
        delivery_list.append({
            'id': f'{delivery_item.id}',
            'title': delivery_item.title,
            'created_at': delivery_item.created_at,
            'user_id': current_user
        })
    
    return jsonify({'data': delivery_list, 'pagination': paginate_data}), HTTP_200_OK


@delivery.get('/<string:delivery_id>')
@jwt_required()
def get_one(delivery_id):
    current_user = get_jwt_identity()
    delivery_obj = Delivery.objects(user_id=current_user, id=delivery_id).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery has not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': f'{delivery_obj.id}',
        'title': delivery_obj.title,
        'created_at': delivery_obj.created_at,
        'user_id': current_user
    }), HTTP_200_OK
    
    
@delivery.get('/deliveryMan/<string:access_key>')
def get_one_by_access_key(access_key):
    delivery_obj = Delivery.objects(access_key=access_key).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery has not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': f'{delivery_obj.id}',
        'title': delivery_obj.title,
        'description': delivery_obj.description,
        'created_at': delivery_obj.created_at,
    }), HTTP_200_OK


@delivery.post('')
@jwt_required()
def create_delivery():
    current_user = get_jwt_identity()
    title = request.get_json().get('title', '')
    access_key = request.get_json().get('access_key', '')
    description = request.get_json().get('description', '')
    
    if len(title) < 5:
        return jsonify({'message': 'title is not correctly'}), HTTP_302_FOUND
    
    if len(access_key) <= 3 or " " in access_key :
        return jsonify({'message': 'access key is not correctly'}), HTTP_302_FOUND
    
    delivery_obj = Delivery(
        title=title, 
        access_key=access_key,
        description=description, 
        user_id=current_user)
    delivery_obj.save()
    
    return jsonify({'message': 'delivery has been created ... '}), HTTP_201_CREATED


@delivery.put('<string:delivery_id>')
@delivery.patch('<string:delivery_id>')
@jwt_required()
def update_delivery(delivery_id):
    current_user = get_jwt_identity()
    current_delivery = Delivery.objects(user_id=current_user, id=delivery_id).first()
    
    if not current_delivery:
        return jsonify({"message": "bookmark not found"}), 404
    
    title = request.get_json().get('title', '')
    description = request.get_json().get('description', '')
        
    current_delivery.update(title=title, description=description, update_at=datetime.now())
    return jsonify({"message": "delivery has been update"}), HTTP_200_OK


@delivery.put('/secure/<string:delivery_id>')
@jwt_required()
def changeç_access_key(delivery_id):
    current_user = get_jwt_identity()
    last_key = request.get_json().get('last_key', '')
    new_key = request.get_json().get('new_key', '')
    
    current_delivery = Delivery.objects(user_id=current_user, id=delivery_id).first()
    
    if not current_delivery:
        return jsonify({"message": "delivery has not found"}), HTTP_404_NOT_FOUND
    
    if current_delivery.access_key not in last_key:
        return jsonify({"message": "last password is not correctly. Please try egain"}), HTTP_302_FOUND
    
    if last_key in new_key:
        return jsonify({"message": "Please change you new access key"}), HTTP_302_FOUND
        
    current_delivery.update(access_key=new_key, update_at=datetime.now())
    return jsonify({"message": "delivery access key has been update"}), HTTP_200_OK