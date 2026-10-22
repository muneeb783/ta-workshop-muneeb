document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        taskList.appendChild(renderTask(task));
    });
}

function renderTask(task) {
    const li = document.createElement('li');
    const checkbox = document.createElement('input');
    const title = document.createElement('span');
    const deleteButton = document.createElement('button');

    checkbox.type = 'checkbox';
    checkbox.className = 'task-checkbox';
    checkbox.dataset.taskId = task.id;
    checkbox.checked = task.completed === true;
    checkbox.addEventListener('change', () => toggleTask(task, checkbox,
        title, li));

    title.className = 'task-title';
    title.textContent = task.title;

    deleteButton.className = 'delete-btn';
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', () => deleteTask(task.id));

    li.appendChild(checkbox);
    li.appendChild(title);
    li.appendChild(deleteButton);
    applyCompletedState(li, title, checkbox.checked);

    return li;
}

function applyCompletedState(listItem, title, completed) {
    listItem.classList.toggle('completed', completed);
    title.classList.toggle('completed', completed);
}

async function toggleTask(task, checkbox, title, listItem) {
    const previousValue = task.completed === true;
    const completed = checkbox.checked;

    try {
        const response = await fetch(`/api/tasks/${task.id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed })
        });

        if (!response.ok) {
            throw new Error('Unable to update task');
        }

        const updatedTask = await response.json();
        task.completed = updatedTask.completed;
        checkbox.checked = updatedTask.completed === true;
        applyCompletedState(listItem, title, checkbox.checked);
    } catch (error) {
        checkbox.checked = previousValue;
        applyCompletedState(listItem, title, previousValue);
    }
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const title = titleInput.value.trim();

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });

    titleInput.value = '';
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
