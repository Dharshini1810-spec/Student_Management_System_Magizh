from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.todos import router as todos_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["User Management"])
api_router.include_router(roles_router, tags=["Roles & Permissions"])
api_router.include_router(todos_router, prefix="/todos", tags=["Todos"])
