import traceback, logging
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import auth, users, todos, projects, student_notes, activity_logs, notifications, dashboard, daily_content, reports, attendance, students, roles, permissions, referral_links
from app.core.response import SuccessResponse
from app.api.deps import get_db
from app.database.init_db import init_db

logging.basicConfig(level=logging.ERROR)

app = FastAPI(title="Student Management System API", version="0.1.0")


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logging.error(f"Unhandled exception: {tb}")
    try:
        path = r"C:\Users\Admin\Desktop\Student_Management_System_Magizh\backend\error_traceback.log"
        with open(path, "a") as f:
            f.write(f"\n--- {request.method} {request.url.path} ---\n{tb}\n")
    except Exception as log_err:
        try:
            with open(r"C:\Users\Admin\Desktop\Student_Management_System_Magizh\backend\error_traceback.log", "a") as f:
                f.write(f"\nLogger error: {log_err}\n")
        except:
            pass
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": tb})


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    try:
        init_db(db)
    finally:
        db.close()

# CORS (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(student_notes.router, prefix="/api/v1/students/{student_id}/notes", tags=["student_notes"])
app.include_router(activity_logs.router, prefix="/api/v1/activity-logs", tags=["activity_logs"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(daily_content.router, prefix="/api/v1/daily-content", tags=["daily_content"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(dashboard.analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["permissions"])
app.include_router(referral_links.router, prefix="/api/v1/referral-links", tags=["referral_links"])

@app.get("/health", response_model=SuccessResponse)
def health_check():
    return SuccessResponse(message="ok")
