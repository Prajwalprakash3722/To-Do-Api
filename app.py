from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisshouldbechangedaftercloningfromgit'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(120))
    status = db.Column(db.String(120), nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.now(), onupdate=db.func.now())


def save_data(title, description):
    task = Task(title=title, description=description)
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


# GET: get all tasks, POST: create new task
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        tasks = Task.query.all()
        result = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'created_at': task.created_at,
                'updated_at': task.updated_at
            }
            result.append(task_data)
        return jsonify(result)

    if request.method == 'POST':
        data = request.get_json()
        title = data['title']
        description = data['description']
        save_data(title, description)
        return jsonify({"message": "Task added successfully"})

    if request.method == 'PUT':
        data = request.get_json()
        title = data['title']
        description = data['description']
        save_data(title, description)
        return jsonify({"message": "Task added successfully"})


@app.route('/task/<pk>', methods=['GET', 'PUT', 'DELETE'])
def task(pk):
    tasks = Task.query.filter_by(id=pk).first()
    if request.method == 'GET':
        if not tasks:
            return jsonify({"message": "Task not found"})

        task_data = {
            'id': tasks.id,
            'title': tasks.title,
            'description': tasks.description,
            'status': tasks.status,
        }
        return jsonify(task_data)
    if request.method == 'PUT':
        data = request.get_json()
        title = data['title']
        description = data['description']
        update_data(pk, title, description)
        return jsonify({"message": "Task updated successfully"})

    if request.method == 'DELETE':
        if not tasks:
            return jsonify({"message": "Task not found"})

        delete_data(pk)
        return jsonify({"message": "Task Deleted successfully"})


@app.route('/task/update/<id>', methods=['PUT'])
def update_task(id):
    tasks = Task.query.filter_by(id=id).first()
    if not tasks:
        return jsonify({"message": "Task not found"})
    update_status(id)
    return jsonify({"message": "Task Completed successfully"})
