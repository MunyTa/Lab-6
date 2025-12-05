from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from typing import List, Optional

try:
    from schemas import TaskCreate, TaskUpdate, TaskResponse
except ImportError:
    from pydantic import BaseModel, Field
    from typing import Optional as Opt


    class TaskCreate(BaseModel):
        title: str = Field(..., min_length=1, max_length=100)
        description: Opt[str] = Field(None, max_length=500)


    class TaskUpdate(BaseModel):
        title: Opt[str] = Field(None, min_length=1, max_length=100)
        description: Opt[str] = Field(None, max_length=500)
        completed: Opt[bool] = None


    class TaskResponse(BaseModel):
        id: int
        title: str
        description: str
        completed: bool

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})

class Task:
    def __init__(self, id: int, title: str, description: str = "", completed: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

tasks_db: List[Task] = []
current_id = 1

initial_tasks = [
    Task(1, 'Изучить Python', 'Пройти курс по Python', True),
    Task(2, 'Создать REST API', 'Написать простое API на Flask', False)
]

tasks_db.extend(initial_tasks)
current_id = 3

def find_task(task_id: int) -> Optional[Task]:
    for task in tasks_db:
        if task.id == task_id:
            return task
    return None


def find_task_index(task_id: int) -> int:
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            return i
    return -1

def validate_pydantic_error(error):
    errors = []
    for err in error.errors():
        errors.append({
            'field': '.'.join(str(loc) for loc in err['loc']),
            'message': err['msg'],
            'type': err['type']
        })
    return errors

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks_list = [task.to_dict() for task in tasks_db]
        return jsonify(tasks_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    global current_id

    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    try:
        task_data = TaskCreate(**request.json)
    except Exception as e:
        return jsonify({
            'error': 'Validation error',
            'details': validate_pydantic_error(e)
        }), 400

    new_task = Task(
        id=current_id,
        title=task_data.title,
        description=task_data.description or "",
        completed=False
    )

    tasks_db.append(new_task)
    current_id += 1

    return jsonify(new_task.to_dict()), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    try:
        update_data = TaskUpdate(**request.json)
    except Exception as e:
        return jsonify({
            'error': 'Validation error',
            'details': validate_pydantic_error(e)
        }), 400

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        if hasattr(task, key):
            setattr(task, key, value)

    return jsonify(task.to_dict())

@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def patch_task(task_id):
    task = find_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    try:
        update_data = TaskUpdate(**request.json)
    except Exception as e:
        return jsonify({
            'error': 'Validation error',
            'details': validate_pydantic_error(e)
        }), 400

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        if hasattr(task, key):
            setattr(task, key, value)

    return jsonify(task.to_dict())

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    index = find_task_index(task_id)
    if index == -1:
        return jsonify({'error': 'Task not found'}), 404

    deleted_task = tasks_db.pop(index)
    return jsonify({
        'result': 'Task deleted',
        'task': deleted_task.to_dict()
    })

@app.route('/tasks', methods=['DELETE'])
def delete_all_tasks():
    deleted_tasks = [task.to_dict() for task in tasks_db]
    tasks_db.clear()
    return jsonify({
        'result': 'All tasks deleted',
        'deleted_tasks': deleted_tasks,
        'count': len(deleted_tasks)
    })

@app.route('/stats', methods=['GET'])
def get_stats():

    try:
        total = len(tasks_db)
        completed = sum(1 for task in tasks_db if task.completed)
        active = total - completed

        return jsonify({
            'total': total,
            'completed': completed,
            'active': active,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=4000)