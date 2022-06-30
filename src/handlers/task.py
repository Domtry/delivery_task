from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_404_NOT_FOUND)
from src.models.model import Task, Delivery
from flask_jwt_extended import (get_jwt_identity, jwt_required)

task = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")

@task.get('/<string:task_id>')
@cross_origin()
def get_one_task(task_id):
  
    task_obj = Task.objects(id=task_id).first()
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
        'delivery_id': f'{task_obj.delivery_id}',
        'amount_delivery': task_obj.amount_delivery,
        'created_at': task_obj.created_at,
    }), HTTP_200_OK

    
@task.get('/completed/<string:secure_key>/<string:task_id>')
@cross_origin()
def toggle_task_status(secure_key, task_id):
    task_status = False    
    task_obj = Task.objects(id=task_id).first()
    
    if not task_obj :
        return jsonify({'message': 'task is not found'}), HTTP_302_FOUND
    
    current_delivery = Delivery.objects(access_key=secure_key).first()
    current_amount = int(current_delivery.total_amount)
    print(current_amount)
    if task_obj.status == False :
        task_status = True
        current_amount = current_amount + task_obj.amount_delivery
    else :
        current_amount = current_amount - task_obj.amount_delivery
    
    task_obj.update(status=task_status, update_at=datetime.now())
    current_delivery.update(total_amount=current_amount)
    
    return jsonify({
        'id': f'{task_obj.id}',
        'title': task_obj.title,
        'end_point': task_obj.end_point,
        'started_point': task_obj.started_point,
        'client_phone': task_obj.client_phone,
        'description': task_obj.description,
        'status': task_status,
        'amount_delivery': task_obj.amount_delivery,
        'created_at': task_obj.created_at,
    }), HTTP_200_OK
    
    
@task.post('/')
@jwt_required()
@cross_origin()
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
    
    delivery_obj = Delivery.objects(user_id=current_user, id=delivery_id).first()
    
    if not delivery_obj :
        return jsonify({'message': 'delivery is not found'}), HTTP_302_FOUND
    
    task_obj = Task(
        title=title,
        started_point=started_point,
        end_point=end_point,
        description=description,
        client_phone=client_phone,
        amount_delivery=amount_delivery,
        delivery_id=delivery_obj
        )
    task_obj.save()
    return jsonify({'message': 'task has been created ... '}), HTTP_201_CREATED


@task.put('/<string:task_id>')
@jwt_required()
@cross_origin()
def update_task(task_id):
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
    
    task_obj = Task.objects(id=task_id, delivery_id=delivery_id).first()
    print(task_id)
    if not task_obj :
        return jsonify({'message': 'task is not found'}), HTTP_302_FOUND
    
    task_obj.update(
        title=title,
        started_point=started_point,
        end_point=end_point,
        description=description,
        client_phone=client_phone,
        amount_delivery=amount_delivery,
        delivery_id=delivery_id,
        update_at=datetime.now()
        )
    return jsonify({'message': 'task has been updated'}), HTTP_201_CREATED


@task.get('/delivery/<string:delivery_access_key>')
@cross_origin()
def get_all_task(delivery_access_key):
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    task_list = []
    
    delivery_obj = Delivery.objects(access_key=delivery_access_key).first()
    task_obj = Task.objects(delivery_id=delivery_obj).paginate(page=page, per_page=per_page)
    
    paginate_data = {
        "page": task_obj.page,
        "per_page": task_obj.per_page,
        "total_count": task_obj.total,
        "prev_page": task_obj.prev_num,
        "next_page": task_obj.next_num,
        "has_next": task_obj.has_next,
        "has_prev": task_obj.has_prev,
    }
    
    for task_item in task_obj.items :
        task_list.append({
            'id': f'{task_item.id}',
            'title': task_item.title,
            'end_point': task_item.end_point,
            'started_point': task_item.started_point,
            'client_phone': task_item.client_phone,
            'description': task_item.description,
            'status': task_item.status,
            'delivery_id': f'{delivery_obj.id}',
            'amount_delivery': task_item.amount_delivery,
            'created_at': task_item.created_at,
        })
    
    return jsonify({'data': task_list, 'pagination': paginate_data}), HTTP_200_OK