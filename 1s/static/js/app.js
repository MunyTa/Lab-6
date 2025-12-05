const API_BASE = window.location.origin;

const elements = {
    taskTitle: document.getElementById('taskTitle'),
    taskDescription: document.getElementById('taskDescription'),
    searchInput: document.getElementById('search-input'),
    titleChars: document.getElementById('title-chars'),
    descChars: document.getElementById('desc-chars'),
    titleError: document.getElementById('title-error'),
    descError: document.getElementById('desc-error'),
    tasksContainer: document.getElementById('tasks-container'),
    totalTasks: document.getElementById('total-tasks'),
    activeTasks: document.getElementById('active-tasks'),
    completedTasks: document.getElementById('completed-tasks'),
    completionRate: document.getElementById('completion-rate'),
    dbInfo: document.getElementById('db-info')
};

let currentTasks = [];
let isSearching = false;


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

async function loadTasks() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/tasks`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        currentTasks = await response.json();
        displayTasks(currentTasks);
        await loadStats();

    } catch (error) {
        console.error('Ошибка загрузки задач:', error);
        showError(`Ошибка загрузки задач: ${error.message}`);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        if (!response.ok) throw new Error('Ошибка загрузки статистики');

        const stats = await response.json();

        elements.totalTasks.textContent = stats.total || 0;
        elements.activeTasks.textContent = stats.active || 0;
        elements.completedTasks.textContent = stats.completed || 0;
        elements.completionRate.textContent =
            stats.completion_rate ? `${Math.round(stats.completion_rate)}%` : '0%';

    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}


function displayTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        elements.tasksContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h3>Нет задач</h3>
                <p>Добавьте свою первую задачу!</p>
            </div>`;
        return;
    }

    const sortedTasks = [...tasks].sort((a, b) => {
        if (a.completed === b.completed) {
            return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        }
        return a.completed ? 1 : -1;
    });

    let html = '';
    sortedTasks.forEach(task => {
        const createdDate = task.created_at ?
            new Date(task.created_at).toLocaleDateString('ru-RU') : '';

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

            <div class="task-meta">
                <span><i class="far fa-calendar"></i> ${createdDate}</span>
                <span><i class="far fa-clock"></i> ${task.completed ? 'Выполнена' : 'В процессе'}</span>
            </div>

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
    hideErrors();

    const title = elements.taskTitle.value.trim();
    const description = elements.taskDescription.value.trim();

    if (!title) {
        showError('title-error', 'Название задачи обязательно');
        return;
    }

    if (title.length > 100) {
        showError('title-error', 'Максимальная длина названия - 100 символов');
        return;
    }

    if (description.length > 500) {
        showError('desc-error', 'Максимальная длина описания - 500 символов');
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
                        showError('title-error', error.message);
                    } else if (error.field === 'description') {
                        showError('desc-error', error.message);
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
        console.error('Ошибка создания задачи:', error);
        alert('Ошибка сети: ' + error.message);
    }
}

async function toggleTask(id) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${id}/toggle`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Ошибка при обновлении задачи');
        }

        await loadTasks();

    } catch (error) {
        console.error('Ошибка переключения задачи:', error);
        alert('Ошибка: ' + error.message);
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
        console.error('Ошибка редактирования задачи:', error);
        alert('Ошибка: ' + error.message);
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
        console.error('Ошибка удаления задачи:', error);
        alert('Ошибка: ' + error.message);
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
        console.error('Ошибка удаления всех задач:', error);
        alert('Ошибка: ' + error.message);
    }
}

async function searchTasks() {
    const keyword = elements.searchInput.value.trim();

    if (!keyword) {
        await loadTasks();
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/tasks/search?q=${encodeURIComponent(keyword)}`);

        if (!response.ok) throw new Error('Ошибка поиска');

        const tasks = await response.json();
        displayTasks(tasks);
        isSearching = true;

    } catch (error) {
        console.error('Ошибка поиска:', error);
        showError(`Ошибка поиска: ${error.message}`);
    }
}

function clearSearch() {
    elements.searchInput.value = '';
    isSearching = false;
    loadTasks();
}

function showLoading() {
    elements.tasksContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i><br>
            Загрузка...
        </div>`;
}

function showError(message) {
    elements.tasksContainer.innerHTML = `
        <div class="error">
            <i class="fas fa-exclamation-triangle"></i><br>
            ${message}
        </div>`;
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}

function hideErrors() {
    elements.titleError.style.display = 'none';
    elements.descError.style.display = 'none';
}

window.addTask = addTask;
window.toggleTask = toggleTask;
window.editTask = editTask;
window.deleteTask = deleteTask;
window.clearAllTasks = clearAllTasks;
window.searchTasks = searchTasks;
window.clearSearch = clearSearch;

document.addEventListener('DOMContentLoaded', init);