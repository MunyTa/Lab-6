from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

users_db = []
next_id = 1


@app.route('/', methods=['GET'])
def index():

    return render_template('index.html', users=users_db)


@app.route('/api/users', methods=['GET'])
def get_users():

    return jsonify(users_db)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    user = next((u for u in users_db if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404


@app.route('/api/users', methods=['POST'])
def create_user():

    global next_id

    if not request.json or not 'name' in request.json:
        return jsonify({'error': 'Missing required fields'}), 400

    user = {
        'id': next_id,
        'name': request.json['name'],
        'email': request.json.get('email', ''),
        'date': request.json.get('date', '')
    }

    users_db.append(user)
    next_id += 1

    return jsonify(user), 201


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users_db if u['id'] == user_id), None)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not request.json:
        return jsonify({'error': 'No data provided'}), 400

    user['name'] = request.json.get('name', user['name'])
    user['email'] = request.json.get('email', user['email'])
    user['date'] = request.json.get('date', user['date'])

    return jsonify(user)


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    global users_db

    user = next((u for u in users_db if u['id'] == user_id), None)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    users_db = [u for u in users_db if u['id'] != user_id]

    return jsonify({'result': 'User deleted'}), 200


@app.route('/add', methods=['GET', 'POST'])
def add_user_form():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')

        if name:
            global next_id
            user = {
                'id': next_id,
                'name': name,
                'email': email,
                'date': date
            }
            users_db.append(user)
            next_id += 1

        return redirect(url_for('index'))

    return render_template('add_user.html')


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_form(user_id):

    user = next((u for u in users_db if u['id'] == user_id), None)

    if not user:
        return redirect(url_for('index'))

    if request.method == 'POST':

        user['name'] = request.form.get('name', user['name'])
        user['email'] = request.form.get('email', user['email'])
        user['date'] = request.form.get('date', user['date'])

        return redirect(url_for('index'))

    return render_template('edit_user.html', user=user)


if __name__ == '__main__':
    app.run(debug=True, port=5000)