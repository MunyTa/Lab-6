from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

tasks = [
    {"id": 1, "title": "Изучить Python", "completed": True},
    {"id": 2, "title": "Изучить FastAPI", "completed": False},
    {"id": 3, "title": "Создать Todo List", "completed": False}
]
next_id = 4

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/tasks")
async def get_tasks():
    return tasks

@app.post("/api/tasks")
async def create_task(request: Request):
    global next_id
    data = await request.json()

    if not data.get("title"):
        return {"error": "Название обязательно"}

    task = {
        "id": next_id,
        "title": data["title"],
        "completed": False
    }

    tasks.append(task)
    next_id += 1
    return task

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    data = await request.json()

    for task in tasks:
        if task["id"] == task_id:
            if "title" in data:
                task["title"] = data["title"]
            if "completed" in data:
                task["completed"] = data["completed"]
            return task

    return {"error": "Задача не найдена"}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)