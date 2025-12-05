from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn

app = FastAPI(
    title="Simple FastAPI App",
    description="Простое приложение, которое принимает параметр и отвечает",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": None, "input_value": None}
    )

@app.get("/greet", response_class=HTMLResponse)
async def greet_get(request: Request, name: Optional[str] = None):

    if name:
        message = f"👋 Привет, {name}! Рад видеть тебя!"
    else:
        message = "👋 Привет! Как тебя зовут?"

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": message, "input_value": name or ""}
    )

@app.post("/greet", response_class=HTMLResponse)
async def greet_post(request: Request, name: str = Form(...)):

    message = f"🎉 Приветствуем, {name}! Добро пожаловать!"

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "message": message, "input_value": name}
    )

@app.get("/api/greet")
async def api_greet(name: Optional[str] = "Гость"):

    return {
        "message": f"Привет, {name}!",
        "timestamp": "2024-01-15T12:00:00",
        "status": "success"
    }

@app.get("/api/calculate")
async def calculate(a: int, b: int, operation: str = "add"):

    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Ошибка: деление на ноль"
    }

    if operation not in operations:
        return {"error": "Неизвестная операция", "available_operations": list(operations.keys())}

    try:
        result = operations[operation](a, b)
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
            "expression": f"{a} {operation} {b} = {result}"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True
    )