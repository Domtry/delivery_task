from flask import Blueprint, jsonify, request
from werkzeug.security import (check_password_hash, generate_password_hash)
import validators
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, 
    jwt_required, create_refresh_token)
from src.constants.http_status_codes import( 
    HTTP_200_OK, HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, 
    HTTP_409_CONFLICT)

from src.models.model import User
user = Blueprint("user", __name__, url_prefix="/api/v1/auth")

@user.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    phone_number = request.json['phone_number']
        
    if len(password) < 6 :
        return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST
    
    if len(username) < 3 :
        return jsonify({'error': 'Username is too short'}), HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({'error': 'Username hould be alphanumeric, also no spaces'}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({'error': 'Email has not valid please write god email'}), HTTP_400_BAD_REQUEST

    if User.objects(username=username).first() is not None :
        return jsonify({'error': 'username is taken'}), HTTP_409_CONFLICT
    
    if User.objects(email=email).first() is not None :
        return jsonify({'error': 'email is taken'}), HTTP_409_CONFLICT
    
    if User.objects(phone_number=phone_number).first() is not None :
        return jsonify({'error': 'phone_number is taken'}), HTTP_409_CONFLICT
    
    pwd_hash = generate_password_hash(password)
    user = User(username=username, email=email, phone_number=phone_number, password=pwd_hash)
    user.save()
    
    return jsonify({
        'message': 'User has created',
        'user': {
            'phone_number': phone_number,
            'username': username,
            'email': email,
            }
        }), HTTP_201_CREATED


@user.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')
    
    user = User.objects(email=email).first()
    
    if user :
        is_correct_pwd = check_password_hash(user.password, password)
        
        if is_correct_pwd :
            refresh = create_refresh_token(identity=f'{user.id}')
            access = create_access_token(identity=f'{user.id}')
            
            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
            
        return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED
    

@user.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.objects(id=user_id).first()
    
    return jsonify({
        'email': user.email,
        'username': user.username
    }), HTTP_200_OK
    
    
@user.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({'access': access}), HTTP_200_OK
