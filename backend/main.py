from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from backend.auth import create_access_token, get_current_user, User, fake_users_db

app = FastAPI()

# In-memory task storage
tasks: List["Task"] = []
task_id_counter = 1


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


class CreateTaskRequest(BaseModel):
    title: str


@app.get("/api/health")
def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: A simple status message indicating the service is healthy.
    """
    return {"status": "healthy"}


@app.post("/api/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return a JWT access token.

    This endpoint validates user credentials using OAuth2 password flow.
    On successful authentication, returns a bearer token for subsequent API calls.

    Args:
        form_data (OAuth2PasswordRequestForm): Contains username and password fields.

    Returns:
        dict: Contains access_token (JWT string) and token_type ("bearer").

    Raises:
        HTTPException: 400 error if username or password is incorrect.
    """
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/tasks")
def get_tasks(current_user: User = Depends(get_current_user)):
    """
    Retrieve all tasks for the authenticated user.

    Returns the complete list of tasks stored in memory.
    Requires a valid JWT bearer token in the Authorization header.

    Args:
        current_user (User): Automatically injected authenticated user from JWT token.

    Returns:
        List[Task]: Array of all task objects with id, title, and completed status.
    """
    return tasks


@app.post("/api/tasks")
def create_task(task_data: CreateTaskRequest, current_user: User = Depends(get_current_user)):
    """
    Create a new task for the authenticated user.

    Generates a new task with auto-incremented ID, the provided title,
    and completed status set to false. Requires authentication.

    Args:
        task_data (CreateTaskRequest): Contains the title for the new task.
        current_user (User): Automatically injected authenticated user from JWT token.

    Returns:
        Task: The newly created task object with assigned ID.
    """
    global task_id_counter
    new_task = Task(id=task_id_counter, title=task_data.title, completed=False)
    tasks.append(new_task)
    task_id_counter += 1
    return new_task


@app.put("/api/tasks/{task_id}/complete")
def complete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Mark a specific task as completed.

    Finds the task by its ID and sets its completed status to true.
    Requires authentication.

    Args:
        task_id (int): The unique identifier of the task to mark as complete.
        current_user (User): Automatically injected authenticated user from JWT token.

    Returns:
        Task: The updated task object with completed=True.

    Raises:
        HTTPException: 404 error if no task exists with the given ID.
    """
    for task in tasks:
        if task.id == task_id:
            task.completed = True
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user)):
    """
    Delete a specific task by its ID.

    Permanently removes the task from the in-memory task list.
    Requires authentication.

    Args:
        task_id (int): The unique identifier of the task to delete.
        current_user (User): Automatically injected authenticated user from JWT token.

    Returns:
        dict: Success message confirming the task was deleted.

    Raises:
        HTTPException: 404 error if no task exists with the given ID.
    """
    global tasks
    for i, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[i]
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")
