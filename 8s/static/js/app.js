const API_BASE = window.location.origin;
const elements = {
    taskTitle: document.getElementById('taskTitle'),
    taskDescription: document.getElementById('taskDescription'),
    titleChars: document.getElementById('title-chars'),
    descChars: document.getElementById('desc-chars'),
    titleError: document.getElementById('title-error'),
    descError: document.getElementById('desc-error'),
    tasksContainer: document.getElementById('tasks-container'),
    totalTasks: document.getElementById('total-tasks'),
    activeTasks: document.getElementById('active-tasks'),
    completedTasks: document.getElementById('completed-tasks'),
    completionRate: document.getElementById('completion-rate')
};

function init() {
    setupEventListeners();
    loadTasks();
}

function setupEventListeners() {
    if (elements.taskTitle) {
        elements.taskTitle.addEventListener('input', function() {
            elements.titleChars.textContent = this.value.length;
        });
    }

    if (elements.taskDescription) {
        elements.taskDescription.addEventListener('input', function() {
            elements.descChars.textContent = this.value.length;
        });
    }

    if (elements.taskTitle) {
        elements.taskTitle.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addTask();
            }
        });
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        if (!response.ok) throw new Error('Ошибка загрузки статистики');

        const stats = await response.json();

        elements.totalTasks.textContent = stats.total;
        elements.activeTasks.textContent = stats.active;
        elements.completedTasks.textContent = stats.completed;
        elements.completionRate.textContent =
            stats.total > 0 ? `${Math.round(stats.completion_rate)}%` : '0%';
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        if (!response.ok) throw new Error('Ошибка сервера');

        const tasks = await response.json();
        displayTasks(tasks);
        await loadStats();

    } catch (error) {
        elements.tasksContainer.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i><br>
                Ошибка загрузки задач: ${error.message}
            </div>`;
        console.error('Ошибка:', error);
    }
}

function displayTasks(tasks) {
    if (tasks.length === 0) {
        elements.tasksContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h3>Нет задач</h3>
                <p>Добавьте свою первую задачу!</p>
            </div>`;
        return;
    }

    tasks.sort((a, b) => {
        if (a.completed === b.completed) return b.id - a.id;
        return a.completed ? 1 : -1;
    });

    let html = '';
    tasks.forEach(task => {
        html += `
        <div class="task ${task.completed ? 'completed' : ''}" id="task-${task.id}">
            <div class="task-header">
                <div class="task-title" title="${task.title}">${task.title}</div>
                <div class="task-id">#${task.id}</div>
            </div>

            ${task.description ? `
            <div class="task-description" title="${task.description}">
                <i class="fas fa-align-left"></i> ${task.description}
            </div>` : ''}

            <div class="task-actions">
                <button class="btn btn-small ${task.completed ? 'btn-secondary' : 'btn-primary'}"
                        onclick="toggleTask(${task.id})">
                    <i class="fas ${task.completed ? 'fa-undo' : 'fa-check'}"></i>
                    ${task.completed ? 'Восстановить' : 'Выполнить'}
                </button>

                <button class="btn btn-small btn-secondary" onclick="editTask(${task.id})">
                    <i class="fas fa-edit"></i> Редактировать
                </button>

                <button class="btn btn-small btn-danger" onclick="deleteTask(${task.id})">
                    <i class="fas fa-trash"></i> Удалить
                </button>
            </div>
        </div>`;
    });

    elements.tasksContainer.innerHTML = html;
}

async function addTask() {
    elements.titleError.style.display = 'none';
    elements.descError.style.display = 'none';

    const title = elements.taskTitle.value.trim();
    const description = elements.taskDescription.value.trim();

    if (!title) {
        elements.titleError.textContent = 'Название задачи обязательно';
        elements.titleError.style.display = 'block';
        return;
    }

    if (title.length > 100) {
        elements.titleError.textContent = 'Максимальная длина названия - 100 символов';
        elements.titleError.style.display = 'block';
        return;
    }

    if (description.length > 500) {
        elements.descError.textContent = 'Максимальная длина описания - 500 символов';
        elements.descError.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description || undefined
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (data.details && Array.isArray(data.details)) {
                data.details.forEach(error => {
                    if (error.field === 'title') {
                        elements.titleError.textContent = error.message;
                        elements.titleError.style.display = 'block';
                    } else if (error.field === 'description') {
                        elements.descError.textContent = error.message;
                        elements.descError.style.display = 'block';
                    }
                });
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
            return;
        }

        elements.taskTitle.value = '';
        elements.taskDescription.value = '';
        elements.titleChars.textContent = '0';
        elements.descChars.textContent = '0';

        await loadTasks();

    } catch (error) {
        alert('Ошибка сети: ' + error.message);
        console.error('Ошибка:', error);
    }
}

async function toggleTask(id) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${id}`);
        if (!response.ok) throw new Error('Задача не найдена');

        const task = await response.json();

        await fetch(`${API_BASE}/tasks/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                completed: !task.completed
            })
        });

        await loadTasks();
    } catch (error) {
        alert('Ошибка: ' + error.message);
        console.error('Ошибка:', error);
    }
}

async function editTask(id) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${id}`);
        if (!response.ok) throw new Error('Задача не найдена');

        const task = await response.json();

        const newTitle = prompt('Новое название задачи:', task.title);
        if (newTitle === null) return;

        const newDescription = prompt('Новое описание задачи:', task.description || '');
        if (newDescription === null) return;

        await fetch(`${API_BASE}/tasks/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: newTitle,
                description: newDescription || undefined,
                completed: task.completed
            })
        });

        await loadTasks();
    } catch (error) {
        alert('Ошибка: ' + error.message);
        console.error('Ошибка:', error);
    }
}

async function deleteTask(id) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Ошибка при удалении');

        await loadTasks();
    } catch (error) {
        alert('Ошибка: ' + error.message);
        console.error('Ошибка:', error);
    }
}

async function clearAllTasks() {
    if (!confirm('Вы уверены, что хотите удалить ВСЕ задачи?\nЭто действие нельзя отменить.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Ошибка при удалении');

        await loadTasks();
    } catch (error) {
        alert('Ошибка: ' + error.message);
        console.error('Ошибка:', error);
    }
}

document.addEventListener('DOMContentLoaded', init);

window.addTask = addTask;
window.toggleTask = toggleTask;
window.editTask = editTask;
window.deleteTask = deleteTask;
window.clearAllTasks = clearAllTasks;