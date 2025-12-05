from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):

    title: str = Field(..., min_length=1, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")


class TaskUpdate(BaseModel):

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):

    id: int
    title: str
    description: str
    completed: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True