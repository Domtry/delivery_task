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
    
    delivery_obj = Delivery.objects(user=current_user).paginate(page=page, per_page=per_page)
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
            'shared_link': delivery_item.shared_link,
            'created_at': delivery_item.created_at,
            'user_id': current_user
        })
    
    return jsonify({'data': delivery_list, 'pagination': paginate_data}), HTTP_200_OK


@delivery.get('/<string:delivery_id>')
@jwt_required()
def get_one(delivery_id):
    current_user = get_jwt_identity()
    delivery_obj = Delivery.objects(user=current_user, id=delivery_id).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery has not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': f'{delivery_obj.id}',
        'title': delivery_obj.title,
        'shared_link': delivery_obj.shared_link,
        'created_at': delivery_obj.created_at,
        'user_id': current_user
    }), HTTP_200_OK
    

@delivery.get('/<string:delivery_id>')
@jwt_required()
def get_one(delivery_id):
    current_user = get_jwt_identity()
    delivery_obj = Delivery.objects(user=current_user, id=delivery_id).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery has not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': f'{delivery_obj.id}',
        'title': delivery_obj.title,
        'shared_link': delivery_obj.shared_link,
        'created_at': delivery_obj.created_at,
        'user_id': current_user
    }), HTTP_200_OK
    
    
@delivery.post('')
@jwt_required()
def create_delivery():
    current_user = get_jwt_identity()
    title = request.get_json().get('title', '')
    access_key = request.get_json().get('accessKey', '')
    description = request.get_json().get('description', '')
    
    if len(title) < 5:
        return jsonify({'message': 'title has ... '}), HTTP_302_FOUND
    
    if len(access_key) <= 3 or " " in access_key :
        return jsonify({'message': 'title has ... '}), HTTP_302_FOUND
    
    delivery_obj = Delivery(
        title=title, 
        access_key=access_key,
        description=description, 
        shared_link="https://test.com/sddsdsdsdsds",
        user=current_user)
    delivery_obj.save()
    
    return jsonify({'message': 'delivery has been created ... '}), HTTP_201_CREATED