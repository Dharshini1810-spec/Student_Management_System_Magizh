from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
<<<<<<< HEAD
from app.api.v1.permissions import router as permissions_router
from app.api.v1.students import router as students_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.attendance import router as attendance_router
=======
>>>>>>> fcf518897bf1e7d68bc46b20f3d81c9d5f561424

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
<<<<<<< HEAD
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(students_router, prefix="/students", tags=["Students"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])

=======
api_router.include_router(users_router, prefix="/users", tags=["User Management"])
api_router.include_router(roles_router, tags=["Roles & Permissions"])
>>>>>>> fcf518897bf1e7d68bc46b20f3d81c9d5f561424
