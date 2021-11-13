import uuid
import jwt
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisshouldbechangedaftercloningfromgit'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(120))
    status = db.Column(db.String(120), nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers['token'] if 'token' in request.headers else None
        if not token:
            return jsonify({"message": "Token Not Found"})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({"message": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


def save_data(title, description, current_user):
    task = Task(title=title, description=description, user_id=current_user)
    db.session.add(task)
    db.session.commit()


def update_data(id, title, description):
    task = Task.query.filter_by(id=id).first()
    task.title = title
    task.description = description
    db.session.commit()


def update_status(id):
    task = Task.query.filter_by(id=id).first()
    task.status = True
    db.session.commit()


def delete_data(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()


@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API Landing Page"})


# Get all Users only if you are a admin
@app.route('/users', methods=['GET'])
@token_required
def user(current_user):
    if current_user.admin:
        if request.method == 'GET':
            users = User.query.all()
            result = []
            for user in users:
                user_data = {'public_id': user.public_id, 'name': user.name}
                result.append(user_data)
            if result:
                return jsonify({'users': result})
        else:
            return jsonify({'message': 'No users found'})
    else:
        return jsonify({"message": "You have no Admin Privileges"})


@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        data = request.get_json()
        if data['name'] and data['password']:
            user = User(public_id=str(uuid.uuid4()),
                        name=data['name'], password=generate_password_hash(data['password'], method='sha256'), admin=data['isAdmin'])
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'User created successfully'})


@app.route('/user/<id>', methods=['GET'])
@token_required
def get_user(current_user, id):
    if current_user.public_id == id:
        user = User.query.filter_by(public_id=id).first()
        user_data = {'name': user.name,
                     'password': user.password, 'isAdmin': user.admin}
        return jsonify(user_data)
    return({"message": "You can not View Others Profile"})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if data['name'] and data['password']:
            user = User.query.filter_by(name=data['name']).first()
            if user and check_password_hash(user.password, data['password']):
                token = jwt.encode(
                    {'public_id': user.public_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # set limit for user
                     }, app.config['SECRET_KEY'], algorithm='HS256')
                return jsonify({'message': 'User logged in successfully', 'Token': token})
            else:
                return jsonify({'message': 'Invalid credentials'})
    if request.method == 'GET':
        return make_response(405)

# GET: get all tasks, POST: create new task


@app.route('/tasks', methods=['GET', 'POST'])
@token_required
def get_all_tasks(current_user):

    if request.method == 'GET':
        tasks = Task.query.filter_by(user_id=current_user.public_id)
        result = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'created_at': task.created_at,
                'updated_at': task.updated_at,
            }
            result.append(task_data)
        return jsonify(result)

    if request.method == 'POST':
        data = request.get_json()
        title = data['title']
        description = data['description']
        save_data(title, description, current_user.public_id)
        return jsonify({"message": "Task added successfully"})

    if request.method == 'PUT':
        data = request.get_json()
        title = data['title']
        description = data['description']
        save_data(title, description, current_user.public_id)
        return jsonify({"message": "Task Updated successfully"})


@app.route('/task/<pk>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def get_task(current_user, pk):
    user_id = current_user.public_id
    tasks = Task.query.filter_by(id=pk).first()
    if request.method == 'GET':
        if not tasks:
            return jsonify({"message": "Task not found"})
        if tasks.user_id == user_id:
            task_data = {
                'id': tasks.id,
                'title': tasks.title,
                'description': tasks.description,
                'status': tasks.status,
            }
            return jsonify(task_data)
        return jsonify({"message": "You do not have access"})

    if request.method == 'PUT':
        if tasks.user_id == user_id:
            data = request.get_json()
            title = data['title']
            description = data['description']
            update_data(pk, title, description)
            return jsonify({"message": "Task updated successfully"})
        return jsonify({"message": "You do not have access"})

    if request.method == 'DELETE':
        if tasks.user_id == user_id:
            if not tasks:
                return jsonify({"message": "Task not found"})

            delete_data(pk)
            return jsonify({"message": "Task Deleted successfully"})
        return jsonify({"message": "You do not have access"})


@app.route('/task/update/<id>', methods=['PUT'])
@token_required
def update_task(current_user, id):
    user_id = current_user.public_id
    tasks = Task.query.filter_by(id=id).first()
    if tasks.user_id == user_id:
        if not tasks:
            return jsonify({"message": "Task not found"})
        update_status(id)
        return jsonify({"message": "Task Completed successfully"})
    return jsonify({"message": "You do not have access"})
