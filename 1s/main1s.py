from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import TaskCreate, TaskUpdate, TaskResponse
from database import db
import traceback

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})

def validate_pydantic_error(error):

    errors = []
    for err in error.errors():
        errors.append({
            'field': '.'.join(str(loc) for loc in err['loc']),
            'message': err['msg'],
            'type': err['type']
        })
    return errors


def task_to_response(task_dict):
    if not task_dict:
        return None
    try:
        return TaskResponse(**task_dict)
    except Exception:
        return task_dict

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():

    try:
        tasks = db.get_all_tasks()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):

    try:
        task = db.get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Задача не найдена'}), 404
        return jsonify(task)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 415

        task_data = TaskCreate(**request.json)

        new_task = db.create_task(
            title=task_data.title,
            description=task_data.description or ""
        )

        if not new_task:
            return jsonify({'error': 'Ошибка создания задачи'}), 500

        return jsonify(new_task), 201

    except Exception as e:
        if hasattr(e, 'errors'):
            return jsonify({
                'error': 'Ошибка валидации',
                'details': validate_pydantic_error(e)
            }), 400
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):

    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 415

        update_data = TaskUpdate(**request.json)

        update_dict = update_data.model_dump(exclude_unset=True)

        updated_task = db.update_task(task_id, **update_dict)

        if not updated_task:
            return jsonify({'error': 'Задача не найдена'}), 404

        return jsonify(updated_task)

    except Exception as e:
        if hasattr(e, 'errors'):
            return jsonify({
                'error': 'Ошибка валидации',
                'details': validate_pydantic_error(e)
            }), 400
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def patch_task(task_id):

    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 415

        update_data = TaskUpdate(**request.json)
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            return jsonify({'error': 'Нет полей для обновления'}), 400

        updated_task = db.update_task(task_id, **update_dict)

        if not updated_task:
            return jsonify({'error': 'Задача не найдена'}), 404

        return jsonify(updated_task)

    except Exception as e:
        if hasattr(e, 'errors'):
            return jsonify({
                'error': 'Ошибка валидации',
                'details': validate_pydantic_error(e)
            }), 400
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task_completion(task_id):

    try:
        toggled_task = db.toggle_task_completion(task_id)

        if not toggled_task:
            return jsonify({'error': 'Задача не найдена'}), 404

        return jsonify(toggled_task)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):

    try:

        task = db.get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Задача не найдена'}), 404

        deleted = db.delete_task(task_id)
        if not deleted:
            return jsonify({'error': 'Ошибка удаления'}), 500

        return jsonify({
            'result': 'Задача удалена',
            'task': task
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tasks', methods=['DELETE'])
def delete_all_tasks():

    try:
        deleted_count = db.delete_all_tasks()

        return jsonify({
            'result': 'Все задачи удалены',
            'count': deleted_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():

    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tasks/search', methods=['GET'])
def search_tasks():

    try:
        keyword = request.args.get('q', '')
        if not keyword:
            return jsonify({'error': 'Необходим поисковый запрос'}), 400

        tasks = db.search_tasks(keyword)
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():

    try:

        db.get_connection().execute("SELECT 1")
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': traceback.format_exc()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Эндпоинт не найден'}), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Ошибка сервера: {e}\n{traceback.format_exc()}")
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Запуск Todo List приложения с SQLite")
    print("📁 База данных: todo.db")
    print("🌐 API: http://localhost:2000/")
    print("🖥️  Интерфейс: http://localhost:2000/")
    print("=" * 50)

    app.run(debug=True, port=2000)