from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.todos import router as todos_router
from app.api.v1.daily_content import router as daily_content_router
from app.api.v1.projects import router as projects_router
from app.api.v1.student_notes import router as student_notes_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["User Management"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles & Permissions"])
api_router.include_router(todos_router, prefix="/todos", tags=["Todos"])
api_router.include_router(daily_content_router, prefix="/daily-content", tags=["Daily Content"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(student_notes_router, prefix="/students/{student_id}/notes", tags=["Student Notes"])
