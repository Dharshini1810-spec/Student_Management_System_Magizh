from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, todos, projects, student_notes, activity_logs, notifications, dashboard
from app.core.response import SuccessResponse

app = FastAPI(title="Student Management System API", version="0.1.0")

# CORS (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(student_notes.router, prefix="/api/v1/students/{student_id}/notes", tags=["student_notes"])
app.include_router(activity_logs.router, prefix="/api/v1/activity-logs", tags=["activity_logs"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(dashboard.analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/health", response_model=SuccessResponse)
def health_check():
    return SuccessResponse(message="ok")
