const API_BASE = window.location.origin;

function sendGetRequest() {
    const nameInput = document.getElementById('name');
    const name = nameInput.value.trim();

    if (!name) {
        alert('Пожалуйста, введите имя');
        nameInput.focus();
        return;
    }

    window.location.href = `/greet?name=${encodeURIComponent(name)}`;
}

async function testAPI() {
    try {
        const response = await fetch(`${API_BASE}/api/greet?name=ТестовыйПользователь`);
        const data = await response.json();

        alert(`API тест:\n${data.message}\n\nСтатус: ${data.status}`);
        console.log('API Response:', data);

    } catch (error) {
        console.error('API Error:', error);
        alert('Ошибка при тестировании API');
    }
}

async function calculate() {
    const num1 = document.getElementById('num1').value;
    const num2 = document.getElementById('num2').value;
    const operation = document.getElementById('operation').value;

    if (!num1 || !num2) {
        showResult('calc-result', '⚠️ Пожалуйста, введите оба числа', 'warning');
        return;
    }

    try {
        const url = `${API_BASE}/api/calculate?a=${num1}&b=${num2}&operation=${operation}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            showResult('calc-result', `❌ Ошибка: ${data.error}`, 'error');
        } else {
            const result = `✅ ${data.expression}`;
            showResult('calc-result', result, 'success');
        }

    } catch (error) {
        showResult('calc-result', `❌ Ошибка сети: ${error.message}`, 'error');
        console.error('Calculate error:', error);
    }
}

async function getUser() {
    const userId = document.getElementById('user-id').value;
    const showDetails = document.getElementById('user-details').checked;

    if (!userId || userId < 1 || userId > 3) {
        showResult('user-result', '⚠️ Введите ID от 1 до 3', 'warning');
        return;
    }

    try {
        const url = `${API_BASE}/api/user/${userId}${showDetails ? '?details=true' : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            showResult('user-result', `❌ ${data.error}`, 'error');
        } else {
            const formatted = JSON.stringify(data, null, 2);
            showResult('user-result', formatted, 'success');
        }

    } catch (error) {
        showResult('user-result', `❌ Ошибка: ${error.message}`, 'error');
        console.error('Get user error:', error);
    }
}

async function quickGreet() {
    const name = document.getElementById('quick-name').value.trim();

    if (!name) {
        showResult('quick-result', '⚠️ Введите имя', 'warning');
        return;
    }

    try {
        const url = `${API_BASE}/api/greet?name=${encodeURIComponent(name)}`;
        const response = await fetch(url);
        const data = await response.json();

        showResult('quick-result', `💬 ${data.message}\n\n📅 ${data.timestamp}\n✅ ${data.status}`, 'success');

    } catch (error) {
        showResult('quick-result', `❌ Ошибка: ${error.message}`, 'error');
        console.error('Quick greet error:', error);
    }
}

function showResult(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);

    element.className = 'result';

    if (type === 'error') {
        element.classList.add('error');
        element.style.borderColor = '#f44336';
        element.style.backgroundColor = '#ffebee';
    } else if (type === 'success') {
        element.classList.add('success');
        element.style.borderColor = '#4caf50';
        element.style.backgroundColor = '#e8f5e9';
    } else if (type === 'warning') {
        element.classList.add('warning');
        element.style.borderColor = '#ff9800';
        element.style.backgroundColor = '#fff3e0';
    }

    element.textContent = message;
    element.style.display = 'block';
}

function populateExamples() {
    const now = new Date();
    const timestamp = now.toISOString().split('T')[0];

    const examples = ['Алексей', 'Мария', 'Дмитрий', 'Екатерина', 'Сергей'];

    if (!document.getElementById('example-buttons')) {
        const container = document.querySelector('.form-group');
        const exampleDiv = document.createElement('div');
        exampleDiv.id = 'example-buttons';
        exampleDiv.style.marginTop = '10px';
        exampleDiv.innerHTML = `
            <small style="display: block; margin-bottom: 5px; color: #666;">
                <i class="fas fa-lightbulb"></i> Быстрые примеры:
            </small>
            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                ${examples.map(name =>
                    `<button type="button" class="btn-example" onclick="document.getElementById('name').value = '${name}'">
                        ${name}
                    </button>`
                ).join('')}
            </div>
        `;
        container.appendChild(exampleDiv);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('FastAPI Demo загружен!');

    populateExamples();

    const nameInput = document.getElementById('name');
    if (nameInput && !nameInput.value) {
        nameInput.focus();
    }

    const style = document.createElement('style');
    style.textContent = `
        .btn-example {
            padding: 5px 10px;
            background: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-example:hover {
            background: #d0d0d0;
            transform: translateY(-1px);
        }
        .result.error { color: #d32f2f; }
        .result.success { color: #388e3c; }
        .result.warning { color: #f57c00; }
    `;
    document.head.appendChild(style);
});

window.sendGetRequest = sendGetRequest;
window.testAPI = testAPI;
window.calculate = calculate;
window.getUser = getUser;
window.quickGreet = quickGreet;