from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_404_NOT_FOUND
from src.models.model import Task, Delivery
from flask_jwt_extended import (get_jwt_identity, jwt_required)

task = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")

@task.get('/<string:task_id>')
def get_one_task(task_id):
    delivery_access_key = request.get_json().get('delivery_key', '')
    delivery_obj = Delivery.objects(access_key=delivery_access_key).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery has not found'}), HTTP_404_NOT_FOUND
    
    task_obj = Task.objects(id=task_id, delivery_id=delivery_obj).first()
    if not task_obj :
        return jsonify({'message': 'task has not found'}), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': f'{task_obj.id}',
        'title': task_obj.title,
        'end_point': task_obj.end_point,
        'started_point': task_obj.started_point,
        'client_phone': task_obj.client_phone,
        'description': task_obj.description,
        'status': task_obj.status,
        'amount_delivery': task_obj.amount_delivery,
        'created_at': task_obj.created_at,
        'delivery_id': delivery_obj
    }), HTTP_200_OK
    
    
@task.post('/')
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    delivery_id = request.get_json().get('delivery_id', '')
    title = request.get_json().get('title', '')
    end_point = request.get_json().get('end_point', '')
    started_point = request.get_json().get('started_point', '')
    description = request.get_json().get('description', '')
    amount_delivery = request.get_json().get('amount_delivery', '')
    client_phone = request.get_json().get('client_phone', '')
    
    if len(title) < 5:
        return jsonify({'message': 'title is not correctly'}), HTTP_302_FOUND
    
    if len(started_point) < 5:
        return jsonify({'message': 'started point is not correctly'}), HTTP_302_FOUND
    
    if len(end_point) < 5:
        return jsonify({'message': 'end point is not correctly'}), HTTP_302_FOUND
    
    if amount_delivery == 0:
        return jsonify({'message': 'amount is not correctly'}), HTTP_302_FOUND
    
    if len(client_phone) <= 8:
        return jsonify({'message': 'phone number is not correctly'}), HTTP_302_FOUND
    
    if not Delivery.objects(user_id=current_user, id=delivery_id).first() :
        return jsonify({'message': 'delivery is not found'}), HTTP_302_FOUND
    
    task_obj = Task(
        title=title,
        started_point=started_point,
        end_point=end_point,
        description=description,
        client_phone=client_phone,
        amount_delivery=amount_delivery,
        delivery_id=delivery_id
        )
    task_obj.save()
    return jsonify({'message': 'task has been created ... '}), HTTP_201_CREATED
