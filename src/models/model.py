from datetime import datetime
from enum import unique
from flask_mongoengine import MongoEngine

db = MongoEngine()


class Task(db.Document):
    title = db.StringField()
    end_point = db.StringField(required=True)
    started_point = db.StringField(required=True)
    client_phone = db.StringField(required=True)
    description = db.StringField()
    status = db.BooleanField(default=False)
    amount_delivery = db.IntField(min_value=0, default=0)
    created_at = db.DateTimeField(default=datetime.now())
    update_at = db.DateTimeField(default=datetime.now())
    delivery_id = db.ReferenceField('Delivery')
    
    def __repr__(self) -> str:
        return f'Task => {self.title}' 
        

class Delivery(db.Document):
    title = db.StringField(required=True)
    description = db.StringField()
    access_key = db.StringField(required=True, unique=True)
    update_at = db.DateTimeField(required=True, default=datetime.now())
    created_at = db.DateTimeField(required=True, default=datetime.now())
    tasks = db.ReferenceField('Task', reverse_delete_rule=2)
    user_id = db.ReferenceField('User')  
    
    def __repr__(self) -> str:
        f'Delivery => {self.title}' 
     

class User(db.Document):
    email = db.EmailField(required=True, unique=True)
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, unique=True)
    phone_number = db.StringField(required=True, unique=True)
    created_at = db.DateTimeField(required=True, default=datetime.now())
    update_at = db.DateTimeField(required=True, default=datetime.now())
    delivery = db.ReferenceField('Delivery', reverse_delete_rule=2)  
    
    def __repr__(self) -> str:
        f'User => {self.username}' 